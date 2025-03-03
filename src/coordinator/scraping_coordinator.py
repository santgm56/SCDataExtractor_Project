"""
Descripción:
    Coordina el scraping multi-tipo con gestión de subtipos dinámicos.
    - Soporta tareas con subtipos específicos (e-commerce/real_state)
    - Valida estructura de tareas
    - Integra correctamente con DataHandler para almacenamiento 
    estructurado

- Módulo logging:
Permite implementar un sistema de registro flexible para rastrear
eventos dentro de aplicaciones y bibliotecas.
Fuente: https://realpython.com/python-logging/

- Módulo concurrent.futures:
Proporciona una interfaz de alto nivel para ejecutar tareas de 
manera asíncrona, utilizando grupos de subprocesos o trabajadores 
de procesos.
Fuente: https://medium.com/@smrati.katiyar/introduction-to-concurrent-futures-in-python-009fe1d4592c

- Módulo typing: 
Permite especificar tipos de datos de manera más precisa y legible.
Fuente: 
https://medium.com/@moraneus/exploring-the-power-of-pythons-typing-library-ff32cec44981

¿Por qué se usa el módulo `typing` en el código?
El módulo typing se implementa para definir tipos de datos esperados en el 
código de manera explícita y robusta (por ejemplo, List en lugar de 
solo list). Esto mejora la claridad del código, facilita su 
mantenimiento y permite que herramientas detecten errores de tipo 
antes de ejecutar el programa, esto nos ayudar por mucho más a aumentar 
la fiabilidad en el programa.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from src.utils.logger import get_logger
from src.utils.helpers import validate_url, calculate_stats

# Importar todos los extractores necesarios
from src.components.static_page_extractor import StaticPageExtractor
from src.components.dynamic.ecommerce_extractor import EcommerceExtractor
from src.components.dynamic.real_state_extractor import RealEstateExtractor

class ScrapingCoordinator:
    """
    Clase para la gestión de subtipos y validación de tareas
    """
    def __init__(self, tasks: List[Dict], max_workers: int = 5):
        self.STATIC_TYPES = ['static']
        self.DYNAMIC_SUBTYPES = ['e-commerce', 'real_state']
        self.validate_tasks(tasks)
        self.tasks = tasks
        self.max_workers = max_workers
        self.logger = get_logger('ScrapingCoordinator')
        self.logger.setLevel(logging.DEBUG)
        self.results = []

    def validate_tasks(self, tasks):
        """Valida la estructura de cada tarea"""
        required_fields = {
            'static': ['url', 'type'],
            'dynamic': ['url', 'type', 'subtype']
        }
        
        for task in tasks:
            task_type = task.get('type', 'invalid')
            
            if task_type not in ['static', 'dynamic']:
                raise ValueError(f"Tipo de tarea inválido: {task_type}")
                
            required = required_fields[task_type]
            missing = [field for field in required if field not in task]
            
            if missing:
                raise ValueError(
                    f"Tarea {task.get('url')} falta campos: {missing}"
                )
            
            if task_type == 'dynamic' and task.get('subtype') not in self.DYNAMIC_SUBTYPES:
                raise ValueError(
                    f"Subtipo dinámico inválido: {task.get('subtype')}"
                )

    def select_extractor(self, task: Dict):
        """Selección mejorada de extractores con subtipos"""
        url = task['url']
        task_type = task['type']
        
        if task_type == 'static':
            return StaticPageExtractor(url)
            
        # Manejo de subtipos dinámicos
        subtype = task['subtype']
        params = {
            'num_productos': task.get('num_productos', 1),
            'tienda': task.get('tienda')
        }
        
        if subtype == 'e-commerce':
            return EcommerceExtractor(url, **params)
        elif subtype == 'real_state':
            return RealEstateExtractor(url, **params)
            
        raise ValueError(f"Subtipo no implementado: {subtype}")

    def process_task(self, task: Dict):
        """Procesamiento con logging mejorado"""
        try:
            extractor = self.select_extractor(task)
            data = extractor.scrape()
            
            # Registro detallado
            log_data = {
                'url': task['url'],
                'type': task['type'],
                'subtype': task.get('subtype'),
                'results': len(data) if isinstance(data, list) else 1
            }
            self.logger.info(f"Tarea completada: {log_data}")
            
            return {
                'url': task['url'],
                'type': task['type'],
                'subtype': task.get('subtype'),
                'data': data
            }
            
        except Exception as e:
            error_info = {
                'url': task['url'],
                'error': str(e),
                'task_type': task['type'],
                'subtype': task.get('subtype')
            }
            self.logger.error(
                "Error en tarea: %s", error_info, exc_info=True)
            return error_info

    def run(self):
        """Ejecución con estadísticas finales"""
        self.logger.info(
            f"Iniciando scraping de {len(self.tasks)} tareas "
            f"con {self.max_workers} workers"
        )
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.process_task, task) for task in self.tasks]
            
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
                
        # Generar reporte estadístico
        success = sum(1 for r in self.results if 'data' in r)
        errors = len(self.results) - success
        
        stats = {
            'total_tasks': len(self.tasks),
            'success': success,
            'errors': errors,
            'error_rate': f"{(errors/len(self.tasks)*100):.1f}%" if self.tasks else "0%"
        }
        
        self.logger.info("Proceso completo. Estadísticas: %s", stats)
        return {
            'results': self.results,
            'statistics': stats
        }