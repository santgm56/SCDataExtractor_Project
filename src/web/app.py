#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: app.py
Descripción:
    Configuración de la aplicación web utilizando Flask.
    Esta aplicación expone una API REST para interactuar con los 
    datos extraídos y almacenados en la base de datos SQLite.
    
    Funcionalidades:
    - Ruta principal que muestra un mensaje de bienvenida.
    - Registro de rutas definidas en un blueprint (en routes.py).
    - Controladores de errores básicos para 404 y 500.
"""

from flask import Flask, jsonify
from src.web.routes import web_bp
from src.db.database import init_db

def create_app():
    """
    Función de fábrica para crear y configurar la aplicación Flask.
    """
    app = Flask(__name__)
    init_db()  # Inicializa la base de datos y crea las tablas
    
    # Configuración básica de la aplicación
    app.config['DEBUG'] = True  # Activar el modo de depuración (usar False en producción)
    
    # Registrar el blueprint con las rutas de la API
    app.register_blueprint(web_bp)
    
    @app.route('/')
    def index():
        return "Bienvenido a la API del Scraper - Proyecto SUPER_PROYECTO_FINAL"
    
    # Controlador de error para rutas no encontradas (404)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Recurso no encontrado"}), 404
    
    # Controlador de error para errores internos del servidor (500)
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500

    return app

# Bloque para ejecutar la aplicación directamente
if __name__ == '__main__':
    app = create_app()
    app.run()
