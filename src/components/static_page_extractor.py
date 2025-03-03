"""
Módulo: static_page_extractor.py
Descripción:
    Implementa el extractor para páginas web estáticas, heredando de la 
    clase abstracta WebDataExtractor. Este extractor:
    - Descarga el HTML de la página usando Requests, con reintentos y 
    caching.
    - Parsea el HTML para extraer información estructurada (título, 
    infobox, contenido, imágenes) orientada a sitios como Wikipedia y 
    wikis de fandom.
    - Almacena los datos extraídos en una base de datos SQL mediante 
    SQLAlchemy.
    - Permite la personalización de selectores y otros parámetros a 
    través de un archivo de configuración.

Principios de POO:
    - Herencia y Polimorfismo: Hereda de WebDataExtractor e implementa 
    sus métodos abstractos.
    - Encapsulamiento: La lógica interna (descarga, parseo y 
    almacenamiento) está oculta, exponiéndose únicamente a través de la 
    interfaz pública.
"""

"""
- Módulo hashlib:
Convierte los datos de entrada en una cadena de bytes de tamaño fijo.
Fuente: https://docs.python.org/es/3.10/library/hashlib.html

- Módulo json:
Para convertir datos a formato JSON.
Fuente: https://www.freecodecamp.org/espanol/news/python-leer-archivo-json-como-cargar-json-desde-un-archivo-y-procesar-dumps/

- Módulo os:
Permite interactuar con funcionalidades dependientes del sistema 
operativo.
Fuente: https://docs.python.org/es/3.10/library/os.html

- Módulo requests:
Para realizar solicitudes HTTP y obtener respuestas.
Fuente: https://www.geeksforgeeks.org/python-requests-tutorial/

- Módulo time:
Proporciona varias funciones para manejar tareas relacionadas con 
el tiempo.
Fuente: https://docs.python.org/es/3.10/library/time.html

- Módulo BeautifulSoup:
Para extraer datos de archivos HTML y XML.
Fuente: https://datascientest.com/es/beautiful-soup-aprender-web-scraping

- Módulo urllib.parse.urljoin:
Construye una URL completa ("absoluta") combinando una "URL base" 
(base) con otra URL (url)
Fuente: https://docs.python.org/3/library/urllib.parse.html
"""

import hashlib
import json
import os
import requests
import time

from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Importar la clase base
from src.base.web_data_extractor import WebDataExtractor

from src.config import (
    STATIC_TIMEOUT_ST, 
    RETRY_COUNT_ST, 
    RETRY_DELAY_ST, 
    USER_AGENT_ST, 
    SELECTORS_ST_DEFAULT,
    SELECTORS_ST_BY_SITE,
    CACHE_DIR)

from src.components.data_handler import DataHandler

# Diccionario para contenido descargado en caché.
CACHE = {} 

class StaticPageExtractor(WebDataExtractor):
    """
    Esta clase implementa la extracción de datos en páginas web 
    estáticas (HTML/CSS). Hereda de `WebDataExtractor` (herencia) y 
    utiliza encapsulamiento para ocultar la lógica de los selectores, 
    parseo y almacenamiento.
    """

    def __init__(self, url):
        """
        Inicializa el extractor con la URL proporcionada.
        Utiliza encapsulamiento para manejar selectores.
        """
        super().__init__(url)  # Herencia: llama al constructor de la clase base
        self.logger.info(
            f"StaticPageExtractor inicializado para la URL: {self.url}."
            )
        self.__selectores = self.get_selectores()
        self.logger.info(
            f"Selectores usados para {self.url}: {self.__selectores}.")
    
    @property
    def selectores(self):
        """Obtiene los selectores actuales."""
        return self.__selectores
    
    @selectores.setter
    def selectores(self, selectores):
        """Establece los selectores."""
        self.__selectores = selectores

    def get_selectores(self):
        """Elige selectores según el dominio de la URL."""
        for domain in SELECTORS_ST_BY_SITE:
            if domain in self.url:
                return SELECTORS_ST_BY_SITE[domain]
        self.logger.warning(
            f"Usando selectores genéricos para: {self.url}")
        return SELECTORS_ST_DEFAULT

    def get_cache_filename(self):
        """
        Genera un nombre de archivo único basado en la URL.
        """
        # Convierte la URL en un hash único
        url_hash = hashlib.md5(self.url.encode()).hexdigest() 
        return os.path.join(CACHE_DIR, f"{url_hash}.html")

    def download(self):
        cache_file = self.get_cache_filename()
        
        # 1. Validar caché en memoria
        if self.url in CACHE:
            cached_content = CACHE[self.url]
            if cached_content and len(cached_content) > 1000:  # Mínimo razonable
                self.html_content = cached_content
                self.logger.debug(f"Cache memoria válido: {self.url}")
                return self.html_content
            else:
                self.logger.warning("Cache memoria inválido. Eliminando...")
                del CACHE[self.url]

        # 2. Validar caché en disco
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                disk_content = f.read()
                if disk_content and len(disk_content) > 1000:
                    self.html_content = disk_content
                    CACHE[self.url] = disk_content
                    self.logger.debug(f"Cache disco válido: {len(disk_content)} caracteres")
                    return self.html_content
                else:
                    self.logger.error("Cache disco inválido. Eliminando...")
                    os.remove(cache_file)

        # 3. Descarga nueva con verificación
        headers = {"User-Agent": USER_AGENT_ST}
        intentos = 0
        
        while intentos < RETRY_COUNT_ST:
            try:
                response = requests.get(self.url, headers=headers, timeout=STATIC_TIMEOUT_ST)
                response.raise_for_status()
                
                new_content = response.text
                if not new_content or len(new_content) < 1000:
                    raise ValueError("Contenido insuficiente")
                    
                if "<!DOCTYPE html>" not in new_content[:100].lower():
                    raise ValueError("No es un documento HTML válido")

                self.html_content = new_content
                CACHE[self.url] = new_content
                
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                self.logger.info(f"Descarga exitosa: {len(new_content)} caracteres")
                return new_content
                
            except Exception as e:
                self.logger.error(f"Intento {intentos+1} fallido: {str(e)}")
                intentos += 1
                time.sleep(RETRY_DELAY_ST)
        
        raise Exception(f"Fallo definitivo: {self.url}")

    def parse(self):
        """
        Parsea el HTML descargado y extrae información estructurada.
        Utiliza polimorfismo al sobrescribir el método de la clase base.
        """
        try:
            self.logger.debug("Iniciando parseo del contenido HTML.")
            if not self.html_content:  # Validación adicional
                raise ValueError("No hay contenido HTML para parsear")

            soup = BeautifulSoup(self.html_content, 'html.parser')
            
            # Se otiene los selectores específicos para el dominio 
            selectores = self.selectores
            
            # Extrae el título de la página
            title_config = selectores.get("title", {})
            title_tag = soup.find(
                title_config.get("tag", "h1"),  # Valor por defecto 'h1' si no existe
                id=title_config.get("id"),
                class_=title_config.get("class")
            )
            title = title_tag.get_text(strip=True) if title_tag else "Sin Título"

            # Extrae infobox 
            infobox = {}
            infobox_config = self.selectores.get("infobox", {})

            # Buscar la infobox según el selector del sitio actual
            infobox_container = soup.find(infobox_config.get("tag"), class_=infobox_config.get("class"))

            if infobox_container:
                print("Infobox encontrada.")

                # Si es una infobox de Wikipedia (tabla)
                if infobox_config.get("tag") == "table":
                    for row in infobox_container.find_all("tr"):
                        header = row.find("th")
                        cell = row.find("td")
                        if header and cell:
                            key = header.get_text(strip=True)
                            value = cell.get_text(" ", strip=True)
                            infobox[key] = value

                # Si es una infobox de Fandom (aside)
                elif infobox_config.get("tag") == "aside":
                    for data_row in infobox_container.find_all("div", class_="pi-item pi-data"):
                        label = data_row.find("h3", class_="pi-data-label")
                        value = data_row.find("div", class_="pi-data-value")

                        if label and value:
                            label_text = label.get_text(strip=True)

                            # Si el valor es una lista de <li>, extraerlos como lista
                            if value.find("ul"):
                                value_text = [li.get_text(strip=True) for li in value.find_all("li")]
                            else:
                                value_text = value.get_text(separator=" ", strip=True)

                            infobox[label_text] = value_text

                print(f"Infobox extraída: {infobox}")
            else:
                print("No se encontró la infobox.")

            # Se extrae el contenido principal
            content_paragraphs = []
            content_config = selectores.get("content", {})
            content_container = soup.find(
                content_config.get("tag", "div"),
                id=content_config.get("id"),
                class_=content_config.get("class")
            )
            
            # Dentro del método parse(), en la sección de extracción de contenido:
            if content_container:
                paragraph_tag = selectores.get("paragraph", "p")
                
                # Excluir párrafos dentro de div.hatnote (notas al inicio)
                all_paragraphs = content_container.find_all(paragraph_tag)
                filtered_paragraphs = [
                    p for p in all_paragraphs
                    if not p.find_parent("div", class_="hatnote")  # Excluir párrafos en hatnotes
                ]
                
                for p in filtered_paragraphs[:3]:  # Limitar a los primeros 3 relevantes
                    text = p.get_text(separator=' ', strip=True)
                    if text:
                        content_paragraphs.append(text)

            # Extraer imágenes dentro del contenido principal
            images = []
            if "image" in selectores:
                image_config = selectores["image"]
                parent_configs = image_config.get("parent", [])  # Ahora es una lista de contenedores

                for parent in parent_configs:
                    content_container = soup.find(parent.get("tag"), class_=parent.get("class"))
                    
                    if content_container:
                        print(f"Contenedor de imágenes encontrado ({parent.get('class')}), buscando imágenes...")
                        for img in content_container.find_all(image_config.get("tag", "img")):
                            img_url = img.get("src")
                            if img_url:
                                full_url = urljoin(self.url, img_url)  # Convertir a URL absoluta
                                images.append(full_url)

            # Extraer listas 
            lists = []
            list_config = self.selectores.get("lists", {})
            parent_config = list_config.get("parent", {})

            # Buscar el contenedor principal
            list_container = soup.find(parent_config.get("tag"), class_=parent_config.get("class"))

            if list_container:        
                BLACKLIST_CLASSES = [
                    "toc", 
                    "index", 
                    "navigation", 
                    "menu", 
                    "sidebar", 
                    "footer"]

                # Buscar listas dentro del contenido principal
                for ul in list_container.find_all("ul"):  
                    ul_classes = ul.get("class", [])
                    
                    # Filtra listas no deseadas
                    if not any(
                        cls in ul_classes for cls in BLACKLIST_CLASSES):  
                        for li in ul.find_all("li"):
                            text = li.get_text(separator=' ', strip=True)
                            # Evitar listas vacías o muy cortas
                            if text and len(text) > 2:  
                                lists.append(text)

            # Extrae tablas
            tables = []
            table_config = selectores.get("tables", {})

            # Buscar TODAS las tablas en el contenido principal
            parent_config = selectores.get("content", {})
            content_container = soup.find(parent_config.get("tag"), class_=parent_config.get("class"))

            if content_container:
                all_tables = content_container.find_all(table_config.get("tag", "table"))
                
                if not all_tables:
                    print("No se encontraron tablas en el contenido.")
                else:
                    print(f"Se encontraron {len(all_tables)} tablas.")

                for table in all_tables:
                    headers = [th.get_text(strip=True) for th in table.find_all("th")]

                    table_data = []
                    for row in table.find_all("tr"):
                        cells = row.find_all(["td", "th"])  # Captura datos de cualquier celda
                        if not cells:
                            continue # Ignorar filas vacías

                        row_data = {}
                        for i, cell in enumerate(cells):
                            text = cell.get_text(separator=" ", strip=True)
                            column_name = headers[i] if i < len(headers) else f"Columna_{i}"  # Genera nombres si no hay headers
                            row_data[column_name] = text

                        table_data.append(row_data)

                    # Solo guardar si hay datos
                    if table_data:
                        tables.append({
                            "headers": headers if headers else [f"Columna_{i}" for i in range(len(table_data[0]))],
                            "rows": table_data
                        })

                if not tables:
                    print("Se encontraron tablas pero estaban vacías.")
                else:
                    print(f"Se extrajeron {len(tables)} tablas correctamente.")

            else:
                print("No se encontró el contenedor principal.")

            structured_data = {
                "title": title,
                "infobox": infobox if "infobox" in selectores else {},
                "content": content_paragraphs,
                "images": images,
                "url": self.url,
                "lists": lists,
                "tables": tables,
                "url": self.url
            }

            self.logger.debug("Parseo completado. Datos estructurados extraídos.")
            return structured_data

        except Exception as e:
            self.logger.error(f"Error durante el parseo: {str(e)}")
            raise Exception(f"Error en el parseo: {e}") from None
        
    def store(self) -> bool:
        try:
            # Validar estructura básica de datos
            required_keys = ['title', 'content']
            if not all(key in self.data for key in required_keys):
                self.logger.warning("Datos incompletos para almacenar")
                return False
                
            return super().store()
            
        except Exception as e:
            self.logger.error(f"Error almacenando: {str(e)}")
            return False
        
# Prueebas para solo el módulo
if __name__ == "__main__":
    # Ejemplo con Wikipedia
    url_wiki = "https://es.wikipedia.org/wiki/Python"

    # Ejemplo con Fandom (ej: Harry Potter Wiki)
    url_fandom = "https://harrypotter.fandom.com/es/wiki/Harry_Potter"
    # Ejemplo con MDN Web Docs (documentación técnica)
    url_wiki2 = "https://es.wikipedia.org/wiki/Colombia"

    url_wiki3 = "https://es.wikipedia.org/wiki/Gustavo_Petro"

    urls = [url_wiki, url_fandom, url_wiki2, url_wiki3]

    for url in urls:
        print(f"\nScrapeando: {url}")
        extractor = StaticPageExtractor(url)
        try:
            data = extractor.scrape()  # Llama a download() + parse()
            print(json.dumps(data, indent=4, ensure_ascii=False))
            if extractor.store():
                print(":) Datos guardados en JSON/SQL.")
            else:
                print(":() Error al guardar datos.")
        except Exception as e:
            print(f"Oopss. Error grave: {str(e)}")