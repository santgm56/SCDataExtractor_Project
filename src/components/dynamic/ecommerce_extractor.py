"""
Este código es un extractor de datos web dinámico utilizado para extraer 
información de páginas web que cargan contenido dinámico por medio de 
JavaScript. Utiliza Selenium para renderizar la página y BeautifulSoup 
para parsear el HTML. Está configurado para manejar múltiples tiendas o 
portales (como MercadoLibre o Alkosto) mediante selectores 
personalizables, permitiendo extraer datos como: títulos, precios, 
imágenes y descripciones. Además, incluye características como 
paginación automática, manejo de errores robusto y almacenamiento 
de datos en JSON o base de datos.
"""

import logging
import re

from bs4 import BeautifulSoup, Tag
from typing import Union, Dict, List
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

from .dynamic_page_extractor import DynamicPageExtractor
from src.components.data_handler import DataHandler

from src.config import SELECTORES_LISTA_DINAMICOS

# Añadir al inicio del archivo
from src.utils.logger import setup_logger, get_logger
from src.utils.helpers import create_directory_structure
from src.config import PAGINACION_ML

class ProductData:
    """
    Clase para manejar la estructura de datos de productos.
    Esta clase define los atributos básicos de un producto, como título, 
    imagen, precios, descuento, etc.
    También incluye un método para convertir los datos del producto en 
    un diccionario.
    """
    
    def __init__(self):
        """
        Inicializa los atributos de un producto con un valor por defecto.
        """
        # Título del producto
        self.title: str = "" 
        # URL de la imagen del producto
        self.image: Union[str, None] = None 
        # Precio original del producto
        self.price_original: str = "" 
        # Precio de venta del producto
        self.price_sell: str = "" 
        # Descuento aplicado al producto
        self.discount: str = "0%" 
        # Calificación y número de reseñas del producto
        self.rating: Dict[str, str] = {} 
        # URL del producto
        self.url: str = "" 
        # Descripción del producto
        self.description: Union[str, None] = None 


    def to_dict(self) -> Dict:
        """Convierte los datos del producto a un diccionario."""
        return self.__dict__

class EcommerceExtractor(DynamicPageExtractor):
    """
    Clase principal para extraer datos de productos de tiendas en línea.
    Hereda de `DynamicPageExtractor` (herencia) y utiliza composición
    al trabajar con objetos de la clase `ProductData`.
    """
    def __init__(
            self, url: str, tienda: str, num_productos: int = 1, max_paginas: int = 1):
        """
        Inicializa el extractor con la URL, la tienda, el número 
        de productos y el máximo de páginas. Utiliza encapsulamiento 
        para manejar atributos privados de la clase base.
        
        Args:
            url: URL de la tienda a scrapear
            tienda: Nombre de la tienda (mercadolibre, alkosto)
            num_productos: Número de productos a extraer
            max_paginas: Máximo de páginas a cargar (cada página ~48 productos)
        """
        super().__init__(url, tienda, num_productos, max_paginas) 
        # Usa el logger configurado globalmente para esta clase
        self.logger = get_logger(self.__class__.__name__)
        create_directory_structure()  # Crear estructura de directorios
        
    @property
    def tienda(self):
        """Obtiene la tienda actual."""
        return self._DynamicPageExtractor__tienda
    
    @property
    def num_productos(self):
        """Obtiene el número de productos a extraer."""
        return self._DynamicPageExtractor__num_productos
        
    @tienda.setter
    def tienda(self, value):
        """Establece la tienda actual."""
        self._DynamicPageExtractor__tienda = value

    @num_productos.setter
    def num_productos(self, value):
        """
        Establece el número de productos a extraer.
        Utiliza encapsulamiento para validar que el valor sea 
        mayor que 0.
        """
        if value < 1:
            raise ValueError("El número de productos debe ser mayor "
                            "que 0.")
        self._DynamicPageExtractor__num_productos = value

    def detectar_tienda(self) -> str:
        """Detecta la tienda basada en patrones de URL."""
        # Registrar un mensaje de depuración con la URL actual
        self.logger.debug(f"Detectando tienda para URL: {self.url}.")
        # Iterar sobre la lista de tiendas definidas en S
        # ELECTORES_LISTA_DINAMICOS
        for tienda in SELECTORES_LISTA_DINAMICOS:
            # Si el nombre de la tienda se encuentra en la URL
            if tienda in self.url:
                self.logger.info(f"Tienda detectada: {tienda}")
                # Devolver el nombre de la tienda detectada
                return tienda
        raise ValueError("No se reconoce la tienda para la URL: "
                        f"{self.url}.")

    def scrape(self):
        """Sobrescribe scrape para soportar paginación en MercadoLibre y Alkosto."""
        tienda = self.tienda or self.detectar_tienda()

        if tienda == "mercadolibre":
            return self._scrape_mercadolibre_paginated()
        if tienda == "alkosto":
            return self._scrape_alkosto_paginated()

        return super().scrape()

    def _scrape_mercadolibre_paginated(self):
        """Descarga múltiples páginas usando el patrón _Desde_ y acumula productos."""
        all_products = []

        base_url = self._normalizar_url_ml(self.url)

        for page in range(1, self.max_paginas + 1):
            page_url = self._build_ml_page_url(base_url, page)
            self.logger.info(
                f"Descargando página {page}/{self.max_paginas} de MercadoLibre: {page_url}"
            )

            html = self.download(override_url=page_url)
            if not html:
                self.logger.warning(
                    f"No se obtuvo HTML para la página {page}. Deteniendo paginación."
                )
                break

            try:
                parsed = self.parse(html_content=html) or []
            except Exception as e:
                self.logger.error(
                    f"Error parseando la página {page} de ML: {e}. Se detiene paginación.",
                    exc_info=True,
                )
                break

            all_products.extend(parsed)

            if len(all_products) >= self.num_productos:
                self.logger.info(
                    f"Se alcanzó el límite solicitado de {self.num_productos} productos."
                )
                break

        # Limitar al número solicitado
        self.data = all_products[: self.num_productos]

        # Guardar resultados
        try:
            self.store()
        except Exception as e:
            self.logger.error(f"Error guardando resultados ML: {e}")
        return self.data

    def _normalizar_url_ml(self, url: str) -> str:
        """Elimina cualquier sufijo _Desde_xxx para usarlo como base de paginación."""
        # Quitar sufijos tipo _Desde_49_NoIndex_True
        return re.sub(r"_Desde_\d+(?:_NoIndex_True)?", "", url)

    def _build_ml_page_url(self, base_url: str, page: int) -> str:
        """Construye la URL de la página dada usando el offset de 48 items."""
        if page <= 1:
            return base_url

        page_size = PAGINACION_ML.get("page_size", 48)
        sufijo = PAGINACION_ML.get("url_suffix", "_NoIndex_True")

        # ML usa offsets comenzando en 1 y luego 49, 97, etc.
        start = 1 + (page - 1) * page_size
        return f"{base_url}_Desde_{start}{sufijo}"

    def _scrape_alkosto_paginated(self):
        """Pagina usando el parámetro page= y acumula productos."""
        all_products = []

        base_url = self._normalizar_url_alkosto(self.url)

        for page in range(1, self.max_paginas + 1):
            page_url = self._build_alkosto_page_url(base_url, page)
            self.logger.info(
                f"Descargando página {page}/{self.max_paginas} de Alkosto: {page_url}"
            )

            html = self.download(override_url=page_url)
            if not html:
                self.logger.warning(
                    f"No se obtuvo HTML para la página {page}. Deteniendo paginación."
                )
                break

            try:
                parsed = self.parse(html_content=html) or []
            except Exception as e:
                self.logger.error(
                    f"Error parseando la página {page} de Alkosto: {e}. Se detiene paginación.",
                    exc_info=True,
                )
                break

            all_products.extend(parsed)

            if len(all_products) >= self.num_productos:
                self.logger.info(
                    f"Se alcanzó el límite solicitado de {self.num_productos} productos."
                )
                break

        self.data = all_products[: self.num_productos]
        try:
            self.store()
        except Exception as e:
            self.logger.error(f"Error guardando resultados Alkosto: {e}")
        return self.data

    def _normalizar_url_alkosto(self, url: str) -> str:
        """Elimina cualquier page= existente para usar como base."""
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        qs.pop("page", None)
        query = urlencode(qs, doseq=True)
        cleaned = parsed._replace(query=query)
        return cleaned.geturl()

    def _build_alkosto_page_url(self, base_url: str, page: int) -> str:
        """Construye URL con page=N preservando otros parámetros."""
        parsed = urlparse(base_url)
        qs = parse_qs(parsed.query)
        if page > 1:
            qs["page"] = [str(page)]
        else:
            qs.pop("page", None)
        query = urlencode(qs, doseq=True)
        return parsed._replace(query=query).geturl()
    
    def parse(self, html_content: str = None) -> List[Dict]:
        """
        Extrae y estructura los datos de productos del HTML descargado.
        """
        try:
            # Usar el parámetro html_content si se provee, sino el atributo de clase
            content = html_content if html_content else self.html_content
            
            if not content:
                raise ValueError("No hay contenido HTML para parsear.")
            
            self.logger.info("Iniciando proceso de parseo.")
            soup = BeautifulSoup(content, 'html.parser')
            selectores = self.obtener_selectores()
            productos = self.procesar_productos(soup, selectores)
            self.validar_resultados(productos)
            # Retornar un solo producto si num_productos=1, sino la lista completa
            self.data = productos if self.num_productos > 1 else (productos[0] if productos else None)
            return self.data
        
        except Exception as e:
            self.logger.error(f"Error en parseo: {str(e)}.", exc_info=True)
            raise

    def obtener_selectores(self) -> Dict:
        """Determina los selectores a usar según el tipo de página."""
        # Verificar si la URL corresponde a una página de 
        # producto individual
        if "/p/" in self.url or "/item/" in self.url:
            self.logger.debug("Usando selectores de página individual.")
            # Devolver los selectores para una página individual de 
            # la tienda actual
            return SELECTORES_LISTA_DINAMICOS[self.tienda]
        # Si no es una página individual, asumir que es una página 
        # de listado
        self.logger.debug("Usando selectores de listado.")
        # Verificar si la tienda actual tiene selectores definidos 
        # en la configuración
        if self.tienda not in SELECTORES_LISTA_DINAMICOS:
            raise ValueError("No hay selectores de listado para "
                            f"{self.tienda}.")
        # Devolver los selectores para una página de listado de 
        # la tienda actual
        return SELECTORES_LISTA_DINAMICOS[self.tienda]

    def procesar_productos(self, 
                        soup: BeautifulSoup, 
                        selectores: Dict) -> List[Dict]:
        """
        Procesa el contenido HTML y extrae los datos de productos.
        Utiliza composición al crear instancias de `ProductData`.
        """
        # Obtener el contenedor principal de productos utilizando los 
        # selectores
        contenedor_productos = self.obtener_contenedor_productos(
                                                    soup, 
                                                    selectores)
        
        # Extraer y estructurar los datos de cada producto en el 
        # contenedor
        return [
            self.extraer_datos_producto(producto, selectores) 
            for producto in contenedor_productos
        ]

    def obtener_contenedor_productos(self, 
                                    soup: BeautifulSoup, 
                                    selectores: Dict) -> List[Tag]:
        """Obtiene el contenedor principal de productos"""
        # Verificar si el selector de producto está definido
        if "producto" not in selectores:
            # Si no está definido, asumir que es una página individual y 
            # usar el contenedor único
            self.logger.debug(
                "Usando contenedor único para página individual")
            return [soup]
        
        self.logger.debug("Buscando contenedor de productos en listado")
        # Buscar todos los elementos que coincidan con el 
        # selector de producto (para aprovechar todo el scroll)
        productos_encontrados = soup.find_all(
            selectores["producto"]["tag"],
            class_=selectores["producto"].get("class")
        )
        
        # Log para debugging: cuántos productos se encontraron en el HTML
        self.logger.info(
            f"Productos encontrados en el HTML después del scroll: {len(productos_encontrados)}"
        )
        
        # Informar si se encontraron menos productos de los solicitados
        if len(productos_encontrados) < self.num_productos:
            self.logger.warning(
                f"Se solicitaron {self.num_productos} productos "
                f"pero solo se encontraron {len(productos_encontrados)}"
            )
        
        # Limitar al número solicitado (tomar los primeros num_productos)
        return productos_encontrados[:self.num_productos]
    
    def extraer_datos_producto(self, 
                        producto: Tag, 
                        selectores: Dict) -> Dict:
        """
        Extrae y estructura los datos de un producto individual.
        Utiliza composición al trabajar con un objeto de `ProductData`.
        """
        data = ProductData()  # Composición: crea una instancia de ProductData
        
        try:
            self.logger.debug("Extrayendo título del producto")
            data.title = self.extraer_texto(
                producto, selectores["title"])
            
            self.logger.debug("Extrayendo imagen del producto")
            data.image = self.extraer_imagen(
                producto, selectores["image"])
            
            self.logger.debug("Extrayendo precio original del producto")
            data.price_original = self.extraer_precio(
                producto, selectores["price_original"])
            
            self.logger.debug("Extrayendo precio de venta del producto")
            data.price_sell = self.extraer_precio(
                producto, selectores["price_sell"])
            
            self.logger.debug("Extrayendo descuento del producto")
            data.discount = self.procesar_descuento(
                producto, selectores.get("discount"))
            
            self.logger.debug("Extrayendo calificación del producto")
            data.rating = self.extraer_puntuacion(
                producto, selectores["rating"])
            
            self.logger.debug("Extrayendo URL del producto")
            data.url = self.extraer_url(producto, selectores.get("url"))
            
            # Solo extraer descripción si es página individual de Alkosto
            self.logger.debug("Extrayendo descripción del producto")
            data.description = self.extraer_descripcion(
                producto, selectores.get("description"))

        except KeyError as e:
            self.logger.warning(f"Selector no encontrado: {str(e)}.")
        except Exception as e:
            self.logger.error(f"Error extrayendo datos: {str(e)}")

        # Convertir los datos del producto a un diccionario y devolverlo
        return data.to_dict()

    def extraer_texto(self, elemento: Tag, selector: Dict) -> str:
        """
        Extrae texto de un elemento usando el selector 
        proporcionado.
        Si el selector no está especificado, devuelve una cadena vacía."""
        if not selector:
            return ""
            
        # Buscar el elemento padre usando la etiqueta y clase(s)
        elemento_padre = (elemento.find(selector["tag"], 
                        class_=selector.get("class")))
        if not elemento_padre:
            return ""
            
        # Si se especifica un sub_element, buscarlo dentro del elemento padre.
        if "sub_element" in selector:
            sub_selector = selector["sub_element"]
            elemento_hijo = (
                elemento_padre.
                find(sub_selector["tag"], 
                class_=sub_selector.get("class")))
            # Si se encontró el sub-elemento, usar ese; si no, fallback 
            # al elemento padre
            elemento_final = (elemento_hijo 
                            if elemento_hijo 
                            else elemento_padre)
        else:
            elemento_final = elemento_padre
            
        return elemento_final.get_text(strip=True) if elemento_final else ""

    def extraer_imagen(self, 
                    elemento: Tag, 
                    selector: Dict) -> Union[str, None]:
        """Extrae URL de imagen (compatible con Alkosto y ML)"""
        if not selector:
            return None
        
        # Buscar el contenedor padre (div para Alkosto, img para ML)
        contenedor = elemento.find(
            selector["tag"], 
            class_=selector.get("class"))
        if not contenedor:
            return None
        
        # Buscar la etiqueta img dentro del contenedor (solo para Alkosto)
        if "sub_element" in selector:
            img_element = contenedor.find(selector["sub_element"]["tag"])
        else:
            # Para ML que ya es la etiqueta img
            img_element = contenedor  
        
        if not img_element:
            return None
        
        # Extraer URL de la imagen
        for attr in ["src", "data-src"]:
            if attr in img_element.attrs:
                url = img_element[attr]
                if not url.startswith("data:image"):
                    # Convertir URLs relativas de Alkosto a absolutas
                    if self.tienda == "alkosto" and url.startswith("/"):
                        return urljoin("https://www.alkosto.com", url)
                    return url
        return None

    def extraer_precio(self, elemento: Tag, selector_padre: Dict) -> str:
        """
        Extrae y formatea el precio completo con 
        símbolo y fracción.
        """
        if not selector_padre:
            return "Precio no disponible"

        if (selector_padre.get('optional') and 
            not elemento.find(selector_padre["tag"], 
            class_=selector_padre.get("class"))):
            return self.extraer_precio(elemento, 
                        SELECTORES_LISTA_DINAMICOS[self.tienda]["price_sell"])
        
        # Buscar el contenedor principal del precio
        elemento_padre = elemento.find(
            selector_padre["tag"], 
            class_=selector_padre.get("class")
        )
        if not elemento_padre:
            return "Precio no encontrado"
        
        # Extraer símbolo de moneda
        simbolo = ""
        if "currency_symbol" in selector_padre:
            simbolo_selector = selector_padre["currency_symbol"]
            simbolo_element = elemento_padre.find(
                simbolo_selector["tag"],
                class_=simbolo_selector.get("class")
            )
            simbolo = (simbolo_element
                    .get_text(strip=True) 
                    if simbolo_element else "")
        
        # Extraer valor numérico
        fraccion = ""
        if "fraction" in selector_padre:
            fraction_selector = selector_padre["fraction"]
            
            # Caso Alkosto: valor en texto del contenedor padre
            if fraction_selector.get("tag") is None:
                texto_completo = elemento_padre.get_text(strip=True)
                fraccion = texto_completo.replace(simbolo, "").strip()
            
            # Caso MercadoLibre: valor en elemento hijo
            else:
                fraction_element = elemento_padre.find(
                    fraction_selector["tag"],
                    class_=fraction_selector.get("class")
                )
                fraccion = (fraction_element
                            .get_text(strip=True) 
                            if fraction_element else "")
        
        else:
            fraccion = elemento_padre.get_text(strip=True)
        
        return (
            f"{simbolo}{fraccion}" 
            if fraccion else "Precio no disponible")

    def procesar_descuento(self, elemento: Tag, selector: Dict) -> str:
        """Extrae y limpia el porcentaje de descuento."""
        if self.tienda == "alkosto":
            if not selector:
                return "0%"
            
            # Buscar el contenedor padre
            contenedor = elemento.find(
                selector["tag"], 
                class_=selector.get("class")
            )
            if not contenedor:
                return "0%"
            
            # Buscar el elemento del descuento dentro del contenedor
            sub_element = contenedor.find(
                selector["sub_element"]["tag"],
                class_=selector["sub_element"].get("class")
            )
            if not sub_element:
                return "0%"
            
            texto = sub_element.get_text(strip=True)
            match = re.search(r"(\d+%)", texto)
            return match.group(0) if match else "0%"
        
        # Lógica para otras tiendas
        texto_descuento = self.extraer_texto(elemento, selector)
        if not texto_descuento:
            return "0%"
        
        match = re.search(r"(\d+%)", texto_descuento)
        return match.group(1) if match else "0%"

    def extraer_puntuacion(self, 
                            elemento: Tag, 
                            selector: Dict) -> Dict[str, str]:
        """Extrae y formatea los datos de calificación."""
        default = {"rating": "N/A", "rating_count": "Sin calificaciones"}

        if self.tienda == "alkosto":
            rating_element = elemento.find("span", class_="averageNumber")
            count_element = elemento.find("span", class_="review")
            
            if not rating_element or not count_element:
                return default
            
            rating = rating_element.get_text(strip=True)
            count = count_element.get_text(strip=True)
            count_match = re.search(r"\((\d+)\)", count)
            
            if not count_match:
                return default
            
            return {
                "rating": f"{rating} de 5",
                "rating_count": f"{count_match.group(1)} reseñas"
            }
        
        elif self.tienda == "mercadolibre":
            # Lógica para MercadoLibre
            contenedor = elemento.find("div", class_="poly-component__reviews")
            if not contenedor:
                return default
                
            rating = contenedor.find("span", class_="poly-reviews__rating")
            count = contenedor.find("span", class_="poly-reviews__total")
            
            try:
                rating_num = rating.get_text(strip=True) if rating else "N/A"
                
                if count:
                    count_text = count.get_text(strip=True)
                    count_match = re.search(r"\((\d+)\)", count_text)
                    count_num = count_match.group(1) if count_match else "0"
                else:
                    count_num = "0"
                
                return {
                    "rating": f"{rating_num.replace(',', '.')} de 5",
                    "rating_count": f"{count_num} reseñas"
                }
            except Exception as e:
                self.logger.warning(f"Error extrayendo rating: {str(e)}")
                return default
        
        # Lógica genérica para otras tiendas
        texto_puntuacion = self.extraer_texto(elemento, selector)
        if not texto_puntuacion:
            return default
            
        match = re.search(
            r"Calificación (\d+,\d+) de (\d+) \((\d+) calificaciones\)", 
            texto_puntuacion
        )
        if not match:
            return default
            
        return {
            "rating": f"{match.group(1).replace(',', '.')} de {match.group(2)}",
            "rating_count": f"{match.group(3)} comentarios"
        }

    def extraer_url(self, elemento: Tag, selector: Dict) -> str:
        """Construye URL absoluta (compatible con Alkosto y ML)"""
        if not selector:
            return self.url
            
        link_element = elemento.find(
            selector["tag"], 
            class_=selector.get("class"))
        if not link_element or selector["attr"] not in link_element.attrs:
            return self.url
            
        url = urljoin(self.url, link_element[selector["attr"]])
        
        if self.tienda == "alkosto":
            return url.split("?")[0] 
        
        return url
    
    def extraer_descripcion(self, elemento: Tag, selector: Dict) -> Union[str, List]:
        """
        Extrae y formatea la descripción de Alkosto desde 
        key features.
        """
        if not selector or self.tienda != "alkosto":
            return ""
        
        contenedor = elemento.find(selector["tag"], class_=selector.get("class"))
        if not contenedor:
            return ""
        
        items = contenedor.find_all("li", class_="item")
        descripcion = []
        
        for item in items:
            key_element = item.find("div", class_="item--key")
            value_element = item.find("div", class_="item--value")
            if key_element and value_element:
                descripcion.append(
                    f"{key_element.get_text(strip=True)}: "
                    f"{value_element.get_text(strip=True)}"
                )
        
        if not descripcion:
            return ""
        
        result = []
        for item in descripcion:
            if ": " in item:
                key, value = item.split(": ", 1)
                result.append({"-": key, "": value})
        
        return result

    def validar_resultados(self, productos: List[Dict]):
        """Valida y registra resultados del parseo"""
        if not productos:
            self.logger.warning("No se encontraron productos")
            return
            
        self.logger.info(f"Productos extraídos: {len(productos)}")
        self.logger.debug(f"Primer producto: {productos[0]}")
        
        if len(productos) < self.num_productos:
            self.logger.warning(
                f"Se solicitaron {self.num_productos} productos pero "
                f"solo se encontraron {len(productos)}"
            )

    def store(self) -> bool:
        """Implementación concreta del método abstracto"""
        try:
            if not self.data:
                self.logger.warning("No hay datos para almacenar")
                return False
            
            handler = DataHandler(
                self.data, 
                storage_format='both',
                logger=self.logger
            )
            return handler.store_data(url=self.url, tipo="e-commerce")
        
        except Exception as e:
            self.logger.error(f"Error almacenando datos: {str(e)}")
            return False

# Lugar para pruebas unitarias...
if __name__ == "__main__":
    from src.utils.logger import setup_logger
    setup_logger({
        'name': 'EcommerceExtractor',
        'level': 'DEBUG',
        'log_dir': 'logs',
        'enable_console': True
    })
    
    # Prueba MercadoLibre
    try:
        url = "https://listado.mercadolibre.com.co/computadores"
        extractor = EcommerceExtractor(url, 
                                    num_productos=1, 
                                    tienda="mercadolibre")
        productos = extractor.scrape() or []
        
        print("\n:) Resultados obtenidos:")
        for idx, prod in enumerate(productos[:3], 1):
            print(f"\nProducto #{idx}")
            print(f"Título: {prod.get('title', 'Sin título')}")
            print(f"Precio: {prod.get('price_sell', 'N/A')}")
            print(f"Descuento: {prod.get('discount', '0%')}")
            print(f"URL: {prod.get('url', '#')[:60]}...")
            
        if extractor.data:
            print("\n:) Datos guardados exitosamente de Mercadolibre")
                
    except Exception as e:
        logging.error(f":( Error en ejecución: {str(e)}", exc_info=True)

    # Configuración para Alkosto
    try:
        url_alkosto = "https://www.alkosto.com/search?text=lavadoras"
        extractor_alkosto = EcommerceExtractor(
            url_alkosto, num_productos=1, 
            tienda="alkosto")
        productos_alkosto = extractor_alkosto.scrape() or []
        
        print("\nResultados Alkosto:")
        for idx, prod in enumerate(productos_alkosto, 1):
            print(f"\nProducto #{idx}")
            print(f"Título: {prod.get('title', 'Sin título')}")
            print(f"Precio: {prod.get('price_sell', 'N/A')}")
            print(f"Descuento: {prod.get('discount', '0%')}")
            print(f"URL: {prod.get('url', '#')[:60]}...")
            
        if extractor_alkosto.data:
            print("\n :)Datos de Alkosto guardados en JSON.")
                
    except Exception as e:
        logging.error(f":( Error en Alkosto: {str(e)}", exc_info=True)