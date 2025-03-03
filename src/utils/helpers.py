"""
- Módulo hashlib:
Convierte los datos de entrada en una cadena de bytes de tamaño fijo.
Fuente: https://docs.python.org/es/3.10/library/hashlib.html

- Módulo os:
Permite interactuar con funcionalidades dependientes del sistema 
operativo.
Fuente: https://docs.python.org/es/3.10/library/os.html

- Módulo re:
Este módulo contiene funciones y expresiones regulares que pueden ser 
usadas para buscar patrones dentro de cadenas de texto.
Fuente: https://docs.python.org/es/3.13/library/re.html

- Módulo typing: 
Permite especificar tipos de datos de manera más precisa y legible.
Fuente: https://medium.com/@moraneus/exploring-the-power-of-pythons-typing-library-ff32cec44981

¿Por qué se usa el módulo `typing` en el código?
Este módulo nos facilita en la definición de los tipos de datos esperados, 
lo cual mejora la claridad del código, facilitando el mantenimiento y 
permitiendo que herramientas detecten errores antes de ejecutar.

- Módulo urllib.parse.urljoin:
Construye una URL completa ("absoluta") combinando una "URL base" 
(base) con otra URL (url)
Fuente: https://docs.python.org/3/library/urllib.parse.html
"""

import hashlib
import os
import re

from typing import List, Dict, Union
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Valida que una URL tenga formato correcto"""
    regex = re.compile(
        r'^(https?://)?'
        r'(([A-Z0-9-]+\.)+[A-Z]{2,63})' 
        r'(:\d+)?'  # Puerto
        r'(/.*)?$',  # Ruta
        re.IGNORECASE
    )
    return re.match(regex, url) is not None

def create_directory_structure(base_path: str = "outputs") -> None:
    """Crea la estructura de directorios necesaria"""
    directories = [
        base_path,
        os.path.join(base_path, "static_pages_extractors"),
        os.path.join(base_path, "dynamic_extractors", "e-commerce"),
        os.path.join(base_path, "dynamic_extractors", "real_state"),
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def clean_filename(filename: str, max_length: int = 100) -> str:
    """Limpia un nombre de archivo para hacerlo válido en todos los 
    sistemas"""
    # Eliminar caracteres especiales y espacios extras
    cleaned = re.sub(
        r'[\\/*?:"<>|]', 
        "_", 
        filename.strip()
    )
    # Reemplazar múltiples guiones bajos por uno solo
    cleaned = re.sub(r'_{2,}', '_', cleaned)
    # Limitar longitud y eliminar espacios
    return cleaned[:max_length].strip('_')

def calculate_stats(
        results: List[Dict]) -> Dict[str, Union[int, float]]:
    """Calcula estadísticas de los resultados del scraping"""
    stats = {
        'total': len(results),
        'success': 0,
        'errors': 0,
        'error_types': {},
        'avg_time': 0.0
    }
    
    for result in results:
        if 'error' in result:
            stats['errors'] += 1
            error_type = result['error'].split(':')[0]
            stats['error_types'][error_type] = (stats['error_types']
                                                .get(error_type, 0) + 1)
        else:
            stats['success'] += 1
    
    if stats['total'] > 0:
        stats['success_rate'] = (stats['success'] / stats['total']) * 100
        stats['error_rate'] = (stats['errors'] / stats['total']) * 100
    
    return stats

def generate_hash(content: str, length: int = 8) -> str:
    """Genera un hash único para contenido"""
    return hashlib.md5(content.encode()).hexdigest()[:length]