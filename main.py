"""
Archivo: main.py
Descripción:
    Punto de entrada principal del scraper.
    
    Funcionalidades:
    - Configuración del sistema de logging.
    - Definición de tareas de scraping (por ejemplo, URLs estáticas
    y dinámicas).
    - Ejecución del proceso de scraping utilizando ScrapingCoordinator.
    - Manejo y almacenamiento de datos extraídos mediante DataHandler.
    - Generación opcional de reportes.
"""

import sys
import logging

from colorama import Fore, Style, init
from typing import Dict

# Configuración de colorama
init(autoreset=True)

# Importaciones internas
from src.utils.logger import setup_logger
from src.utils.helpers import validate_url, create_directory_structure
from src.coordinator.scraping_coordinator import ScrapingCoordinator
from src.components.data_handler import DataHandler
from src.components.static_page_extractor import StaticPageExtractor
from src.components.dynamic.real_state_extractor import RealEstateExtractor
from src.components.dynamic.ecommerce_extractor import EcommerceExtractor


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
        print(f"{'WEB SCRAPING AUTOMATIZADO':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
    
    @staticmethod
    def show_menu() -> int:
        print(f"{Fore.YELLOW}Seleccione el tipo de scraping:{Style.RESET_ALL}")
        print(" 1. Páginas estáticas (Wikipedia, blogs, documentación)")
        print(" 2. E-commerce (Productos, tiendas online)...")
        print(" 3. Bienes raíces (Propiedades, inmuebles)...")
        print(" 4. ¿Ya te vas? - Salir")
        return int(input("\nIngrese su opción: "))

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
        params['max_paginas'] = int(input("Máximo de páginas a recorrer: "))
        return params

    @staticmethod
    def show_progress(message: str):
        print(f"{Fore.GREEN}[PROGRESO]{Style.RESET_ALL} {message}")

    @staticmethod
    def show_error(message: str):
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")
    
    @staticmethod
    def get_static_query() -> str:
        print(f"\n{Fore.YELLOW}Seleccione sitio para scraping estático:{Style.RESET_ALL}")
        print("1. Wikipedia")
        print("2. Fandom (Wikis)")
        opcion = int(input("Opción: "))
        
        if opcion == 1:
            query = input("Ingrese término a buscar en Wikipedia (ej: Python): ").strip()
            return f"https://es.wikipedia.org/wiki/{query.replace(' ', '_')}"
        elif opcion == 2:
            wiki_name = input("Nombre del Wiki (ej: harrypotter, leagueoflegends): ").strip()
            article = input("Artículo a buscar (ej: Harry_Potter, Arcane_(serie_de_televisión)): ").strip()
            return f"https://{wiki_name}.fandom.com/es/wiki/{article}"
        else:
            raise ValueError("Opción inválida")

    @staticmethod
    def get_ecommerce_params() -> Dict:
        print(f"\n{Fore.YELLOW}Seleccione tienda:{Style.RESET_ALL}")
        print("1. MercadoLibre")
        print("2. Alkosto")
        
        try:
            tienda = int(input("Opción: "))
            producto = input("Producto a buscar (ej: Computador, Lavadora): ").strip().lower()
            
            if tienda == 1:
                # URL corregida usando formato actual de MercadoLibre
                return {
                    'url': f"https://listado.mercadolibre.com.co/{producto.replace(' ', '-')}_Desde_1"
                }
            elif tienda == 2:
                return {
                    'url': f"https://www.alkosto.com/search?text={producto.replace(' ', '%20')}"
                }
            else:
                raise ValueError("Opción inválida")
                
        except ValueError as e:
            raise ValueError(f"Error en selección de tienda: {str(e)}")

    @staticmethod
    def get_metrocuadrado_params() -> Dict:
        ciudades = {
            1: ('bogota', {
                1: 'teusaquillo',
                2: 'chapinero',
                3: 'usaquen',
                4: 'engativa',
                5: 'kennedy',
                6: 'bosa',
                7: 'fontibon',
                8: 'suba',
                9: 'tunjuelito',
                10: 'santafe',
                11: 'antonio narino'
            }),
            2: ('medellin', {
                1: 'el-poblado',
                2: 'laureles'
            })
        }
        
        print(f"\n{Fore.YELLOW}Seleccione ciudad:{Style.RESET_ALL}")
        for idx in ciudades:
            print(f"{idx}. {ciudades[idx][0].capitalize()}")
        ciudad_op = int(input("Opción: "))
        
        ciudad_data = ciudades.get(ciudad_op)
        if not ciudad_data:
            raise ValueError("Ciudad inválida")
        
        print(f"\nLocalidades disponibles para {ciudad_data[0].capitalize()}:")
        for idx in ciudad_data[1]:
            print(f"{idx}. {ciudad_data[1][idx].capitalize()}")
        localidad_op = int(input("Opción: "))
        localidad = ciudad_data[1].get(localidad_op)
        
        tipos = {
            1: 'apartaestudio',
            2: 'apartamentos',
            3: 'casas',
            4: 'oficinas',
            5: 'locales'
        }
        print(f"\n{Fore.YELLOW}Seleccione tipos de propiedad (separados por coma):{Style.RESET_ALL}")
        for idx in tipos:
            print(f"{idx}. {tipos[idx].capitalize()}")
        seleccion = input("Opciones: ").split(',')
        
        tipos_seleccionados = [tipos[int(s.strip())] for s in seleccion]
        tipos_query = '-'.join(tipos_seleccionados)
        
        return {
            'url': f"https://www.metrocuadrado.com/{tipos_query}/venta/{ciudad_data[0]}/{localidad}/?search=form",
            'localidad': localidad,
            'ciudad': ciudad_data[0],
            'tipos': tipos_seleccionados
        }

def main():
    setup_logger(LOGGER_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Iniciando configuración del sistema")

    TerminalInterface.show_header()
    create_directory_structure()
    
    try:
        while True:
            choice = TerminalInterface.show_menu()
            
            if choice == 4:
                print(f"\n{Fore.CYAN}Gracias por usar el sistema!{Style.RESET_ALL}")
                sys.exit(0)
                
            try:
                # Configuración base de la tarea
                task = {
                    'type': 'dynamic' if choice in [2, 3] else 'static',
                    'subtype': ['e-commerce', 'real_state'][choice - 2] if choice in [2, 3] else None
                }

                # Configuración específica por tipo
                if choice == 1:
                    task['url'] = TerminalInterface.get_static_query()
                    task['subtype'] = 'static'
                elif choice == 2:
                    ecom_params = TerminalInterface.get_ecommerce_params()
                    task.update({
                        'url': ecom_params['url'],
                        'subtype': 'e-commerce',
                        'tienda': 'mercadolibre' if 'mercadolibre' in ecom_params['url'] else 'alkosto'
                    })
                elif choice == 3:
                    real_state_params = TerminalInterface.get_metrocuadrado_params()
                    task.update({
                        'url': real_state_params.pop('url'),  # Extraer URL y remover de params
                        'params': real_state_params  # Ahora solo contiene localidad, ciudad, tipos
                    })
                else:
                    TerminalInterface.show_error("Opción inválida!")
                    continue

                # Configuración dinámica común
                if choice in [2, 3]:
                    dynamic_params = TerminalInterface.get_dynamic_params()
                    task.update(dynamic_params)
                    task['num_productos'] = dynamic_params['num_productos']

                # Validación final de campos requeridos
                required_fields = {
                    'static': ['type', 'url'],
                    'dynamic': ['type', 'subtype', 'url', 'num_productos']
                }
                missing = [field for field in required_fields[task['type']] if field not in task]
                if missing:
                    raise ValueError(f"Faltan campos obligatorios: {missing}")

                # Ejecución del scraping
                TerminalInterface.show_progress("Iniciando proceso de scraping...")

                if task['type'] == 'static':
                    # Lógica para scraping estático
                    scraper = StaticPageExtractor(task['url'])
                    html_content = scraper.download()
                    
                    if html_content:
                        data = scraper.parse()
                        if scraper.store():
                            TerminalInterface.show_progress("Datos almacenados en: outputs/static/")
                            
                        if input("\n¿Generar reporte? (S/n): ").lower() == 's':
                            report_path = DataHandler([data]).generate_report()
                            if report_path:
                                TerminalInterface.show_progress(f"Reporte generado: {report_path}")

                else:
                    # Lógica para scraping dinámico (e-commerce y real_state)
                    if task['subtype'] == 'e-commerce':
                        extractor = EcommerceExtractor(
                            task['url'], 
                            task['tienda'], 
                            task['num_productos']
                        )
                    elif task['subtype'] == 'real_state':
                        real_state_params = task['params'].copy()
                        real_state_url = real_state_params.pop('url', task['url'])
                        extractor = RealEstateExtractor(
                            url=real_state_url,
                            tienda="metrocuadrado",
                            num_productos=task['num_productos'],
                            **real_state_params
                        )
                    
                    if html_content := extractor.download():
                        productos = extractor.parse(html_content)
                        if extractor.store():
                            TerminalInterface.show_progress(f"Datos almacenados en: outputs/{task['subtype']}/")
                        
                        if input("\n¿Generar reporte? (S/n): ").lower() == 's':
                            report_path = DataHandler(productos).generate_report()
                            if report_path:
                                TerminalInterface.show_progress(f"Reporte generado: {report_path}")

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
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}", exc_info=True)
        TerminalInterface.show_error(f"Error fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()