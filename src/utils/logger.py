"""
- Módulo logging:
Permite implementar un sistema de registro flexible para rastrear
eventos dentro de aplicaciones y bibliotecas.
Fuente: https://realpython.com/python-logging/

- Módulo os:
Permite interactuar con funcionalidades dependientes del sistema 
operativo.
Fuente: https://docs.python.org/es/3.10/library/os.html

- Módulo typing: 
Permite especificar tipos de datos de manera más precisa y legible.
Fuente: https://medium.com/@moraneus/exploring-the-power-of-pythons-typing-library-ff32cec44981

¿Por qué se usa el módulo `typing` en el código?
Este módulo nos facilita en la definición de los tipos de datos esperados, 
lo cual mejora la claridad del código, facilitando el mantenimiento y 
permitiendo que herramientas detecten errores antes de ejecutar.
"""

import logging
import os

from logging.handlers import RotatingFileHandler
from typing import Dict, Any


def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """Configura el logger raíz con handlers para archivo y consola"""
    # Configurar logger raíz
    logger = logging.getLogger()
    logger.setLevel(config.get('level', 'INFO').upper())

    # Eliminar handlers existentes para evitar duplicados
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Crear directorio de logs
    log_dir = config.get('log_dir', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Formato común
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler de archivo rotativo
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'scraping.log'),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler de consola
    if config.get('enable_console', True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    # Suprime logs detallados de Selenium y WebDriver
    logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)

    return logger

def get_logger(name: str = None) -> logging.Logger:
    """Obtiene un logger configurado. Si setup_logger no se ejecutó, devuelve un logger básico."""
    logger = logging.getLogger(name or "ScrapingLogger")

    if not logger.hasHandlers():  # Si no hay handlers, configuramos un logger básico
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
