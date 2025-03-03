"""
Módulo: dynamic_page_extractor.py
Descripción:
    Implementamos el extractor para páginas web dinámicas, heredando de la 
    clase abstracta WebDataExtractor. Utiliza Selenium WebDriver para 
    cargar la página, esperar a que se renderice el contenido dinámico 
    y extraer el HTML actualizado.
    
Características:
    - Carga la página de forma dinámica usando Selenium en modo headless.
    - Espera a que se cargue el elemento <body> como indicador de 
    que el contenido se ha renderizado.
    - Parsea el HTML resultante utilizando BeautifulSoup para extraer 
    datos (por ejemplo, enlaces).
    - Almacena los datos extraídos en un archivo JSON dentro de la 
    carpeta outputs.
    
Principios de POO:
    - Herencia: Se hereda de WebDataExtractor.
    - Polimorfismo: Se implementan los métodos abstractos 
    (download, parse, store)
    de manera específica para páginas dinámicas.
    - Encapsulamiento y Abstracción: Los detalles de la carga, espera, 
    parseo y almacenamiento
    están encapsulados en métodos privados.
"""
"""
- Módulo abc:
Proporciona la infraestructura necesaria para definir clases base 
abstractas.

Fuente: https://docs.python.org/es/dev/library/abc.html
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

- Módulo selenium:
paquete utilizado para automatizar la interacción con navegadores web 
desde Python. Soporta varios navegadores y controladores. ;)
Fuente: https://www.geeksforgeeks.org/selenium-python-tutorial/

- Módulo urllib.parse:
Funciona para trabajar con URLs.
Fuente: https://docs.python.org/3/library/urllib.parse.html
"""

from abc import ABC, abstractmethod
import random
import re
import time
from selenium import webdriver
from selenium.common.exceptions import (TimeoutException, 
                                        WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from typing import List, Dict, Optional

# Importar la clase base
from src.base.web_data_extractor import WebDataExtractor

# Importar la clase ScrapedData y la sesión de la base de datos
from src.db.database import SessionLocal
from src.db.models import ScrapedData

from src.components.data_handler import DataHandler

from src.config import USER_AGENT_DINAMICOS

# Selección aleatoria de un agente de usuario
USER_AGENT = random.choice(USER_AGENT_DINAMICOS)

class DynamicPageExtractor(WebDataExtractor):
    """
    Extractor especializado para páginas web dinámicas.
    
    Utiliza Selenium WebDriver para cargar la página y esperar a que 
    se renderice el contenido dinámico, para luego extraer y parsear 
    el HTML actualizado.
    """

    def __init__(
            self, url: str, tienda: str = None, num_productos: int = 1
            ):
        """
        Inicializa el extractor de páginas dinámicas.
        """
        super().__init__(url)
        self.__tienda = tienda or self.detectar_tienda()
        self.logger.info(
            f"DynamicPageExtractor inicializado para la URL: {self.url}" 
            )
        self.__num_productos = num_productos
        self.logger.info(
            f"DynamicPageExtractor inicializado para la URL: {self.url} "
            f"con {self.num_productos} productos."
        )

    @property
    def tienda(self) -> str:
        """Obtiene la clave de la tienda detectada."""
        return self.__tienda
    
    @tienda.setter
    def tienda(self, value: str):
        """Establece la clave de la tienda detectada."""
        self.__tienda = value

    @property
    def num_productos(self) -> int:
        """Obtiene el número de productos a extraer."""
        return self.__num_productos
    
    @num_productos.setter
    def num_productos(self, value: int):
        """Establece el número de productos a extraer."""
        if value < 1:
            raise ValueError("El número de productos debe ser mayor que 0.")
        self.__num_productos = value
        self.logger.info(
            f"Número de productos establecido a: {self.num_productos}."
        )

    def detectar_tienda(self) -> str:
        """Detecta la tienda basada en el dominio de la URL."""
        self.logger.debug(f"Detectando tienda para URL: {self.url}.")
        
        dominio = urlparse(self.url).netloc.lower()  # Ej: "www.alkosto.com"
        
        # Mapeo de dominios a claves de selectores
        dominios_tiendas = {
            "mercadolibre": ["mercadolibre.com", "listado.mercadolibre"],
            "alkosto": ["alkosto.com"],
            "metrocuadrado": ["metrocuadrado.com"]
        }
        
        for tienda, dominios in dominios_tiendas.items():
            if any(subdominio in dominio for subdominio in dominios):
                self.logger.info(f"Tienda detectada: {tienda}")
                return tienda
        
        raise ValueError(f"No se reconoce la tienda para el dominio: {dominio}.")

    def download(self) -> str:
        """
        Descarga el contenido HTML actualizado de la página dinámica 
        utilizando Selenium.

        Configura el WebDriver de Chrome en modo headless para evitar 
        abrir una ventana y espera a que se cargue el elemento <body> 
        como indicador de que la página se ha renderizado.
        """
        max_intentos = 3
        tiempo_espera = 60  # Aumentar el tiempo de espera a 60 segundos
        driver = None
        tienda = self.detectar_tienda()

        for intento in range(1, max_intentos + 1):
            try:
                self.logger.debug(
                    f"Intento {intento}/{max_intentos}: Se está "
                    "configurando Selenium WebDriver para "
                    "scrapear página dinámica..."
                    )
                # Configuración MEJORADA para evadir detección
                opciones = Options()
                opciones.add_argument("--headless=new")  # Modo headless menos detectable
                opciones.add_argument(f"user-agent={random.choice(
                                        USER_AGENT_DINAMICOS)}") 
                opciones.add_argument(
                    "--disable-blink-features=AutomationControlled")
                opciones.add_argument("--disable-infobars")
                opciones.add_argument("--no-sandbox")
                opciones.add_argument("--disable-dev-shm-usage")
                opciones.add_argument("--disable-gpu")
                opciones.add_argument("--lang=es-ES")  # Configura idioma
                opciones.add_argument("--enable-unsafe-swiftshader")  # Para WebGL
                opciones.add_argument("--disable-web-security")  # Desactiva políticas CORS
                opciones.add_argument("--disable-site-isolation-trials")  # Evita aislamiento
                opciones.add_argument("--use-gl=swiftshader")
                
                # Eliminar huellas de automation
                opciones.add_experimental_option(
                    "excludeSwitches", ["enable-automation"])
                opciones.add_experimental_option("useAutomationExtension", False)

                # Instanciar el WebDriver (asegúrate de tener el driver 
                # de Chrome instalado y en el PATH)
                driver = webdriver.Chrome(options=opciones)
                self.logger.debug(
                    "El WebDriver se ha inicializado correctamente."
                    )
                
                # Engaña a sitios que verifican navigator.webdriver
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                
                # Se hace una espera implícita de 5 segundos para to-
                # dos los elementos 
                driver.implicitly_wait(30)
                # Evita que la página tarde demasiado en cargar
                driver.set_page_load_timeout(50)
                self.logger.debug(
                    "Se ha iniciado el Navegador en modo headless. "
                    f"Accediendo a {self.url}" 
                    )
                driver.get(self.url)

                last_height = driver.execute_script(
                    "return document.body.scrollHeight")
                scroll_attempts = 0
                max_scroll = 8 if tienda == "metrocuadrado" else 5

                while scroll_attempts < max_scroll:
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight)")
                    
                    # Tiempos de espera específicos por tienda
                    if tienda == "metrocuadrado":
                        for _ in range(8):
                            driver.execute_script(
                            "window.scrollBy(0, window.innerHeight * 0.8)")
                            time.sleep(random.uniform(2.5, 4.5))
                            if driver.execute_script(
                                "return document.readyState") == "complete":
                                break
                    elif tienda == "alkosto":
                        time.sleep(3)  # Mantener tiempo original para Alkosto
                    else:
                        time.sleep(2)  # Tiempo original para Mercadolibre
                    
                    new_height = driver.execute_script(
                        "return document.body.scrollHeight")
                    
                    # Lógica original de verificación de altura
                    if new_height == last_height:
                        break
                    
                    last_height = new_height
                    scroll_attempts += 1

                    # Scroll adicional solo para Metrocuadrado
                    if tienda == "metrocuadrado" and scroll_attempts % 2 == 0:
                        driver.execute_script("window.scrollBy(0, 500)")
                        time.sleep(1)

                # Esperas específicas por tienda
                if tienda == "alkosto":
                    WebDriverWait(driver, 25).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "li.ais-InfiniteHits-item")
                        )
                    )
                elif tienda == "mercadolibre":
                    WebDriverWait(driver, 15).until(
                        lambda d: any(
                            img.get_attribute("src") 
                            for img in d.find_elements(
                                By.CLASS_NAME, "poly-component__picture")
                        )
                    )
                # En la sección de esperas específicas por tienda, agregar:
                elif tienda == "metrocuadrado":
                    # Esperar carga de elementos clave DESPUÉS del scroll
                    WebDriverWait(driver, tiempo_espera).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "li.sc-gPEVay.dibcyk")
                        )
                    )
                    elementos = driver.find_elements(
                        By.CSS_SELECTOR, "li.sc-gPEVay.dibcyk")

                    # Verificar que al menos un precio tenga formato válido
                    WebDriverWait(driver, 20).until(
                        lambda d: any(
                            re.search(r'\$\d+[\d.,]*', e.text) 
                            for e in d.find_elements(
                                By.CSS_SELECTOR, "p.sc-fMiknA")
                        )
                    )
                    # Verificar que al menos un precio tenga formato válido
                    WebDriverWait(driver, 20).until(
                        lambda d: any(
                            re.search(r'\$\d+[\d.,]*', e.text) 
                            for e in d.find_elements(
                                By.CSS_SELECTOR, "p.sc-fMiknA")
                        )
                    )
                
                # Espera genérica de body como fallback
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            
                html = driver.page_source
                self.html_content = html
                self.logger.debug(
                    "¡Hurra! El contenido dinámico ha sido descargado "
                    "exitosamente."
                    )
                return html
            
            except TimeoutException:
                self.logger.warning(
                    f"Este es el intento: {intento}. No se ha "
                    f"podido cargar la página {self.url} en "
                    "el tiempo esperado."
                    )
            except WebDriverException as e:
                self.logger.error(
                    f"Este es el intento: {intento}. Error de "
                    "WebDriver al cargar la página "
                    f"{self.url}: {str(e)}"
                    )
                break
            except Exception as e:
                self.logger.error(
                    f"Este es el intento: {intento}. Hay un error "
                    f"general en Selenium: {str(e)}"
                )
            finally:
                if driver is not None:
                    driver.quit()
        self.logger.error(
            "Error. :( No se pudo descargar la página dinámica, " 
            f"después de {max_intentos} intentos."
            )
        return None
    
    @abstractmethod
    def parse(self, html_content: Optional[str] = None) -> List[Dict]:
        """Método abstracto a implementar por subclases"""
        pass

    def save_store(self) -> bool:
        """
        Almacena los datos usando el nuevo DataHandler 
        (misma funcionalidad que antes).
        """
        try:
            if not hasattr(self, 'data') or self.data is None:
                self.parse()

            # Convertir a lista si es un solo producto
            data_to_store = (self.data 
                            if isinstance(self.data, list) 
                            else [self.data])

            handler = DataHandler(
                data=data_to_store,
                storage_format='both',
                logger=self.logger
            )
            
            # Pasar URL base para generación de nombres
            return handler.store_data(url=self.url, tipo="dynamic")
        except Exception as e:
            self.logger.error(f"Error en save_store: {str(e)}")
            return False
