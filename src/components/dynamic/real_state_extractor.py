"""
- Módulo logging:
Permite implementar un sistema de registro flexible para rastrear
eventos dentro de aplicaciones y bibliotecas.
Fuente: https://realpython.com/python-logging/

- Módulo random:
Se usa para elegir entre números aleatorios.
Fuente: https://www.w3schools.com/python/module_random.asp

- Módulo re:
Este módulo contiene funciones y expresiones regulares que pueden ser 
usadas para buscar patrones dentro de cadenas de texto.
Fuente: https://docs.python.org/es/3.13/library/re.html

- Módulo time:
Proporciona varias funciones para manejar tareas relacionadas con 
el tiempo.
Fuente: https://docs.python.org/es/3.10/library/time.html

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

- Módulo BeautifulSoup:
Para extraer datos de archivos HTML y XML.
Fuente: 
https://datascientest.com/es/beautiful-soup-aprender-web-scraping
"""

import logging
import random
import re
import time

from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Union
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .dynamic_page_extractor import DynamicPageExtractor
from src.components.data_handler import DataHandler
from src.config import SELECTORES_LISTA_DINAMICOS, USER_AGENT_DINAMICOS
from src.utils.logger import get_logger
from src.utils.helpers import validate_url, clean_filename, generate_hash, create_directory_structure

class RealEstateExtractor(DynamicPageExtractor):
    def __init__(self, url: str, tienda: str = "metrocuadrado", num_productos: int = 1, **params):
        super().__init__(url, tienda, num_productos)
        self.params = params
        self.logger = get_logger(self.__class__.__name__)
        create_directory_structure()
        
        self.driver = None
        self.ubicacion = self.extraer_ubicacion_url()
        self.user_agent = random.choice(USER_AGENT_DINAMICOS)
        self.html_content = ""
        
        logging.getLogger("selenium").setLevel(logging.WARNING)
        logging.getLogger("bs4").setLevel(logging.INFO)

    def extraer_ubicacion_url(self) -> str:
        match = re.search(r"/venta/[^/]+/([^/]+)/", self.url.lower())
        return match.group(1).title() if match else ""

    def configurar_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-agent={self.user_agent}")
        # options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(options=options)

    def download(self) -> str:
        try:
            self.driver = self.configurar_driver()
            self.driver.get("https://www.metrocuadrado.com/buscar/")
            
            self.manejar_popups()
            self.configurar_tipo_negocio()
            self.configurar_ubicacion_exacta()
            self.configurar_tipo_inmueble()
            self.ejecutar_busqueda()
            
            propiedades_unicas = []
            pagina_actual = 1
            
            while len(propiedades_unicas) < self.num_productos:
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 
                                                        "li.sc-gPEVay")))
                    
                    # Parsear y filtrar
                    html_page = self.driver.page_source
                    nuevas_props = self.parse(html_page)
                    
                    # Filtrado de duplicados
                    nuevas_props_filtradas = [
                        p for p in nuevas_props 
                        if p['url'] not in {x['url'] for x in propiedades_unicas}
                    ]
                    
                    # Añadir hasta completar el número requerido
                    for prop in nuevas_props_filtradas:
                        if len(propiedades_unicas) >= self.num_productos:
                            break
                        propiedades_unicas.append(prop)
                    
                    # Paginación
                    if len(propiedades_unicas) < self.num_productos:
                        if not self.ir_pagina_siguiente(pagina_actual):
                            break
                        pagina_actual += 1
                        time.sleep(2)
                
                except Exception as e:
                    self.logger.error("Error en página "
                                    f"{pagina_actual}: {str(e)}")
                    break
            
            self.html_content = self.driver.page_source
            self.data = propiedades_unicas[:self.num_productos]
            return self.html_content
            
        except Exception as e:
            self.logger.error(f"Error crítico: {str(e)}", exc_info=True)
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def manejar_popups(self):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                                            "button#accept-cookies"))
            ).click()
            time.sleep(0.5)
        except Exception:
            pass

    def configurar_tipo_negocio(self):
        try:
            dropdown = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                                            "div#businessType"))
            )
            dropdown.click()
            time.sleep(1)
            
            opcion = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'Compra Nuevo y Usado')]")
                )
            )
            opcion.click()
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Error configurando tipo de negocio: {str(e)}")
            raise

    def configurar_ubicacion_exacta(self):
        try:
            input_loc = WebDriverWait(self.driver, 25).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                                            'input[name="location"]')))
            
            self.driver.execute_script("arguments[0].value = '';", 
                                    input_loc)
            input_loc.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
            time.sleep(0.5)
            
            ubicacion = self.params.get('localidad', '')
            if not ubicacion:
                raise ValueError("Parámetro 'localidad' requerido")
                
            ActionChains(self.driver)\
                .send_keys_to_element(input_loc, ubicacion)\
                .pause(1)\
                .perform()
            
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.react-autosuggest__suggestions-container li:first-child")
                )
            ).click()
            time.sleep(1)
            
        except TimeoutException:
            self.logger.error("No aparecieron sugerencias de ubicación")
            raise
        except Exception as e:
            self.logger.error(f"Error configurando ubicación: {str(e)}")
            raise
    
    def configurar_tipo_inmueble(self):
        """Selecciona tipos de inmueble en el dropdown"""
        if not self.params.get('tipos'):
            return

        try:
            self.logger.info("Configurando tipos de inmueble...")
            
            # 1. Localizar y hacer clic en el dropdown
            dropdown = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='propertyTypes' or contains(@class, 'm2-select__control')]"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown)
            dropdown.click()
            time.sleep(1)
            
            # 2. Esperar carga de opciones
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'm2-select__option')]"))
            )
            
            # 3. Selección robusta de opciones
            for tipo in self.params['tipos']:
                # XPath insensible a mayúsculas y espacios
                xpath = f"""
                //div[contains(@class, 'm2-select__option') 
                    and translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ', 'abcdefghijklmnopqrstuvwxyzáéíóú') 
                    = '{tipo.lower().strip()}']
                """
                option = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, xpath)))
                
                # Click con JavaScript para evitar problemas de visibilidad
                self.driver.execute_script("arguments[0].click();", option)
                self.logger.debug(f"Tipo seleccionado: {tipo}")
                time.sleep(0.5)
            
            # 4. Cerrar dropdown
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
            
        except Exception as e:
            self.logger.error(f"Error en selección de tipos: {str(e)}")
            self.driver.save_screenshot("logs/error_tipos_inmueble.png")
            raise
            
        except Exception as e:
            self.logger.error(f"Error seleccionando tipos: {str(e)}")
            self.driver.save_screenshot("logs/error_tipos_inmueble.png")
            raise

    def ejecutar_busqueda(self):
        btn = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.ID, "btnSearch"))
        )
        btn.click()
        time.sleep(2)

    def parse(self, html_content: str) -> list:
        self.logger.info("Iniciando parseo de propiedades")
        propiedades = []
        urls_vistas = set()  # Nuevo: Rastrear URLs únicas
        soup = BeautifulSoup(html_content, 'html.parser')
        
        config = SELECTORES_LISTA_DINAMICOS[self.tienda]['propiedad']
        
        # Obtener TODOS los listados primero
        todos_listados = [
            item for item in soup.find_all(config['tag'], class_=config['class'])
            if item.find("h2", class_="sc-dxgOiQ")
        ]
        
        self.logger.debug(f"Total de listados crudos: {len(todos_listados)}")
        
        for prop in todos_listados:
            if len(propiedades) >= self.num_productos:
                break 
                
            try:
                url = self.extraer_url(prop, config['children']['url'])
                
                # Filtro clave: Saltar duplicados
                if not url or url in urls_vistas:
                    continue
                    
                urls_vistas.add(url)
                
                titulo = self.extraer_titulo(prop, config['children']['title'])
                precio_extraido = self.extraer_precio(prop, config['children']['price'])
                precio_formateado = self.formatear_precio(precio_extraido)
                area = self.extraer_cardblock(prop, config['children']['area'])
                hab = self.extraer_cardblock(prop, config['children']['rooms'])
                ban = self.extraer_cardblock(prop, config['children']['baths'])
                
                datos = {
                    "title": titulo,
                    "price": f"$ {precio_formateado}", 
                    "area": area,
                    "rooms": hab,
                    "baths": ban, 
                    "url": url,
                }

                if self.es_duplicado(datos, propiedades):
                    continue  # Saltar duplicado por contenido
                
                propiedades.append(datos)
                
            except Exception as e:
                self.logger.error(f"Error procesando propiedad: {str(e)}")
                continue
        
        self.data = propiedades
        self.logger.info(f"Parseo completado. {len(propiedades)} propiedades únicas")
        return propiedades
    
    def es_duplicado(self, datos_propiedad: dict, propiedades: list) -> bool:
        clave_unica = (
            datos_propiedad['title'],
            datos_propiedad['price'],
            datos_propiedad['area']
        )
        
        for prop_existente in propiedades:
            existente_unica = (
                prop_existente['title'],
                prop_existente['price'],
                prop_existente['area']
            )
            if clave_unica == existente_unica:
                return True
        return False
    
    def buscar_contexto(self, elemento, texto_padre):
        for li in elemento.find_all("li"):
            li_text = li.get_text(strip=True)
            if texto_padre.lower() in li_text.lower():
                return li
        return None

    def extraer_titulo(self, elemento: Tag, selector: Dict) -> str:
        candidatos = elemento.find_all(selector["tag"], class_=selector.get("class"))
        if not candidatos:
            return ""
            
        elemento_padre = candidatos[0]
        
        if "sub_element" in selector:
            sub_tag = selector["sub_element"]["tag"]
            sub_element = elemento_padre.find(sub_tag, class_=selector["sub_element"].get("class"))
            return sub_element.get_text(strip=True) if sub_element else elemento_padre.get_text(strip=True)
        
        return elemento_padre.get_text(strip=True)
    
    def extraer_precio(self, elemento: Tag, selector: Dict) -> str:
        card_block = elemento.find("div", class_="card-block")
        contexto = self.buscar_contexto(card_block or elemento, selector['contexto']['texto_padre'])
        if not contexto:
            return ""
        
        precio = contexto.find(selector['sub_element']['tag'], class_=selector['sub_element']['class'])
        return re.sub(r"[^\d]", "", precio.text) if precio else ""

    def formatear_precio(self, precio_str: str) -> str:
        try:
            return "{:,.0f}".format(int(precio_str)).replace(",", ".")
        except ValueError:
            return precio_str
        
    def extraer_cardblock(self, elemento: Tag, selector: Dict) -> str:    
        card_block = elemento.find("div", class_="card-block")
        contexto = self.buscar_contexto(card_block or elemento, selector['contexto']['texto_padre'])
        if not contexto:
            return ""
        
        elemento = contexto.find(selector['sub_element']['tag'], class_=selector['sub_element']['class'])
        return elemento.get_text(strip=True) if elemento else ""
        
    def extraer_url(self, elemento: Tag, selector: Dict) -> str:
        try:
            base_url = "https://www.metrocuadrado.com"
            padre = elemento
            
            if "padre" in selector:
                padre = elemento.find(
                    selector["padre"]["tag"], 
                    class_=selector["padre"].get("class")
                ) or elemento

            a_elem = padre.find(selector["tag"], class_=selector.get("class"))
            if not a_elem:
                return ""

            url_relativa = a_elem.get(selector.get("attr", "href"), "")
            url_absoluta = urljoin(base_url, url_relativa)
            return url_absoluta if validate_url(url_absoluta) else ""
        except Exception as e:
            self.logger.error(f"Error extrayendo URL: {str(e)}")
            return ""
    
    def store(self) -> bool:
        try:
            if not self.data:
                self.logger.warning("Sin datos para almacenar")
                return False
            
            handler = DataHandler(
                self.data, 
                storage_format='both',
                logger=self.logger
            )
            return handler.store_data(
                url=self.url,
                tipo="real_state"  # Eliminar el parámetro custom_name
            )
        except Exception as e:
            self.logger.error(f"Error almacenando datos: {str(e)}")
            return False

# Ejecutar el script principal
if __name__ == "__main__":
    from src.utils.logger import setup_logger
    setup_logger({
        'level': 'DEBUG',
        'log_dir': 'logs',
        'enable_console': True
    })
    
    params = {
        'tipos': ['Apartamentos'],
        'ciudad': 'Bogotá',
        'localidad': 'Chapinero'
    }
    
    try:
        extractor = RealEstateExtractor(
            url="https://www.metrocuadrado.com/buscar/",
            num_productos=3,
            **params
        )
        
        if html := extractor.download():
            print("\nDescarga exitosa!")
            propiedades = extractor.parse(html)
            
            print("\nResultados:")
            for idx, prop in enumerate(propiedades, 1):
                print(f"\nPropiedad #{idx}")
                print(f"Título: {prop['title']}")
                print(f"Precio: {prop['price']}")
                print(f"Área: {prop['area']}")
                print(f"Habitaciones: {prop['rooms']}")
                print(f"Baños: {prop['baths']}")
                print(f"URL: {prop['url']}")
                
            if extractor.store():
                print("\nDatos guardados exitosamente")
            else:
                print("\nError guardando datos")
                
    except Exception as e: 
        print(f"\nError crítico: {str(e)}")
        logging.error(f"Error general: {str(e)}", exc_info=True)