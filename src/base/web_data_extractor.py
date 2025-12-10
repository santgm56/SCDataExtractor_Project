"""
Descripción:
    Para este módulo se define la clase abstracta WebDataExtractor que 
    establece la interfaz y el flujo base para la extracción de datos 
    de páginas web. Las clases hijas (por ejemplo, para páginas 
    estáticas o dinámicas) deberán implementar los métodos abstractos 
    definidos en esta clase.  
"""

from abc import ABC, abstractmethod
import logging

class WebDataExtractor(ABC):
    """
    Clase abstracta base para la extracción de datos web.

    Define el flujo de trabajo básico:
        1. Descargar el contenido HTML de la URL.
        2. Parsear el contenido para extraer la información deseada.
        3. Almacenar o procesar los datos extraídos.

    Además, provee un método generador para iterar sobre los datos 
    extraídos, permitiendo un manejo eficiente de la memoria en grandes volúmenes de datos.
    """

    def __init__(self, url):
        """
        Inicializa el extractor con la URL que se va a procesar.

        :param url: Dirección web del recurso a scrapear.
        """
        # Se asigna la URL proporcionada al atributo url de la instancia
        self.__url = url  
        # Se inicializa el atributo html_content como None. 
        # Este atributo almacenará el contenido HTML descargado          
        self.__html_content = None
        # Se inicializa una lista vacía llamada data para almacenar 
        # los datos extraídos.   
        self.__data = []
        # Se crea un logger con el nombre de la clase actual.          
        self.logger = logging.getLogger(self.__class__.__name__)
        # Se configura el nivel de logging a DEBUG, lo que permite 
        # registrar mensajes de todos los niveles.
        self.logger.setLevel(logging.DEBUG)

    # Getters y Setters para url
    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    # Getters y Setters para html_content
    @property
    def html_content(self):
        return self.__html_content

    @html_content.setter
    def html_content(self, value):
        self.__html_content = value

    # Getters y Setters para data
    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        # Permite dict o list, y convierte dict en [dict]
        if not isinstance(value, (dict, list)):
            raise ValueError(
                "El valor debe ser un diccionario o lista.")
        self.__data = value if isinstance(value, list) else [value]

    @abstractmethod
    def download(self):
        """
        Método abstracto para descargar el contenido HTML de la URL.

        Debe ser implementado por las subclases (por ejemplo, usando 
        Requests para páginas estáticas o Selenium/Playwright para 
        páginas dinámicas).
        """
        raise NotImplementedError(
            "Este método debe ser redefinido en las clases hijas."
            )

    @abstractmethod
    def parse(self):
        """
        Método abstracto para parsear el contenido HTML descargado y 
        extraer la información.

        La implementación deberá transformar el HTML en una estructura 
        de datos (por ejemplo, lista o diccionario)
        que contenga la información requerida.
        """
        raise NotImplementedError(
            "Este método debe ser redefinido en las clases hijas."
            )

    @abstractmethod
    def store(self):
        """
        Método abstracto para almacenar la información extraída.

        Este método se podrá utilizar para guardar los datos en JSON, 
        base de datos u otro formato. Debe devolver True si el
        almacenamiento fue exitoso o False en caso contrario.
        """
        raise NotImplementedError(
            "Este método debe ser redefinido en las clases hijas."
            )

    def scrape(self):
        """
        Organiza el proceso completo de scraping:
            1. Descarga del contenido HTML.
            2. Parseo del contenido para extraer datos.
            3. Almacenamiento de los datos extraídos.

        Devuelve una lista de datos o None si ocurre un error.
        """
        try:
            self.logger.info(
                f"Iniciando proceso de scraping para URL: {self.url}"
                )
            
            # Llama al método download para obtener el contenido HTML.
            self.html_content = self.download()
            # Verifica si el contenido HTML se descargó correctamente.
            if not self.html_content:
                # Registra un mensaje de error si no se pudo descargar 
                # el contenido.
                self.logger.error(
                    "No se pudo descargar el contenido HTML de la URL: " 
                    f"{self.url}."
                    )
                return None
            self.logger.debug(
                "Contenido HTML descargado correctamente."
                )
            
            # Llama al método parse para extraer datos del HTML.
            self.data = self.parse()
            self.logger.debug(
                f"Parseo completado. Se extrajeron {len(self.data)} "
                "elementos."
                )
            
            # Llama al método store para el almacenamiento o 
            # procesamiento posterior de los datos
            if self.store():
                self.logger.info("Datos almacenados exitosamente.")
            else:
                self.logger.warning(
                    "El proceso de almacenamiento de datos falló."
                    )
            
            return self.data

        except Exception as e:
            self.logger.exception(
                f"Error durante el proceso de scraping: {str(e)}"
                )
            return None

    def iter_data(self):
        """
        Método generador que permite iterar sobre los datos extraídos 
        de forma eficiente.
        """
        if not self.data:
            self.logger.warning(
                "No hay datos en caché. Ejecutando el proceso de scraping"
                )
            self.data = self.scrape() or []
            if not self.data:
                self.logger.error(
                    "Lo siento. No se pudo extraer datos durante el "
                    "proceso de scraping. Debe verificar la URL o el "
                    "proceso de scraping."
                    )
                return
        for item in self.data:
            # Devuelve cada elemento uno por uno, sin cargar toda la 
            # lista en memoria.
            yield item
