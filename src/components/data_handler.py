"""
Descripción:
    Este módulo define la clase DataHandler para el manejo y 
    procesamiento de datos extraídos durante el proceso de scraping.

    Además, se incluyen métodos para:
    - Generar reportes en formato de documento (TXT o HTML).
    - Categorizar los resultados.
    - Aplicar un modelo básico de proyección de precios de inmuebles.
"""
"""
- Módulo hashlib:
Convierte los datos de entrada en una cadena de bytes de tamaño fijo.
Fuente: https://docs.python.org/es/3.10/library/hashlib.html

- Módulo json:
Para convertir datos a formato JSON.
Fuente: https://www.freecodecamp.org/espanol/news/python-leer-archivo-json-como-cargar-json-desde-un-archivo-y-procesar-dumps/

- Módulo logging:
Permite implementar un sistema de registro flexible para rastrear
eventos dentro de aplicaciones y bibliotecas.
Fuente: https://realpython.com/python-logging/

- Módulo os:
Permite interactuar con funcionalidades dependientes del sistema 
operativo.
Fuente: https://docs.python.org/es/3.10/library/os.html

- Módulo re:
Este módulo contiene funciones y expresiones regulares que pueden ser 
usadas para buscar patrones dentro de cadenas de texto.
Fuente: https://docs.python.org/es/3.13/library/re.html

- Módulo datetime:
Proporciona objetos y funciones para manipular fechas y horas.
Fuente: https://www.w3schools.com/python/python_datetime.asp

- Módulo typing: 
Permite especificar tipos de datos de manera más precisa y legible.
Fuente: https://medium.com/@moraneus/exploring-the-power-of-pythons-typing-library-ff32cec44981

¿Por qué se usa el módulo `typing` en el código?
Este módulo nos facilita en la definición de los tipos de datos esperados, 
lo cual mejora la claridad del código, facilitando el mantenimiento y 
permitiendo que herramientas detecten errores antes de ejecutar.
"""

import hashlib
import json
import logging
import os
import re
from datetime import datetime
from typing import Union, List, Dict

# Importar la clase ScrapedData y la sesión de la base de datos
from src.db.database import SessionLocal 
from src.db.models import ScrapedData

class DataHandler:
    """
    Clase que se unifica para manejo el de datos del programa
    (JSON, SQL, reportes, etc.).
    """
    def __init__(
        self, 
        data: Union[Dict, List[Dict]], 
        storage_format: str = 'both',
        logger: logging.Logger = None
    ):
        self.__data = data
        self.__storage_format = storage_format.lower()
        self.__logger = logger or logging.getLogger(
            self.__class__.__name__
            )
        self.__logger.setLevel(logging.DEBUG)

    @property
    def data(self) -> Union[Dict, List[Dict]]:
        return self.__data
    
    @property
    def storage_format(self) -> str:
        return self.__storage_format
    
    @storage_format.setter
    def storage_format(self, value: str):
        if value not in ["json", "sql", "both"]:
            raise ValueError("Este formato no es válido")
        self.__storage_format = value.lower()

    @property
    def logger(self) -> logging.Logger:
        return self.__logger
    
    @logger.setter
    def logger(self, value: logging.Logger):
        if not isinstance(value, logging.Logger):
            raise TypeError("Lo siento, pero debe ser una instancia "
                            "de logging.Logger")
        self.__logger = value
            
    def correct_filename(self, name: str, max_length: int = 50) -> str:
        """Corrige los nombres para archivos"""
        if not name:
            return f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return (
            name.strip()
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")[:max_length]
        )

    def store_data(self, url: str = None, tipo: str = "generic") -> bool:
        """
        Almacena en JSON y/o SQL según storage_format.
        - Soporta datos individuales o listas.
        - Combina nombre corregido + timestamp (Marca del Tiempo).
        """
        if not self.data:
            self.logger.error("No hay datos para almacenar")
            return False
        
        formato = True
        
        if self.storage_format in ('json', 'both'):
            if not self.store_json(url, tipo):
                formato = False
        
        if self.storage_format in ('sql', 'both'):
            if not self.store_sql(tipo):
                formato = False
        
        return formato
    
    def store_json(self, url: str, tipo: str) -> bool:
        """
        Lógica unificada de almacenamiento JSON con 
        estructura de carpetas."""
        try:
            # Mapeo de tipos a carpetas
            folder_map = {
                "static": "static_pages_extractors",
                "e-commerce": "dynamic_extractors/e-commerce",
                "real_state": "dynamic_extractors/real_state",
                "dynamic": "dynamic_extractors/generic"
            }
            
            # Obtener carpeta destino
            base_folder = folder_map.get(tipo, "generic_data")
            output_dir = os.path.join("outputs", base_folder)
            os.makedirs(output_dir, exist_ok=True)

            data_list = self.data if isinstance(self.data, list) else [self.data]

            for item in data_list:
                # Limpiar nombre del producto (¡FIX AQUÍ!)
                nombre_producto = item.get("title", "sin_titulo")
                nombre_seguro = re.sub(r'[\\/*?:"<>|]', '_', nombre_producto)  # Eliminar caracteres prohibidos
                nombre_seguro = nombre_seguro.strip().lower().replace(' ', '_')[:50]  # Normalizar
                
                # Generar hash único
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                filename = f"{nombre_seguro}_{url_hash}.json"
                filepath = os.path.join(output_dir, filename)

                # Guardar archivo
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(item, f, ensure_ascii=False, indent=4)
                
                self.logger.debug(f"JSON guardado: {filepath}")

            return True
        except Exception as e:
            self.logger.error(f"Error JSON: {str(e)}")
            return False

    def store_sql(self, tipo: str) -> bool:
        """Lógica unificada de almacenamiento SQL."""
        session = SessionLocal()
        try:
            data_list = (
                self.data if isinstance(self.data, list) 
                else [self.data])

            for item in data_list:
                # Usar URL del producto, no la URL general
                producto_url = item.get("url")
                if not producto_url:
                    continue

                existing = (
                    session.query(ScrapedData)
                    .filter_by(url=producto_url)
                    .first()
                )
                content_json = json.dumps(item, ensure_ascii=False)

                if existing:
                    existing.contenido = content_json
                    self.logger.info(
                        f"Actualizado SQL: {producto_url}")
                else:
                    new_record = ScrapedData(
                        url=producto_url,
                        tipo=tipo,
                        contenido=content_json
                    )
                    session.add(new_record)
                    self.logger.info(
                        f"Nuevo registro en el SQL: {producto_url}")

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            self.logger.error(
                f"Ha habido un error en el SQL: {str(e)}")
            return False
        finally:
            session.close()

    def generate_report(self, report_type='txt'):
        """
        Genera un reporte basado en los datos extraídos.
        """
        try:
            report_dir = os.path.join("outputs", "reports")
            os.makedirs(report_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(
                report_dir, f"report_{timestamp}.{report_type}"
                )

            # Generación de reporte en formato TXT
            if report_type == 'txt':
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("Reporte de Datos Extraídos\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Fecha y Hora: {datetime.now()}\n\n")
                    f.write("Datos:\n")
                    for item in self.data:
                        f.write(f"{item}\n")
            # Generación de reporte en formato HTML
            elif report_type == 'html':
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("<html><head><title>Reporte de Datos "
                            "Extraídos</title></head><body>")
                    f.write("<h1>Reporte de Datos Extraídos</h1>")
                    f.write(f"<p>Fecha y Hora: {datetime.now()}</p>")
                    f.write("<hr>")
                    f.write("<ul>")
                    for item in self.data:
                        f.write(f"<li>{item}</li>")
                    f.write("</ul>")
                    f.write("</body></html>")
            else:
                self.logger.error(
                    f"Tipo de reporte {report_type} no soportado.")
                return None

            self.logger.info(
                f"Reporte generado exitosamente: {filename}"
                )
            return filename
        except Exception as e:
            self.logger.error(f"Error al generar el reporte: {str(e)}")
            return None
        

    def categorize_data(self):
        """
        Categoriza los datos extraídos.
        """
        try:
            categories = {}
            for item in self.data:
                category = item.get('category', 'Sin Categoría')
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
            self.logger.info(
                f"Datos categorizados en {len(categories)} categorías.")
            return categories
        except Exception as e:
            self.logger.error(
                f"Error al categorizar los datos: {str(e)}")
            return {}

# Para después...
"""    def project_prices(self):
        
        Aplica un modelo básico de proyección de precios de inmuebles.
        
        try:
            projected_prices = []
            for item in self.data:
                price = item.get('price')
                if isinstance(price, (int, float)):
                    projected = price * 1.05 
                    new_item = item.copy()
                    new_item['projected_price'] = round(projected, 2)
                    projected_prices.append(new_item)
                else:
                    projected_prices.append(item)
            self.logger.info(
                "Proyección de precios aplicada a "
                f"{len(projected_prices)} elementos.")
            return projected_prices
        except Exception as e:
            self.logger.error(f"Error al proyectar precios: {str(e)}")
            return self.data"""