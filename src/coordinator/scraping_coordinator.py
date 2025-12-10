"""
Descripción:
    Coordina el scraping multi-tipo con gestión de subtipos dinámicos.
    - Soporta tareas con subtipos específicos (e-commerce/real_state)
    - Valida estructura de tareas
    - Integra correctamente con DataHandler para almacenamiento 
    estructurado
    - Incluye reintentos automáticos, rate limiting, caché y más
"""

import logging, time, json, csv, hashlib, concurrent.futures, pickle, os
from pathlib import Path
from src.utils.heap_cq import MinHeap
from dataclasses import dataclass, field
from io import StringIO
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from threading import Lock
from typing import List, Dict, Optional, Callable, Any
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from collections import OrderedDict

from src.utils.logger import get_logger
from src.utils.helpers import validate_url, calculate_stats

# Extractores necesarios
from src.components.dynamic.ecommerce_extractor import EcommerceExtractor

# Se importa tqdm para barra de progreso
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Se importa pandas para exportación Excel
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Se importa psutil para métricas de memoria
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class QueueFullError(Exception):
    """Excepción lanzada cuando la cola está llena"""
    pass

class LRUCache:
    """
    Implementación de caché LRU (Least Recently Used) thread-safe con persistencia en disco.
    Limita el tamaño máximo y elimina elementos menos usados.
    """
    
    def __init__(self, max_size: int = 1000, cache_dir: str = 'cache'):
        self.cache = OrderedDict()
        self.max_size = max_size
        self._lock = Lock()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'scraping_cache.pkl'
        self._load_from_disk()
    
    def _load_from_disk(self) -> None:
        """Carga el caché desde disco al iniciar"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                logging.getLogger('LRUCache').info(
                    f"Caché cargado desde disco: {len(self.cache)} entradas"
                )
            except Exception as e:
                logging.getLogger('LRUCache').warning(
                    f"Error cargando caché desde disco: {e}. Iniciando caché vacío."
                )
                self.cache = OrderedDict()
    
    def _save_to_disk(self) -> None:
        """Guarda el caché a disco"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            logging.getLogger('LRUCache').error(
                f"Error guardando caché a disco: {e}"
            )
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché"""
        with self._lock:
            if key in self.cache:
                # Mover al final
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Guarda un valor en el caché (memoria y disco)"""
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            # Si excede el tamaño, eliminar el menos usado
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
            # Guardar a disco después de cada cambio
            self._save_to_disk()
    
    def clear(self) -> None:
        """Limpia el caché (memoria y disco)"""
        with self._lock:
            self.cache.clear()
            self._save_to_disk()
    
    def size(self) -> int:
        """Retorna el tamaño actual del caché"""
        with self._lock:
            return len(self.cache)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Retorna información detallada del caché"""
        with self._lock:
            total_size = 0
            if self.cache_file.exists():
                total_size = self.cache_file.stat().st_size
            
            return {
                'entries': len(self.cache),
                'max_size': self.max_size,
                'disk_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_file': str(self.cache_file),
                'oldest_entry': list(self.cache.keys())[0] if self.cache else None,
                'newest_entry': list(self.cache.keys())[-1] if self.cache else None
            }

@dataclass(order=True)
class PriorityTask:
    """
    Wrapper para tareas con prioridad.
    """
    priority: int
    timestamp: float = field(compare=True)
    task: Dict = field(compare=False)
    
    def __init__(self, task: Dict):
        # Prioridad más baja en número = mayor prioridad en cola
        self.priority = task.get('priority', 0)
        self.timestamp = time.time()
        self.task = task

class TaskPriorityQueue:
    """
    Cola de prioridad thread-safe para tareas de scraping.
    
    Características:
    - Inserción O(log n)
    - Extracción O(log n)
    - Thread-safe con Lock
    - Soporte para agregar tareas dinámicamente
    - Límite máximo de tareas
    """
    
    def __init__(self, max_size: int = 10000):
        self._heap = MinHeap()
        self._lock = Lock()
        self._counter = 0
        self.max_size = max_size
    
    def push(self, task: Dict) -> None:
        """Agrega una tarea a la cola"""
        with self._lock:
            if len(self._heap) >= self.max_size:
                raise QueueFullError(
                    f"Cola llena. Máximo {self.max_size} tareas permitidas."
                )
            priority_task = PriorityTask(task)
            self._heap.push(priority_task)
    
    def push_many(self, tasks: List[Dict]) -> None:
        """Agrega múltiples tareas a la cola"""
        with self._lock:

            if len(self._heap) + len(tasks) > self.max_size:
                raise QueueFullError(
                    f"No se pueden agregar {len(tasks)} tareas. "
                    f"Espacio disponible: {self.max_size - len(self._heap)}"
                )
            for task in tasks:
                priority_task = PriorityTask(task)
                self._heap.push(priority_task)
    
    def pop(self) -> Optional[Dict]:
        """Extrae la tarea de mayor prioridad"""
        with self._lock:
            if self._heap:
                priority_task = self._heap.pop()
                return priority_task.task
            return None
    
    def peek(self) -> Optional[Dict]:
        """Ve la tarea de mayor prioridad sin extraerla"""
        with self._lock:
            if self._heap:
                return self._heap.peek().task
            return None
    
    def is_empty(self) -> bool:
        """Verifica si la cola está vacía"""
        with self._lock:
            return len(self._heap) == 0
    
    def size(self) -> int:
        """Retorna el número de tareas en la cola"""
        with self._lock:
            return len(self._heap)
    
    def clear(self) -> None:
        """Limpia la cola"""
        with self._lock:
            self._heap.clear()

class ValidationError(Exception):
    """Excepción para errores de validación de tareas"""
    pass


class NetworkError(Exception):
    """Excepción para errores de red que merecen reintento"""
    pass

class ScrapingCoordinator:
    """
    Clase para la gestión de subtipos y validación de tareas.
    
    Características mejoradas:
    - Cola de prioridad con límite de tamaño
    - Caché LRU para prevenir fugas de memoria
    - Manejo de excepciones específico
    - Validación exhaustiva de URLs y parámetros
    - Métricas de memoria
    - Circuit breaker para URLs problemáticas
    - Liberación apropiada de recursos
    """
    
    def __init__(self, 
                tasks: List[Dict], 
                max_workers: int = 5,
                delay_between_requests: float = 1.0,
                max_retries: int = 3,
                default_timeout: int = 30,
                respect_robots_txt: bool = True,
                enable_cache: bool = True,
                cache_size: int = 1000,
                max_queue_size: int = 10000,
                show_progress: bool = True,
                log_level: str = 'INFO',
                on_success: Optional[Callable[[Dict], None]] = None,
                on_error: Optional[Callable[[Dict, Exception], None]] = None,
                on_complete: Optional[Callable[[Dict], None]] = None):
        """
        Inicializa el coordinador de scraping.
        """

        self.DYNAMIC_SUBTYPES = ['e-commerce', 'real_state']
        
        self.validate_tasks(tasks)
        
        self.task_queue = TaskPriorityQueue(max_size=max_queue_size)
        self.task_queue.push_many(tasks)
        
        self._total_tasks = len(tasks)
        
        self.max_workers = max_workers
        self.delay = delay_between_requests
        self.max_retries = max_retries
        self.default_timeout = default_timeout
        self.respect_robots_txt = respect_robots_txt
        self.enable_cache = enable_cache
        self.show_progress = show_progress and TQDM_AVAILABLE
        
        # Callbacks
        self.on_success = on_success
        self.on_error = on_error
        self.on_complete = on_complete
        
        # Se crear un  mutex para la sincronización de hilos
        self.lock = Lock()
        
        self.logger = get_logger('ScrapingCoordinator')
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        self.results = []
        self._cache = LRUCache(max_size=cache_size)
        self._robots_cache: Dict[str, RobotFileParser] = {}
        
        self._worker_pool: Optional[ThreadPoolExecutor] = None
        
        # Se hace circuit breaker para URLs problemáticas
        # URL -> número de fallos
        self._failed_urls: Dict[str, int] = {}
        self._circuit_breaker_threshold = 5
        
        # Se definen las métricas globales
        self.metrics = {
            'total_duration': 0.0,
            'avg_task_duration': 0.0,
            'fastest_task': None,
            'slowest_task': None,
            'cache_hits': 0,
            'cache_misses': 0,
            'memory_usage': 0.0
        }

    def _run_with_timeout(self, func: Callable, timeout: float, *args, **kwargs):
        """
        Ejecuta func(*args, **kwargs) en un hilo separado y fuerza un Timeout
        si excede `timeout` segundos. Lanza TimeoutError (concurrent.futures)
        si se excede el tiempo.
        """
        with ThreadPoolExecutor(max_workers=1) as exec_local:
            future = exec_local.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                # Intentar cancelar (no mata el hilo si está en C bloqueante)
                try:
                    future.cancel()
                except Exception:
                    pass
                # Volver a lanzar el mismo tipo que capturas en process_task
                raise TimeoutError(f"Timeout de {timeout}s excedido")

    def add_task(self, task: Dict) -> None:
        """
        Agrega una nueva tarea a la cola (thread-safe).
        """
        self.validate_tasks([task])
        with self.lock:
            try:
                self.task_queue.push(task)
                self._total_tasks += 1
                self.logger.info(f"Tarea agregada: {task['url']}")
            except QueueFullError as e:
                self.logger.error(f"Error al agregar tarea: {e}")
                raise

    def add_tasks(self, tasks: List[Dict]) -> None:
        """
        Agrega múltiples tareas a la cola (thread-safe).
        """
        self.validate_tasks(tasks)
        with self.lock:
            try:
                self.task_queue.push_many(tasks)
                self._total_tasks += len(tasks)
                self.logger.info(f"{len(tasks)} tareas agregadas")
            except QueueFullError as e:
                self.logger.error(f"Error al agregar tareas: {e}")
                raise

    def validate_tasks(self, tasks: List[Dict]) -> None:
        """
        Valida la estructura y contenido de cada tarea de forma exhaustiva.
        
        Raises:
            ValidationError: Si alguna tarea no cumple los requisitos
        """
        required_fields = {
            'dynamic': ['url', 'type', 'subtype']
        }
        
        for idx, task in enumerate(tasks):
            task_type = task.get('type', 'invalid')
            
            # Validar tipo
            if task_type not in ['dynamic']:
                raise ValidationError(
                    f"Tarea {idx}: Tipo inválido '{task_type}'. "
                    f"Debe ser 'dynamic'"
                )
            
            # Validar campos requeridos
            required = required_fields[task_type]
            missing = [field for field in required if field not in task]
            
            if missing:
                raise ValidationError(
                    f"Tarea {idx} ({task.get('url', 'sin URL')}): "
                    f"Faltan campos requeridos: {missing}"
                )
            
            url = task.get('url', '')
            if not url or not isinstance(url, str):
                raise ValidationError(
                    f"Tarea {idx}: URL inválida o vacía"
                )
            
            # Validar formato de URL
            try:
                if not validate_url(url):
                    raise ValidationError(
                        f"Tarea {idx}: URL mal formada '{url}'. "
                        f"Debe incluir esquema (http/https) y dominio"
                    )
                
                # Validación adicional con urlparse
                parsed = urlparse(url)
                if not all([parsed.scheme, parsed.netloc]):
                    raise ValidationError(
                        f"Tarea {idx}: URL mal formada '{url}'. "
                        f"Debe incluir esquema (http/https) y dominio"
                    )
            except Exception as e:
                raise ValidationError(
                    f"Tarea {idx}: Error al parsear URL '{url}': {e}"
                )

            priority = task.get('priority', 0)
            if not isinstance(priority, int) or priority < 0:
                raise ValidationError(
                    f"Tarea {idx}: Prioridad inválida '{priority}'. "
                    f"Debe ser un entero >= 0"
                )
            
            # Validar timeout
            timeout = task.get('timeout')
            if timeout is not None:
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    raise ValidationError(
                        f"Tarea {idx}: Timeout inválido '{timeout}'. "
                        f"Debe ser un número > 0"
                    )
            
            # Validar subtipo dinámico
            if task_type == 'dynamic':
                subtype = task.get('subtype')
                if subtype not in self.DYNAMIC_SUBTYPES:
                    raise ValidationError(
                        f"Tarea {idx}: Subtipo dinámico inválido '{subtype}'. "
                        f"Debe ser uno de: {self.DYNAMIC_SUBTYPES}"
                    )
                
                # Validar parámetros específicos del subtipo
                if subtype == 'e-commerce':
                    num_productos = task.get('num_productos')
                    if num_productos is not None:
                        if not isinstance(num_productos, int) or num_productos < 1:
                            raise ValidationError(
                                f"Tarea {idx}: num_productos debe ser entero >= 1"
                            )

    def _get_cache_key(self, task: Dict) -> str:
        """Genera clave única para la tarea"""
        task_str = f"{task['url']}_{task['type']}_{task.get('subtype', '')}"
        return hashlib.md5(task_str.encode()).hexdigest()

    def _get_from_cache(self, task: Dict) -> Optional[Dict]:
        """Obtiene resultado de caché si existe"""
        if not self.enable_cache:
            return None
        cache_key = self._get_cache_key(task)
        result = self._cache.get(cache_key)
        
        # Actualizar métricas
        if result:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        
        return result

    def _save_to_cache(self, task: Dict, result: Dict) -> None:
        """Guarda resultado en caché"""
        if self.enable_cache:
            cache_key = self._get_cache_key(task)
            self._cache.set(cache_key, result)

    def is_allowed_by_robots(self, url: str) -> bool:
        """Verifica si el scraping está permitido por robots.txt.

        Nota: algunos sitios (p.ej. MercadoLibre) publican robots.txt
        con `Disallow: /` para `*`, pero el flujo requiere continuar.
        Para esos dominios se hace bypass explícito con un warning.
        """
        if not self.respect_robots_txt:
            return True

        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            # Whitelist de dominios donde se omite robots.txt
            skip_domains = {"mercadolibre.com.co", "listado.mercadolibre.com.co",
                            "mercadolibre.com", "listado.mercadolibre.com"}
            netloc = parsed.netloc.lower()
            if any(dom in netloc for dom in skip_domains):
                self.logger.warning(
                    "robots.txt bypass para dominio conocido con Disallow total: %s",
                    netloc,
                )
                return True

            robots_url = f"{base_url}/robots.txt"

            if base_url not in self._robots_cache:
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self._robots_cache[base_url] = rp

            return self._robots_cache[base_url].can_fetch("*", url)
        except Exception as e:
            self.logger.warning(f"Error verificando robots.txt para {url}: {e}")
            return True

    def _is_circuit_open(self, url: str) -> bool:
        """
        Verifica si el circuit breaker está abierto para esta URL.
        
        Returns:
            True si la URL ha fallado demasiadas veces
        """
        return self._failed_urls.get(url, 0) >= self._circuit_breaker_threshold

    def _record_failure(self, url: str) -> None:
        """Registra un fallo para el circuit breaker"""
        self._failed_urls[url] = self._failed_urls.get(url, 0) + 1

    def _record_success(self, url: str) -> None:
        """Resetea el contador de fallos tras un éxito"""
        if url in self._failed_urls:
            del self._failed_urls[url]

    def select_extractor(self, task: Dict):
        """Selección de extractores con subtipos"""
        url = task['url']
                    
        subtype = task['subtype']
        params = {
            'num_productos': task.get('num_productos', 1),
            'max_paginas': task.get('max_paginas', 1),
            'tienda': task.get('tienda')
        }
        
        if subtype == 'e-commerce':
            return EcommerceExtractor(url, **params)
            
        raise ValueError(f"Subtipo no implementado: {subtype}")

    def _compute_timeout(self, task: Dict) -> int:
        """Calcula timeout efectivo escalado por paginacion y tienda."""
        timeout = task.get('timeout', self.default_timeout)

        if task.get('type') == 'dynamic' and task.get('subtype') == 'e-commerce':
            try:
                max_paginas = max(1, int(task.get('max_paginas', 1) or 1))
            except (TypeError, ValueError):
                max_paginas = 1

            tienda = (task.get('tienda') or '').lower()
            # Alkosto demora mas porque cada scroll espera 5s; MercadoLibre es mas rapido
            per_page_budget = 25 if tienda == 'alkosto' else 15
            timeout = max(timeout, per_page_budget * max_paginas)

        return timeout

    def _scrape_with_extractor(self, task: Dict) -> Any:
        """Ejecuta el scraping con el extractor apropiado"""
        extractor = self.select_extractor(task)
        return extractor.scrape()

    def _apply_rate_limiting(self) -> None:
        """Aplica rate limiting entre requests"""
        with self.lock:
            time.sleep(self.delay)

    def _update_metrics(self, result: Dict) -> None:
        """Actualiza métricas agregadas tras cada tarea (éxito o fallo)."""
        duration = result.get('metrics', {}).get('duration')
        if duration is not None:
            self.metrics['total_duration'] += duration
            total_processed = len(self.results) + 1  # incluir actual
            self.metrics['avg_task_duration'] = round(
                self.metrics['total_duration'] / total_processed, 4
            )
            # Fastest
            if (self.metrics['fastest_task'] is None or
                duration < self.metrics['fastest_task']['duration']):
                self.metrics['fastest_task'] = {
                    'url': result.get('url'),
                    'duration': duration
                }
            # Slowest
            if (self.metrics['slowest_task'] is None or
                duration > self.metrics['slowest_task']['duration']):
                self.metrics['slowest_task'] = {
                    'url': result.get('url'),
                    'duration': duration
                }
        # Memory usage (RSS en MB)
        if PSUTIL_AVAILABLE:
            proc = psutil.Process()
            rss_mb = proc.memory_info().rss / (1024 * 1024)
            self.metrics['memory_usage'] = round(rss_mb, 2)

    def process_task(self, task: Dict) -> Dict:
        """
        Procesamiento con reintentos automáticos y manejo de excepciones.
        """
        start_time = time.time()
        timeout = self._compute_timeout(task)
        url = task['url']
        
        # Verificar circuit breaker
        if self._is_circuit_open(url):
            error_info = {
                'url': url,
                'error': 'Circuit breaker abierto - demasiados fallos previos',
                'task_type': task['type'],
                'subtype': task.get('subtype'),
                'circuit_breaker': True
            }
            self.logger.warning(f"Circuit breaker abierto para {url}")
            if self.on_error:
                self.on_error(task, Exception('Circuit breaker abierto'))
            return error_info
        
        # Verificar caché
        cached_result = self._get_from_cache(task)
        if cached_result:
            self.logger.debug(f"Cache hit para {url}")
            cached_result['from_cache'] = True
            return cached_result
        
        # Verificar robots.txt
        if not self.is_allowed_by_robots(url):
            error_info = {
                'url': url,
                'error': 'Bloqueado por robots.txt',
                'task_type': task['type'],
                'subtype': task.get('subtype')
            }
            self.logger.warning(f"URL bloqueada por robots.txt: {url}")
            if self.on_error:
                self.on_error(task, Exception('Bloqueado por robots.txt'))
            return error_info
        
        # Aplicar rate limiting
        self._apply_rate_limiting()
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                # Ejecutar el extractor con timeout cross-platform
                data = self._run_with_timeout(self._scrape_with_extractor, timeout, task)

                
                duration = time.time() - start_time
                
                # Resetear circuit breaker en éxito
                self._record_success(url)
                
                result = {
                    'url': url,
                    'type': task['type'],
                    'subtype': task.get('subtype'),
                    'priority': task.get('priority', 0),
                    'data': data,
                    'from_cache': False,
                    'metrics': {
                        'duration': round(duration, 3),
                        'attempts': attempt + 1,
                        'url_length': len(url)
                    }
                }
                
                log_data = {
                    'url': url,
                    'type': task['type'],
                    'subtype': task.get('subtype'),
                    'priority': task.get('priority', 0),
                    'results': len(data) if isinstance(data, list) else 1,
                    'duration': f"{duration:.2f}s"
                }
                self.logger.info(f"Tarea completada: {log_data}")
                
                self._save_to_cache(task, result)
                self._update_metrics(result)
                
                if self.on_success:
                    self.on_success(result)
                
                return result
            
            except TimeoutError as e:
                last_exception = TimeoutError(f"Timeout de {timeout}s excedido")
                self.logger.warning(
                    f"Timeout en intento {attempt + 1} para {url}"
                )
                # Timeout es recuperable - reintentar
                
            except (ConnectionError, OSError) as e:
                # Errores de red - reintentar
                last_exception = NetworkError(f"Error de red: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(
                        f"Error de red en intento {attempt + 1} para {url}, "
                        f"reintentando en {wait_time}s... Error: {str(e)}"
                    )
                    time.sleep(wait_time)
            
            except (ValueError, KeyError, AttributeError) as e:
                # Errores de validación/parseo - no reintentar
                last_exception = e
                self.logger.error(
                    f"Error de validación para {url}: {str(e)}. No se reintentará."
                )
                break  # Salir del loop de reintentos
            
            except Exception as e:
                # Otros errores - reintentar con precaución
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(
                        f"Error inesperado en intento {attempt + 1} para {url}, "
                        f"reintentando en {wait_time}s... Error: {str(e)}"
                    )
                    time.sleep(wait_time)
        
        # Registrar fallo en circuit breaker
        self._record_failure(url)
        
        # Todos los intentos fallaron
        duration = time.time() - start_time
        error_info = {
            'url': url,
            'error': str(last_exception),
            'error_type': type(last_exception).__name__,
            'task_type': task['type'],
            'subtype': task.get('subtype'),
            'priority': task.get('priority', 0),
            'metrics': {
                'duration': round(duration, 3),
                'attempts': self.max_retries
            }
        }
        
        self.logger.error(
            f"Tarea fallida después de {self.max_retries} intentos: {error_info}"
        )
        
        if self.on_error:
            self.on_error(task, last_exception)
        
        self._update_metrics(error_info)
        return error_info

    def run(self) -> Dict:
        """
        Ejecución con estadísticas finales y barra de progreso.
        Consume la cola para evitar reprocesar las mismas tareas en ejecuciones subsecuentes.
        """
        total_start_time = time.time()

        # Consumir la cola (pop) en lugar de copiar su contenido
        tasks = []
        while not self.task_queue.is_empty():
            task = self.task_queue.pop()
            if task:
                tasks.append(task)

        self.logger.info(
            f"Iniciando scraping de {len(tasks)} tareas "
            f"con {self.max_workers} workers"
        )

        if not tasks:
            self.logger.warning("No hay tareas para procesar")
            return {
                'results': [],
                'statistics': {
                    'total_tasks': 0,
                    'total_duration': '0s',
                    'avg_task_duration': '0s',
                    'min_task_duration': '0s',
                    'max_task_duration': '0s',
                    'cache_hit_rate': '0%',
                    'cache_size': 0,
                    'failed_urls_tracked': 0
                }
            }

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.process_task, task): task
                for task in tasks
            }

            if self.show_progress:
                future_iter = tqdm(
                    as_completed(futures),
                    total=len(futures),
                    desc="Scraping",
                    unit="tarea"
                )
            else:
                future_iter = as_completed(futures)

            for future in future_iter:
                result = future.result()
                self.results.append(result)

        total_duration = time.time() - total_start_time

        stats = calculate_stats(self.results)

        # Inyectar métricas agregadas calculadas
        stats['aggregated_metrics'] = {
            'avg_task_duration_runtime': self.metrics['avg_task_duration'],
            'fastest_task': self.metrics['fastest_task'],
            'slowest_task': self.metrics['slowest_task'],
            'memory_usage_mb': self.metrics['memory_usage']
        }

        stats['total_duration'] = f"{total_duration:.2f}s"
        stats['cache_hit_rate'] = (
            f"{(self.metrics['cache_hits']/(self.metrics['cache_hits']+self.metrics['cache_misses'])*100):.1f}%"
            if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else "0%"
        )
        stats['cache_size'] = self._cache.size()
        stats['cache_info'] = self._cache.get_cache_info()
        stats['failed_urls_tracked'] = len(self._failed_urls)

        stats['total_tasks'] = stats.pop('total')
        stats['avg_task_duration'] = stats.pop('avg_time')
        stats['min_task_duration'] = stats.pop('min_time')
        stats['max_task_duration'] = stats.pop('max_time')

        self.logger.info("Proceso completo. Estadísticas: %s", stats)

        result_data = {
            'results': self.results,
            'statistics': stats
        }

        if self.on_complete:
            self.on_complete(result_data)

        return result_data

    def export_results(self, format: str = 'json', filepath: Optional[str] = None) -> str:
        """
        Exporta resultados en múltiples formatos.
        Siempre guarda en un archivo en outputs/exports/ si no se especifica filepath.
        """
        # Crear carpeta de exportación si no existe
        export_dir = Path('outputs/exports')
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo con timestamp si no se proporciona
        if not filepath:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            if format == 'json':
                filepath = export_dir / f'scraping_results_{timestamp}.json'
            elif format == 'csv':
                filepath = export_dir / f'scraping_results_{timestamp}.csv'
            elif format == 'excel':
                filepath = export_dir / f'scraping_results_{timestamp}.xlsx'
        else:
            filepath = Path(filepath)
        
        if format == 'json':
            output = json.dumps(self.results, indent=2, ensure_ascii=False)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output)
            return str(filepath)
            
        elif format == 'csv':
            flat_results = []
            for r in self.results:
                flat_row = {
                    'url': r.get('url'),
                    'type': r.get('type') or r.get('task_type'),
                    'subtype': r.get('subtype'),
                    'success': 'data' in r,
                    'error': r.get('error'),
                    'error_type': r.get('error_type'),
                    'duration': r.get('metrics', {}).get('duration'),
                    'attempts': r.get('metrics', {}).get('attempts'),
                    'from_cache': r.get('from_cache', False),
                    'circuit_breaker': r.get('circuit_breaker', False)
                }
                flat_results.append(flat_row)
            
            if not flat_results:
                # Crear archivo vacío
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('')
                return str(filepath)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flat_results[0].keys())
                writer.writeheader()
                writer.writerows(flat_results)
            return str(filepath)
                
        elif format == 'excel':
            if not PANDAS_AVAILABLE:
                raise ImportError(
                    "pandas es requerido para exportar a Excel. "
                    "Instálalo con: pip install pandas openpyxl"
                )
            
            flat_results = []
            for r in self.results:
                flat_row = {
                    'URL': r.get('url'),
                    'Tipo': r.get('type') or r.get('task_type'),
                    'Subtipo': r.get('subtype'),
                    'Éxito': 'Sí' if 'data' in r else 'No',
                    'Error': r.get('error'),
                    'Tipo Error': r.get('error_type'),
                    'Duración (s)': r.get('metrics', {}).get('duration'),
                    'Intentos': r.get('metrics', {}).get('attempts'),
                    'Desde Caché': 'Sí' if r.get('from_cache') else 'No',
                    'Circuit Breaker': 'Sí' if r.get('circuit_breaker') else 'No'
                }
                flat_results.append(flat_row)
            
            df = pd.DataFrame(flat_results)
            df.to_excel(filepath, index=False, engine='openpyxl')
            return str(filepath)
        
        else:
            raise ValueError(
                f"Formato no soportado: {format}. Use 'json', 'csv' o 'excel'"
            )

    def get_failed_tasks(self) -> List[Dict]:
        """Retorna lista de tareas que fallaron"""
        return [r for r in self.results if 'error' in r]

    def get_successful_tasks(self) -> List[Dict]:
        """Retorna lista de tareas exitosas"""
        return [r for r in self.results if 'data' in r]

    def get_circuit_breaker_status(self) -> Dict[str, int]:
        """Retorna el estado del circuit breaker"""
        return self._failed_urls.copy()

    def reset_circuit_breaker(self, url: Optional[str] = None) -> None:
        """
        Resetea el circuit breaker.
        
        Args:
            url: URL específica a resetear, o None para resetear todas
        """
        if url:
            if url in self._failed_urls:
                del self._failed_urls[url]
                self.logger.info(f"Circuit breaker reseteado para {url}")
        else:
            self._failed_urls.clear()
            self.logger.info("Circuit breaker reseteado para todas las URLs")

    def retry_failed_tasks(self) -> Dict:
        """
        Reintenta las tareas que fallaron.
        """
        failed = self.get_failed_tasks()
        if not failed:
            self.logger.info("No hay tareas fallidas para reintentar")
            return {'results': [], 'statistics': {}}

        retry_tasks = []
        for f in failed:
            if f.get('circuit_breaker'):
                continue  # Evitar reintentar bloqueadas
            # Reconstruir tarea original mínima
            task = {
                'url': f['url'],
                'type': f.get('task_type', f.get('type', 'dynamic')),
                'subtype': f.get('subtype'),
                'priority': f.get('priority', 0),
                'timeout': f.get('metrics', {}).get('duration') or self.default_timeout
            }
            # Validar que siga siendo dinámica
            if task['type'] != 'dynamic' or not task['subtype']:
                self.logger.warning(f"Tarea inválida para reintento: {task}")
                continue
            retry_tasks.append(task)

        if not retry_tasks:
            self.logger.info("No hay tareas válidas para reintentar")
            return {'results': [], 'statistics': {}}

        self.logger.info(f"Reintentando {len(retry_tasks)} tareas fallidas")

        retry_coordinator = ScrapingCoordinator(
            tasks=retry_tasks,
            max_workers=self.max_workers,
            delay_between_requests=self.delay,
            max_retries=self.max_retries,
            default_timeout=self.default_timeout,
            respect_robots_txt=self.respect_robots_txt,
            enable_cache=False,
            show_progress=self.show_progress
        )

        return retry_coordinator.run()

    def clear_cache(self) -> None:
        """Limpia el caché de resultados"""
        self._cache.clear()
        self._robots_cache.clear()
        self.logger.info("Caché limpiado")

    def cleanup(self) -> None:
        """
        Libera todos los recursos utilizados.
        Llamar al finalizar el uso del coordinador.
        """
        self.logger.info("Iniciando limpieza de recursos...")
        
        # Limpiar caché
        self.clear_cache()
        
        # Limpiar cola
        self.task_queue.clear()
        
        # Limpiar resultados
        self.results.clear()
        
        # Limpiar circuit breaker
        self._failed_urls.clear()
        
        self.logger.info("Recursos liberados correctamente")

    def __del__(self):
        """Destructor para asegurar liberación de recursos"""
        try:
            self.cleanup()
        except Exception as e:
            # Evitar errores en destructor
            pass

    def __enter__(self):
        """Soporte para context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Limpieza automática al salir del contexto"""
        self.cleanup()
        return False