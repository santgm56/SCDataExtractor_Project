#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo: database.py
Descripción:
    Configura la conexión a la base de datos utilizando SQLAlchemy.
    Define el engine, el sessionmaker y funciones para inicializar 
    la base de datos, creando las tablas definidas en los modelos 
    (por ejemplo, ScrapedData).
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, ScrapedData

# Configuración del logger para el módulo de base de datos
logger = logging.getLogger("Database")
logger.setLevel(logging.DEBUG)


# Asegurar carpeta de salida para SQLite por defecto
DEFAULT_SQLITE_PATH = os.path.join("outputs", "scraped_data.db")
os.makedirs(os.path.dirname(DEFAULT_SQLITE_PATH), exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}"
    )

# Creación del engine de SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Configuración del sessionmaker para gestionar sesiones de la base de datos
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
    )

def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas en 
    los modelos.
    
    Esta función utiliza la metadata de SQLAlchemy para crear las tablas 
    en la base de datos.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada exitosamente.")
    except Exception as e:
        logger.error("Error al inicializar la base de datos: %s", str(e))
        raise

def get_db():
    """
    Generador que provee una sesión de la base de datos.

    Se recomienda utilizarlo en contextos 'with' para asegurar que la 
    sesión se cierra correctamente después de usarla.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print(":) Tablas creadas exitosamente.")