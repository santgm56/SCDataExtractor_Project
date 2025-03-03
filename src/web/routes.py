#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: routes.py
Descripción:
    Define las rutas de la API para la aplicación web.
    Estas rutas permiten consultar y visualizar los datos extraídos 
    por el scraper.
    
    Funcionalidades:
    - Ruta para obtener todos los registros de datos (/api/data).
    - Ruta para obtener un registro específico por su ID (/api/data/<id>).
"""

from flask import Blueprint, jsonify, request
from src.db.database import SessionLocal
from src.db.models import ScrapedData

# Creación del blueprint para las rutas de la API
web_bp = Blueprint('web', __name__, url_prefix='/api')

@web_bp.route('/data', methods=['GET'])
def get_all_data():
    """
    Obtiene todos los registros de datos extraídos almacenados en la 
    base de datos.
    """
    session = SessionLocal()
    try:
        data_records = session.query(ScrapedData).all()
        data_list = []
        for record in data_records:
            data_list.append({
                "id": record.id,
                "url": record.url,
                "tipo": record.tipo,
                "contenido": record.contenido,
                "fecha_extraccion": record.fecha_extraccion.isoformat()
            })
        return jsonify(data_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@web_bp.route('/data/<int:data_id>', methods=['GET'])
def get_data_by_id(data_id):
    """
    Obtiene un registro específico de datos a partir de su ID.
    
    :param data_id: ID del registro.
    :return: JSON con la información del registro o un mensaje de error.
    """
    session = SessionLocal()
    try:
        record = session.query(ScrapedData).filter(
            ScrapedData.id == data_id).first()
        if record:
            data_item = {
                "id": record.id,
                "url": record.url,
                "tipo": record.tipo,
                "contenido": record.contenido,
                "fecha_extraccion": record.fecha_extraccion.isoformat()
            }
            return jsonify(data_item)
        else:
            return jsonify({"error": "Registro no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
