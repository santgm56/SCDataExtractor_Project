#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: routes.py
Descripción:
    Define las rutas de la API para la aplicación web.
    Estas rutas permiten consultar y visualizar los datos extraídos 
    por el scraper.
    
    Funcionalidades:
    - Rutas para obtener datos por tipo (genérico, e-commerce)
    - Rutas para gestionar sesiones de scraping
    - Paginación y filtrado de resultados
    - Estadísticas de sesiones
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import desc
from src.db.database import SessionLocal
from src.db.models import ScrapedData, ProductoEcommerce, ScrapingSession

# Creación del blueprint para las rutas de la API
web_bp = Blueprint('web', __name__, url_prefix='/api')


def serialize_scraped_data(record):
    """Serializa un registro según su tipo polimórfico."""
    base_data = {
        "id": record.id,
        "url": record.url,
        "tipo": record.tipo,
        "fecha_extraccion": record.fecha_extraccion.isoformat(),
        "session_id": record.session_id
    }
    
    # Si es ProductoEcommerce, incluir campos específicos
    if isinstance(record, ProductoEcommerce):
        base_data.update({
            "nombre": record.nombre,
            "imagen_url": record.imagen_url,
            "precio_original": record.precio_original,
            "precio": record.precio,
            "descuento": record.descuento,
            "rating": record.rating_metadata,
            "descripcion": record.descripcion
        })
    elif hasattr(record, 'contenido'):
        # Para tipos genéricos con contenido JSON
        base_data["contenido"] = record.contenido
    
    return base_data


# ==================== RUTAS DE DATOS GENERALES ====================

@web_bp.route('/data', methods=['GET'])
def get_all_data():
    """
    Obtiene todos los registros con paginación.
    Query params: ?page=1&per_page=20&tipo=e-commerce
    """
    session = SessionLocal()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        tipo = request.args.get('tipo', None)
        
        query = session.query(ScrapedData)
        
        if tipo:
            query = query.filter(ScrapedData.tipo == tipo)
        
        total = query.count()
        data_records = query.order_by(desc(ScrapedData.fecha_extraccion))\
                           .limit(per_page)\
                           .offset((page - 1) * per_page)\
                           .all()
        
        data_list = [serialize_scraped_data(record) for record in data_records]
        
        return jsonify({
            "data": data_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@web_bp.route('/data/<int:data_id>', methods=['GET'])
def get_data_by_id(data_id):
    """
    Obtiene un registro específico de datos a partir de su ID.
    """
    session = SessionLocal()
    try:
        record = session.query(ScrapedData).filter(
            ScrapedData.id == data_id).first()
        
        if not record:
            return jsonify({"error": "Registro no encontrado"}), 404
        
        return jsonify(serialize_scraped_data(record))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# ==================== RUTAS ESPECÍFICAS DE E-COMMERCE ====================

@web_bp.route('/ecommerce', methods=['GET'])
def get_ecommerce_products():
    """
    Obtiene productos de e-commerce con filtros.
    Query params: ?page=1&per_page=20&min_precio=1000&max_precio=5000
    """
    session = SessionLocal()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        min_precio = request.args.get('min_precio', type=float)
        max_precio = request.args.get('max_precio', type=float)
        
        query = session.query(ProductoEcommerce)
        
        if min_precio:
            query = query.filter(ProductoEcommerce.precio >= min_precio)
        if max_precio:
            query = query.filter(ProductoEcommerce.precio <= max_precio)
        
        total = query.count()
        products = query.order_by(desc(ProductoEcommerce.fecha_extraccion))\
                       .limit(per_page)\
                       .offset((page - 1) * per_page)\
                       .all()
        
        product_list = [serialize_scraped_data(p) for p in products]
        
        return jsonify({
            "products": product_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# ==================== RUTAS DE SESIONES ====================

@web_bp.route('/sessions', methods=['GET'])
def get_all_sessions():
    """
    Obtiene todas las sesiones de scraping.
    """
    session = SessionLocal()
    try:
        sessions = session.query(ScrapingSession)\
                         .order_by(desc(ScrapingSession.start_time))\
                         .all()
        
        sessions_list = []
        for s in sessions:
            sessions_list.append({
                "id": s.id,
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "total_items": s.total_items,
                "successful_items": s.successful_items,
                "failed_items": s.failed_items,
                "success_rate": round((s.successful_items / s.total_items * 100) if s.total_items > 0 else 0, 2)
            })
        
        return jsonify(sessions_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@web_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session_details(session_id):
    """
    Obtiene detalles de una sesión específica y sus productos.
    """
    db_session = SessionLocal()
    try:
        scraping_session = db_session.query(ScrapingSession)\
                                    .filter(ScrapingSession.id == session_id)\
                                    .first()
        
        if not scraping_session:
            return jsonify({"error": "Sesión no encontrada"}), 404
        
        # Obtener productos de esta sesión
        products = db_session.query(ScrapedData)\
                            .filter(ScrapedData.session_id == session_id)\
                            .all()
        
        return jsonify({
            "session": {
                "id": scraping_session.id,
                "start_time": scraping_session.start_time.isoformat(),
                "end_time": scraping_session.end_time.isoformat() if scraping_session.end_time else None,
                "total_items": scraping_session.total_items,
                "successful_items": scraping_session.successful_items,
                "failed_items": scraping_session.failed_items
            },
            "products": [serialize_scraped_data(p) for p in products]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()


# ==================== ESTADÍSTICAS ====================

@web_bp.route('/stats', methods=['GET'])
def get_statistics():
    """
    Obtiene estadísticas generales del sistema.
    """
    session = SessionLocal()
    try:
        total_products = session.query(ScrapedData).count()
        total_ecommerce = session.query(ProductoEcommerce).count()
        total_sessions = session.query(ScrapingSession).count()
        
        # Productos por tipo
        tipos = session.query(ScrapedData.tipo, 
                            session.query(ScrapedData).filter(
                                ScrapedData.tipo == ScrapedData.tipo
                            ).count()).distinct().all()
        
        return jsonify({
            "total_products": total_products,
            "total_ecommerce": total_ecommerce,
            "total_sessions": total_sessions,
            "products_by_type": {
                "e-commerce": total_ecommerce,
                "generic": total_products - total_ecommerce
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
