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
"""

from abc import ABC, abstractmethod
import random
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
        self,
        url: str,
        tienda: str = None,
        num_productos: int = 1,
        max_paginas: int = 1,
        scroll_max: int = 5,
        scroll_wait_alkosto: float = 5.0,
        scroll_wait_default: float = 2.0,
    ):
        """
        Inicializa el extractor de páginas dinámicas.
        
        Args:
            url: URL de la página a scrapear
            tienda: Nombre de la tienda (mercadolibre, alkosto)
            num_productos: Número de productos a extraer
            max_paginas: Máximo de páginas a cargar (aproximado, cada página ~48 productos)
            scroll_max: Máximo de scrolls por página
            scroll_wait_alkosto: Tiempo de espera entre scrolls para Alkosto
            scroll_wait_default: Tiempo de espera entre scrolls por defecto
        """
        super().__init__(url)
        self.__tienda = tienda or self.detectar_tienda()
        self.__num_productos = num_productos
        self.__max_paginas = max_paginas
        self._scroll_max = scroll_max
        self._scroll_wait_alkosto = scroll_wait_alkosto
        self._scroll_wait_default = scroll_wait_default

        self.logger.info(
            f"DynamicPageExtractor inicializado para la URL: {self.url}" 
            )
        self.logger.info(
            f"DynamicPageExtractor inicializado para la URL: {self.url} "
            f"con {self.num_productos} productos y máximo {self.max_paginas} página(s)."
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
    
    @property
    def max_paginas(self) -> int:
        """Obtiene el máximo de páginas a cargar."""
        return self.__max_paginas
    
    @max_paginas.setter
    def max_paginas(self, value: int):
        """Establece el máximo de páginas a cargar."""
        if value < 1:
            raise ValueError("El número de páginas debe ser mayor que 0.")
        self.__max_paginas = value
        self.logger.info(
            f"Máximo de páginas establecido a: {self.max_paginas}."
        )

    def detectar_tienda(self) -> str:
        """Detecta la tienda basada en el dominio de la URL."""
        self.logger.debug(f"Detectando tienda para URL: {self.url}.")
        
        dominio = urlparse(self.url).netloc.lower()
        
        # Mapeo de dominios a claves de selectores (solo e-commerce)
        dominios_tiendas = {
            "mercadolibre": ["mercadolibre.com", "listado.mercadolibre"],
            "alkosto": ["alkosto.com"]
        }
        
        for tienda, dominios in dominios_tiendas.items():
            if any(subdominio in dominio for subdominio in dominios):
                self.logger.info(f"Tienda detectada: {tienda}")
                return tienda
        
        raise ValueError(f"No se reconoce la tienda para el dominio: {dominio}.")

    def download(self, override_url: str = None) -> str:
        """
        Descarga el contenido HTML actualizado de la página dinámica 
        utilizando Selenium.

        Configura el WebDriver de Chrome en modo headless para evitar 
        abrir una ventana y espera a que se cargue el elemento <body> 
        como indicador de que la página se ha renderizado.
        """
        max_intentos = 3
        driver = None
        tienda = self.tienda or self.detectar_tienda()
        target_url = override_url or self.url

        for intento in range(1, max_intentos + 1):
            try:
                self.logger.debug(
                    f"Intento {intento}/{max_intentos}: Se está "
                    "configurando Selenium WebDriver para "
                    "scrapear página dinámica..."
                    )
                # Configuración MEJORADA para evadir detección
                opciones = self._configurar_chrome_options()
                driver = webdriver.Chrome(options=opciones)
                self.logger.debug(
                    "El WebDriver se ha inicializado correctamente."
                    )
                
                # Engaña a sitios que verifican navigator.webdriver
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                
                # Se hace una espera implícita de 30 segundos para todos los elementos 
                driver.implicitly_wait(30)
                # Evita que la página tarde demasiado en cargar
                driver.set_page_load_timeout(50)
                self.logger.debug(
                    "Se ha iniciado el Navegador en modo headless. "
                    f"Accediendo a {target_url}" 
                    )
                driver.get(target_url)

                # Estrategia de scroll extraído a método separado
                # Calcular scrolls necesarios según max_paginas
                # Cada "página" de MercadoLibre tiene ~48 productos
                # Asumiendo que cada 2-3 scrolls se carga ~1 página
                scrolls_por_pagina = 3
                # Si recibimos override_url significa que ya estamos
                # en una página específica; solo scrolleamos 1 página.
                scroll_pages = 1 if override_url else self.__max_paginas
                scroll_max_calculado = scroll_pages * scrolls_por_pagina
                
                self.logger.info(
                    f"Aplicando scroll para cargar hasta {self.__max_paginas} página(s) "
                    f"({scroll_max_calculado} scrolls aproximadamente)"
                )
                
                self._aplicar_scroll(
                    driver,
                    tienda,
                    scroll_max_calculado,
                    self._scroll_wait_alkosto,
                    self._scroll_wait_default,
                )

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
    
    def _configurar_chrome_options(self) -> Options:
        """Configura opciones de Chrome para evasión de detección."""
        opciones = Options()
        opciones.add_argument("--headless=new")
        opciones.add_argument(f"user-agent={USER_AGENT}")
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_argument("--disable-infobars")
        opciones.add_argument("--no-sandbox")
        opciones.add_argument("--disable-dev-shm-usage")
        opciones.add_argument("--disable-gpu")
        opciones.add_argument("--lang=es-ES")
        opciones.add_argument("--enable-unsafe-swiftshader")
        opciones.add_argument("--disable-web-security")
        opciones.add_argument("--disable-site-isolation-trials")
        opciones.add_argument("--use-gl=swiftshader")
        
        opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
        opciones.add_experimental_option("useAutomationExtension", False)
        
        return opciones

    def _aplicar_scroll(
        self,
        driver,
        tienda: str,
        max_scroll: int = 5,
        wait_alkosto: float = 5.0,
        wait_default: float = 2.0,
    ):
        """Aplica scroll con parámetros configurables."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        
        # Para Alkosto, contar productos en lugar de altura
        if tienda == "alkosto":
            from bs4 import BeautifulSoup
            last_product_count = 0
            no_change_count = 0
            
            while scroll_attempts < max_scroll:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(wait_alkosto)
                
                # Contar productos actuales
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                current_products = len(soup.find_all('li', class_='ais-InfiniteHits-item'))
                
                # Si no hay cambio en productos, incrementar contador
                if current_products == last_product_count:
                    no_change_count += 1
                    if no_change_count >= 2:  # Detenerse después de 2 scrolls sin cambios
                        break
                else:
                    no_change_count = 0  # Resetear si hubo cambio
                
                last_product_count = current_products
                scroll_attempts += 1
        else:
            # Para otras tiendas (MercadoLibre), usar altura
            while scroll_attempts < max_scroll:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(wait_default)
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                
                last_height = new_height
                scroll_attempts += 1

    @abstractmethod
    def parse(self, html_content: Optional[str] = None) -> List[Dict]:
        """Método abstracto a implementar por subclases"""
        pass

    def store(self) -> bool:
        try:
            if not self.data:
                self.parse()

            data_to_store = self.data if isinstance(self.data, list) else [self.data]

            handler = DataHandler(
                data=data_to_store,
                storage_format='both',
                logger=self.logger
            )

            tipo = "e-commerce" if self.tienda in {"mercadolibre", "alkosto"} else "dynamic"
            return handler.store_data(url=self.url, tipo=tipo)
        except Exception as e:
            self.logger.error(f"Error en store: {str(e)}")
            return False
