"""
Archivo: main.py
Descripción:
    Punto de entrada principal del scraper usando ScrapingCoordinator.
    
    Funcionalidades:
    - Configuración del sistema de logging.
    - Gestión de múltiples tareas de scraping con cola de prioridad.
    - Procesamiento paralelo con workers.
    - Caché LRU, reintentos automáticos, circuit breaker.
    - Exportación de resultados (JSON, CSV, Excel).
    - Métricas y estadísticas detalladas.
"""

import sys
import logging
import json
import argparse

from colorama import Fore, Style, init
from typing import Dict, List

# Configuración de colorama
init(autoreset=True)

# Importaciones internas
from src.utils.logger import setup_logger
from src.utils.helpers import validate_url, create_directory_structure
from src.coordinator.scraping_coordinator import ScrapingCoordinator


def _emit_products_for_java(coordinator: ScrapingCoordinator):
    """Imprime cada producto en una sola línea JSON para que Java lo parsee.

    DataManager.java busca líneas con 'title' y 'price_sell';
    por eso emitimos un json.dumps por producto. No cambia la salida
    interactiva.
    """
    try:
        for task_result in coordinator.results:
            data = task_result.get('data') if isinstance(task_result, dict) else None
            if not data:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                print(json.dumps(item, ensure_ascii=False))
    except Exception as e:
        print(f"[WARN] No se pudo emitir productos para Java: {e}")


def _run_java_bridge(args: argparse.Namespace):
    """Modo no interactivo para la app Java (sin prompts)."""
    setup_logger(LOGGER_CONFIG)
    create_directory_structure()

    tienda = (args.tienda or "").lower()
    if tienda not in ("mercadolibre", "alkosto"):
        raise ValueError("Tienda debe ser 'mercadolibre' o 'alkosto'")

    task = {
        'url': (f"https://listado.mercadolibre.com.co/{args.producto.replace(' ', '-')}")
               if tienda == 'mercadolibre'
               else f"https://www.alkosto.com/search?text={args.producto.replace(' ', '%20')}",
        'type': 'dynamic',
        'subtype': 'e-commerce',
        'tienda': tienda,
        'num_productos': args.items,
        'max_paginas': args.paginas,
        'priority': 3,
    }

    coordinator = ScrapingCoordinator(
        tasks=[task],
        max_workers=1,
        delay_between_requests=1.0,
        max_retries=2,
        enable_cache=False,
        show_progress=False,
        respect_robots_txt=False,
    )

    result = coordinator.run()
    _emit_products_for_java(coordinator)

    if args.export:
        coordinator.export_results(format='json')

    return result


LOGGER_CONFIG = {
    'name': 'ScrapingSystem',
    'level': 'DEBUG',
    'log_dir': 'logs',
    'enable_console': True
}

class TerminalInterface:
    """Clase para manejar la interfaz de terminal"""
    
    @staticmethod
    def show_header():
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{'SCDATAEXTRACTOR - SCRAPING':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
    
    @staticmethod
    def show_menu() -> int:
        print(f"{Fore.YELLOW}Seleccione modo de operación:{Style.RESET_ALL}")
        print(" 1. Scraping interactivo (una tarea)")
        print(" 2. Scraping por lotes (múltiples tareas)")
        print(" 3. Cargar tareas desde archivo JSON")
        print(" 4. Ver estadísticas de sesión anterior")
        print(" 5. Reintentar tareas fallidas")
        print(" 6. Limpiar caché")
        print(" 7. Salir")
        return int(input("\nIngrese su opción: "))

    @staticmethod
    def get_coordinator_config() -> Dict:
        print(f"\n{Fore.YELLOW}Configuración del Coordinator:{Style.RESET_ALL}")
        config = {}
        config['max_workers'] = int(input("Número de workers paralelos (1-10) [3]: ") or "3")
        config['delay_between_requests'] = float(input("Delay entre requests en segundos [1.0]: ") or "1.0")
        config['max_retries'] = int(input("Máximo de reintentos [3]: ") or "3")
        config['enable_cache'] = input("¿Habilitar caché? (S/n) [S]: ").lower() != 'n'
        config['show_progress'] = input("¿Mostrar barra de progreso? (S/n) [S]: ").lower() != 'n'
        config['respect_robots_txt'] = input("¿Respetar robots.txt? (s/N) [N]: ").lower() == 's'
        return config

    @staticmethod
    def get_url() -> str:
        while True:
            url = input("\nIngrese la URL a scrapear: ").strip()
            if validate_url(url):
                return url
            print(f"{Fore.RED}URL inválida! Intente nuevamente.{Style.RESET_ALL}")

    @staticmethod
    def get_dynamic_params() -> Dict:
        params = {}
        print(f"\n{Fore.YELLOW}Configuración de scraping dinámico:{Style.RESET_ALL}")
        params['num_productos'] = int(input("Cantidad de items a extraer: "))
        params['max_paginas'] = int(input("Máximo de páginas a recorrer [1]: ") or "1")
        params['priority'] = int(input("Prioridad de la tarea (1=alta, 5=baja) [3]: ") or "3")
        print(f"\n{Fore.CYAN}💡 Nota: Cada página tiene ~48 productos. Para {params['num_productos']} productos se recomienda {(params['num_productos'] // 48) + 1} página(s).{Style.RESET_ALL}")
        return params

    @staticmethod
    def create_task_interactive() -> Dict:
        """Crea una tarea de forma interactiva"""
        print(f"\n{Fore.CYAN}=== Creación de Tarea ==={Style.RESET_ALL}")
        
        ecom_params = TerminalInterface.get_ecommerce_params()
        dynamic_params = TerminalInterface.get_dynamic_params()
        
        task = {
            'url': ecom_params['url'],
            'type': 'dynamic',
            'subtype': 'e-commerce',
            'tienda': 'mercadolibre' if 'mercadolibre' in ecom_params['url'] else 'alkosto',
            'num_productos': dynamic_params['num_productos'],
            'max_paginas': dynamic_params.get('max_paginas', 1),
            'priority': dynamic_params['priority']
        }
        
        return task
    
    @staticmethod
    def create_multiple_tasks() -> List[Dict]:
        """Crea múltiples tareas de forma interactiva"""
        tasks = []
        num_tasks = int(input(f"\n{Fore.YELLOW}¿Cuántas tareas desea crear? {Style.RESET_ALL}"))
        
        for i in range(num_tasks):
            print(f"\n{Fore.CYAN}--- Tarea {i+1}/{num_tasks} ---{Style.RESET_ALL}")
            task = TerminalInterface.create_task_interactive()
            tasks.append(task)
            print(f"{Fore.GREEN}✓ Tarea agregada{Style.RESET_ALL}")
        
        return tasks
    
    @staticmethod
    def load_tasks_from_file() -> List[Dict]:
        """Carga tareas desde un archivo JSON"""
        filepath = input(f"\n{Fore.YELLOW}Ruta del archivo JSON: {Style.RESET_ALL}").strip()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            print(f"{Fore.GREEN}✓ Cargadas {len(tasks)} tareas desde {filepath}{Style.RESET_ALL}")
            return tasks
        except FileNotFoundError:
            print(f"{Fore.RED}✗ Archivo no encontrado{Style.RESET_ALL}")
            return []
        except json.JSONDecodeError:
            print(f"{Fore.RED}✗ Error al parsear JSON{Style.RESET_ALL}")
            return []

    @staticmethod
    def show_progress(message: str):
        print(f"{Fore.GREEN}[PROGRESO]{Style.RESET_ALL} {message}")

    @staticmethod
    def show_error(message: str):
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def show_statistics(stats: Dict):
        """Muestra estadísticas de forma elegante"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{'ESTADÍSTICAS DE SCRAPING':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Resumen:{Style.RESET_ALL}")
        print(f"  Total de tareas: {stats.get('total_tasks', 0)}")
        print(f"  Exitosas: {Fore.GREEN}{stats.get('success', 0)}{Style.RESET_ALL}")
        print(f"  Fallidas: {Fore.RED}{stats.get('failed', 0)}{Style.RESET_ALL}")
        print(f"  Duración total: {stats.get('total_duration', 'N/A')}")
        
        print(f"\n{Fore.YELLOW}Métricas:{Style.RESET_ALL}")
        print(f"  Duración promedio: {stats.get('avg_task_duration', 'N/A')}")
        print(f"  Tarea más rápida: {stats.get('min_task_duration', 'N/A')}")
        print(f"  Tarea más lenta: {stats.get('max_task_duration', 'N/A')}")
        
        if 'cache_hit_rate' in stats:
            print(f"\n{Fore.YELLOW}Caché:{Style.RESET_ALL}")
            print(f"  Hit rate: {stats['cache_hit_rate']}")
            print(f"  Tamaño: {stats.get('cache_size', 0)} entradas")
            
            # Mostrar información detallada del caché si está disponible
            cache_info = stats.get('cache_info', {})
            if cache_info:
                print(f"  Archivo: {cache_info.get('cache_file', 'N/A')}")
                print(f"  Tamaño en disco: {cache_info.get('disk_size_mb', 0)} MB")
                print(f"  Capacidad máxima: {cache_info.get('max_size', 0)} entradas")
        
        agg_metrics = stats.get('aggregated_metrics', {})
        if agg_metrics:
            print(f"\n{Fore.YELLOW}Métricas agregadas:{Style.RESET_ALL}")
            print(f"  Memoria usada: {agg_metrics.get('memory_usage_mb', 0):.2f} MB")
            fastest = agg_metrics.get('fastest_task')
            if isinstance(fastest, dict) and 'duration' in fastest:
                url_snippet = fastest.get('url', '')[:50]
                print(f"  Tarea más rápida: {fastest['duration']:.3f}s ({url_snippet})")
            elif isinstance(fastest, (int, float)):
                print(f"  Tarea más rápida: {fastest:.3f}s")

            slowest = agg_metrics.get('slowest_task')
            if isinstance(slowest, dict) and 'duration' in slowest:
                url_snippet = slowest.get('url', '')[:50]
                print(f"  Tarea más lenta: {slowest['duration']:.3f}s ({url_snippet})")
            elif isinstance(slowest, (int, float)):
                print(f"  Tarea más lenta: {slowest:.3f}s")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

    @staticmethod
    def get_ecommerce_params() -> Dict:
        print(f"\n{Fore.YELLOW}Seleccione tienda:{Style.RESET_ALL}")
        print("1. MercadoLibre")
        print("2. Alkosto")
        
        try:
            tienda = int(input("Opción: "))
            producto = input("Producto a buscar (ej: Computador, Lavadora): ").strip().lower()
            
            if tienda == 1:
                # URL corregida: MercadoLibre usa guiones para separar palabras
                return {
                    'url': f"https://listado.mercadolibre.com.co/{producto.replace(' ', '-')}"
                }
            elif tienda == 2:
                return {
                    'url': f"https://www.alkosto.com/search?text={producto.replace(' ', '%20')}"
                }
            else:
                raise ValueError("Opción inválida")
                
        except ValueError as e:
            raise ValueError(f"Error en selección de tienda: {str(e)}")

def main():
    setup_logger(LOGGER_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Iniciando configuración del sistema")

    TerminalInterface.show_header()
    create_directory_structure()
    
    # Variable global para mantener el último coordinator
    last_coordinator = None
    
    try:
        while True:
            choice = TerminalInterface.show_menu()
            
            if choice == 7:
                print(f"\n{Fore.CYAN}Gracias por usar el sistema!{Style.RESET_ALL}")
                sys.exit(0)
            
            # Opción 6: Limpiar caché
            elif choice == 6:
                from pathlib import Path
                cache_file = Path('cache') / 'scraping_cache.pkl'
                
                if cache_file.exists():
                    confirm = input(f"\n{Fore.YELLOW}¿Está seguro de limpiar el caché? (S/n): {Style.RESET_ALL}").lower()
                    if confirm != 'n':
                        cache_file.unlink()
                        print(f"{Fore.GREEN}✓ Caché limpiado exitosamente{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Operación cancelada{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No existe archivo de caché{Style.RESET_ALL}")
                continue
                
            try:
                # Opción 1: Scraping interactivo
                if choice == 1:
                    config = TerminalInterface.get_coordinator_config()
                    task = TerminalInterface.create_task_interactive()
                    
                    TerminalInterface.show_progress("Iniciando ScrapingCoordinator...")
                    
                    coordinator = ScrapingCoordinator(
                        tasks=[task],
                        max_workers=config['max_workers'],
                        delay_between_requests=config['delay_between_requests'],
                        max_retries=config['max_retries'],
                        enable_cache=config['enable_cache'],
                        show_progress=config['show_progress'],
                        respect_robots_txt=config['respect_robots_txt']
                    )
                    
                    result = coordinator.run()
                    last_coordinator = coordinator

                    # Emitir productos en stdout para consumo de la app Java
                    _emit_products_for_java(coordinator)
                    
                    # Mostrar estadísticas
                    TerminalInterface.show_statistics(result['statistics'])
                    
                    # Opción de exportar
                    if input(f"\n{Fore.YELLOW}¿Exportar resultados? (S/n): {Style.RESET_ALL}").lower() != 'n':
                        export_format = input("Formato (json/csv/excel) [json]: ").strip().lower() or 'json'
                        filepath = coordinator.export_results(format=export_format)
                        print(f"{Fore.GREEN}[ÉXITO]{Style.RESET_ALL} Archivo exportado: {Fore.CYAN}{filepath}{Style.RESET_ALL}")
                
                # Opción 2: Scraping por lotes
                elif choice == 2:
                    config = TerminalInterface.get_coordinator_config()
                    tasks = TerminalInterface.create_multiple_tasks()
                    
                    if not tasks:
                        TerminalInterface.show_error("No se crearon tareas")
                        continue
                    
                    TerminalInterface.show_progress("Iniciando ScrapingCoordinator...")
                    
                    coordinator = ScrapingCoordinator(
                        tasks=tasks,
                        max_workers=config['max_workers'],
                        delay_between_requests=config['delay_between_requests'],
                        max_retries=config['max_retries'],
                        enable_cache=config['enable_cache'],
                        show_progress=config['show_progress'],
                        respect_robots_txt=config['respect_robots_txt']
                    )
                    
                    result = coordinator.run()
                    last_coordinator = coordinator

                    # Emitir productos en stdout para consumo de la app Java
                    _emit_products_for_java(coordinator)
                    
                    TerminalInterface.show_statistics(result['statistics'])
                    
                    # Mostrar tareas fallidas
                    failed = coordinator.get_failed_tasks()
                    if failed:
                        print(f"\n{Fore.RED}Tareas fallidas: {len(failed)}{Style.RESET_ALL}")
                        for i, f in enumerate(failed[:5], 1):
                            print(f"  {i}. {f.get('url', 'N/A')} - {f.get('error', 'Error desconocido')}")
                    
                    if input(f"\n{Fore.YELLOW}¿Exportar resultados? (S/n): {Style.RESET_ALL}").lower() != 'n':
                        export_format = input("Formato (json/csv/excel) [json]: ").strip().lower() or 'json'
                        filepath = coordinator.export_results(format=export_format)
                        print(f"{Fore.GREEN}[ÉXITO]{Style.RESET_ALL} Archivo exportado: {Fore.CYAN}{filepath}{Style.RESET_ALL}")
                
                # Opción 3: Cargar desde archivo
                elif choice == 3:
                    tasks = TerminalInterface.load_tasks_from_file()
                    
                    if not tasks:
                        continue
                    
                    config = TerminalInterface.get_coordinator_config()
                    
                    coordinator = ScrapingCoordinator(
                        tasks=tasks,
                        max_workers=config['max_workers'],
                        delay_between_requests=config['delay_between_requests'],
                        max_retries=config['max_retries'],
                        enable_cache=config['enable_cache'],
                        show_progress=config['show_progress'],
                        respect_robots_txt=config['respect_robots_txt']
                    )
                    
                    result = coordinator.run()
                    last_coordinator = coordinator

                    # Emitir productos en stdout para consumo de la app Java
                    _emit_products_for_java(coordinator)
                    
                    TerminalInterface.show_statistics(result['statistics'])
                    
                    if input(f"\n{Fore.YELLOW}¿Exportar resultados? (S/n): {Style.RESET_ALL}").lower() != 'n':
                        export_format = input("Formato (json/csv/excel) [json]: ").strip().lower() or 'json'
                        filepath = coordinator.export_results(format=export_format)
                        print(f"{Fore.GREEN}[ÉXITO]{Style.RESET_ALL} Archivo exportado: {Fore.CYAN}{filepath}{Style.RESET_ALL}")
                
                # Opción 4: Ver estadísticas anteriores
                elif choice == 4:
                    if last_coordinator:
                        stats = {
                            'total_tasks': len(last_coordinator.results),
                            'success': len(last_coordinator.get_successful_tasks()),
                            'failed': len(last_coordinator.get_failed_tasks()),
                            'cache_size': last_coordinator._cache.size(),
                            'aggregated_metrics': last_coordinator.metrics
                        }
                        TerminalInterface.show_statistics(stats)
                        
                        # Mostrar estado del circuit breaker
                        cb_status = last_coordinator.get_circuit_breaker_status()
                        if cb_status:
                            print(f"\n{Fore.YELLOW}Circuit Breaker Status:{Style.RESET_ALL}")
                            for url, count in cb_status.items():
                                print(f"  {url[:50]}... → {count} fallos")
                    else:
                        TerminalInterface.show_error("No hay sesión anterior")
                
                # Opción 5: Reintentar tareas fallidas
                elif choice == 5:
                    if last_coordinator and last_coordinator.get_failed_tasks():
                        TerminalInterface.show_progress("Reintentando tareas fallidas...")
                        result = last_coordinator.retry_failed_tasks()
                        _emit_products_for_java(last_coordinator)
                        TerminalInterface.show_statistics(result['statistics'])
                    else:
                        TerminalInterface.show_error("No hay tareas fallidas para reintentar")
                
                else:
                    TerminalInterface.show_error("Opción inválida!")
                    continue
                    
            except ValueError as e:
                TerminalInterface.show_error(f"Error de configuración: {str(e)}")
            except KeyError as e:
                TerminalInterface.show_error(f"Campo faltante: {str(e)}")
            except Exception as e:
                logger.error(f"Error durante scraping: {str(e)}", exc_info=True)
                TerminalInterface.show_error(f"Error en el proceso: {str(e)}")

            input("\nPresione Enter para continuar...")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Proceso interrumpido por el usuario.{Style.RESET_ALL}")
        if last_coordinator:
            last_coordinator.cleanup()
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}", exc_info=True)
        TerminalInterface.show_error(f"Error fatal: {str(e)}")
        sys.exit(1)
    finally:
        if last_coordinator:
            last_coordinator.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCDATAEXTRACTOR")
    parser.add_argument("--java-bridge", action="store_true", help="Ejecuta sin prompts para la app Java")
    parser.add_argument("--tienda", type=str, help="mercadolibre | alkosto")
    parser.add_argument("--producto", type=str, help="Texto de búsqueda")
    parser.add_argument("--items", type=int, default=10, help="Número de productos a extraer")
    parser.add_argument("--paginas", type=int, default=1, help="Número máximo de páginas")
    parser.add_argument("--export", action="store_true", help="Exportar JSON en outputs/exports")

    args, unknown = parser.parse_known_args()

    if args.java_bridge:
        _run_java_bridge(args)
        sys.exit(0)

    main()