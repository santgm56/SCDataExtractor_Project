import hashlib
import os
import re

from typing import List, Dict, Union
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Valida que una URL tenga formato correcto"""
    try:
        # Validación con urlparse primero
        parsed = urlparse(url)
        
        # Protocolo obligatorio
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Debe tener dominio/host
        if not parsed.netloc:
            return False
        
        # Validación adicional con regex
        regex = re.compile(
            r'^https?://'  # Protocolo obligatorio
            r'(?:'
            r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63}'  # Dominio
            r'|localhost'  # O localhost
            r'|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'  # O IP
            r')'
            r'(?::\d{1,5})?'  # Puerto opcional (1-5 dígitos)
            r'(?:/.*)?$',  # Ruta opcional
            re.IGNORECASE
        )
        
        return re.match(regex, url) is not None
    except Exception:
        return False

def create_directory_structure(base_path: str = "outputs") -> None:
    """Crea la estructura de directorios necesaria"""
    directories = [
        base_path,
        os.path.join(base_path, "dynamic_extractors", "e-commerce"),
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

def calculate_stats(results: List[Dict]) -> Dict[str, Union[int, float, str]]:
    """
    Calcula estadísticas completas de los resultados del scraping.
    """
    stats = {
        'total': len(results),
        'success': 0,
        'errors': 0,
        'cached': 0,
        'circuit_breaker_blocks': 0,
        'error_types': {},
        'total_time': 0.0,
        'avg_time': 0.0,
        'min_time': float('inf'),
        'max_time': 0.0
    }
    
    if len(results) == 0:
        stats['min_time'] = 0.0
        return stats
    
    for result in results:
        # Contar éxitos y errores
        if 'error' in result:
            stats['errors'] += 1
            # Registrar tipos de error
            error_type = result.get('error_type', 'Unknown')
            stats['error_types'][error_type] = stats['error_types'].get(error_type, 0) + 1
        else:
            stats['success'] += 1
        
        # Contar resultados desde caché
        if result.get('from_cache', False):
            stats['cached'] += 1
        
        # Contar bloqueos por circuit breaker
        if result.get('circuit_breaker', False):
            stats['circuit_breaker_blocks'] += 1
        
        # Calcular estadísticas de tiempo
        duration = result.get('metrics', {}).get('duration', 0)
        if duration > 0:
            stats['total_time'] += duration
            stats['min_time'] = min(stats['min_time'], duration)
            stats['max_time'] = max(stats['max_time'], duration)
    
    # Calcular tasas porcentuales
    if stats['total'] > 0:
        stats['success_rate'] = f"{(stats['success'] / stats['total']) * 100:.1f}%"
        stats['error_rate'] = f"{(stats['errors'] / stats['total']) * 100:.1f}%"
        stats['cache_rate'] = f"{(stats['cached'] / stats['total']) * 100:.1f}%"
    
    # Calcular tiempo promedio
    if stats['success'] > 0:
        stats['avg_time'] = f"{stats['total_time'] / stats['success']:.2f}s"
    else:
        stats['avg_time'] = "0.00s"
    
    # Formatear tiempos min/max
    if stats['min_time'] == float('inf'):
        stats['min_time'] = "0.00s"
    else:
        stats['min_time'] = f"{stats['min_time']:.2f}s"
    
    stats['max_time'] = f"{stats['max_time']:.2f}s"
    stats['total_time'] = f"{stats['total_time']:.2f}s"
    
    return stats

def generate_hash(content: str, length: int = 8) -> str:
    """Genera un hash único para contenido"""
    return hashlib.md5(content.encode()).hexdigest()[:length]