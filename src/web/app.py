#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: app.py
Descripción:
    Configuración de la aplicación web utilizando Flask.
    Esta aplicación expone una API REST para interactuar con los datos extraídos y almacenados en la base de datos SQLite.
    
    Funcionalidades:
    - API REST con documentación de endpoints
    - CORS habilitado para acceso desde frontend
    - Configuración flexible mediante variables de entorno
    - Logging configurado
    - Manejo robusto de errores
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from src.web.routes import web_bp
from src.db.database import init_db

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """
    Función de fábrica para crear y configurar la aplicación Flask.
    
    Args:
        config: Diccionario opcional con configuraciones personalizadas
    """
    app = Flask(__name__)
    
    # Configuración desde variables de entorno
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JSON_AS_ASCII'] = False  # Soporte para caracteres Unicode
    app.config['JSON_SORT_KEYS'] = False  # Mantener orden de keys
    
    # Aplicar configuración personalizada si existe
    if config:
        app.config.update(config)
    
    # Inicializar base de datos
    try:
        init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
    
    # Habilitar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Registrar el blueprint con las rutas de la API
    app.register_blueprint(web_bp)
    
    @app.route('/')
    def index():
        """Ruta principal con documentación de endpoints."""
        return jsonify({
            "message": "API del Scraper - SCDataExtractor",
            "version": "1.0",
            "endpoints": {
                "datos_generales": {
                    "GET /api/data": "Lista todos los datos (paginado)",
                    "GET /api/data/<id>": "Obtiene un dato específico"
                },
                "ecommerce": {
                    "GET /api/ecommerce": "Lista productos (con filtros de precio)"
                },
                "sesiones": {
                    "GET /api/sessions": "Lista todas las sesiones de scraping",
                    "GET /api/sessions/<id>": "Detalle de sesión con productos"
                },
                "estadisticas": {
                    "GET /api/stats": "Estadísticas generales del sistema"
                }
            },
            "parametros_comunes": {
                "paginacion": "?page=1&per_page=20",
                "filtros": "?tipo=e-commerce&min_precio=1000&max_precio=5000"
            }
        })
    
    @app.route('/health')
    def health_check():
        """Endpoint para verificar el estado de la aplicación."""
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    
    # Controlador de error para rutas no encontradas (404)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Recurso no encontrado",
            "message": "La ruta solicitada no existe"
        }), 404
    
    # Controlador de error para errores internos del servidor (500)
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Error interno del servidor: {str(error)}")
        return jsonify({
            "error": "Error interno del servidor",
            "message": "Ocurrió un error inesperado"
        }), 500
    
    # Controlador para errores de validación (400)
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Solicitud incorrecta",
            "message": str(error)
        }), 400

    logger.info(f"Aplicación Flask creada en modo {'DEBUG' if app.config['DEBUG'] else 'PRODUCTION'}")
    return app

# Bloque para ejecutar la aplicación directamente
if __name__ == '__main__':
    app = create_app()
    
    # Configuración de host y puerto desde variables de entorno
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"Iniciando servidor en http://{host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])
