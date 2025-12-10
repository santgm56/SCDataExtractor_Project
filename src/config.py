"""
Módulo os:
Permite interactuar con funcionalidades dependientes del sistema 
operativo.
Fuente: https://docs.python.org/es/3.10/library/os.html
"""
import os

# Carpeta esencial para almacenar los archivos de salida
OUTPUT_DIR = 'outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)


DYNAMIC_TIMEOUT = 25  

USER_AGENT_DINAMICOS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Parámetros reutilizables para paginación dinámica
PAGINACION_ML = {
    "page_size": 48,  # MercadoLibre muestra ~48 items por página
    "url_suffix": "_NoIndex_True",  # sufijo estándar observado
}

SELECTORES_LISTA_DINAMICOS = {
    "mercadolibre": {
        "producto": {"tag": "li", "class": "ui-search-layout__item"},
        "url": {
            "tag": "a", 
            "class": "poly-component__title", 
            "attr": "href"}, 
        "title": {"tag": "a", "class": "poly-component__title"},
        "image": {
            "tag": "img", 
            "class": "poly-component__picture", 
            "attr": "src"  
        },
        "price_sell": {
            "tag": "span", 
            "class": "andes-money-amount--cents-superscript",
            "currency_symbol": {  # Selector anidado para el símbolo
                "tag": "span", 
                "class": "andes-money-amount__currency-symbol"
            },
            "fraction": {  # Selector anidado para el valor numérico
                "tag": "span", 
                "class": "andes-money-amount__fraction"
            }
        },
        "price_original": {
            "tag": "s", 
            "class": "andes-money-amount--previous",
            "currency_symbol": { 
                "tag": "span", 
                "class": "andes-money-amount__currency-symbol"
            },
            "fraction": { 
                "tag": "span", 
                "class": "andes-money-amount__fraction"
            }
        },
        "rating": {
        "tag": "div",
        "class": "poly-component__reviews"
        },
        "discount": {
            "tag": "span", 
            "class": "andes-money-amount__discount"
        }
    },
    "alkosto": {
        "producto": {
            "tag": "li", 
            "class": "ais-InfiniteHits-item"
        },
        "title": {
            "tag": "h3", 
            "class": "product__item__top__title"
        },
        "image": {
        "tag": "div", 
        "class": "product__item__information__image",
        "sub_element": {"tag": "img"},  # Buscar img dentro del div
        "attr": "src"
    },
        "price_original": {
        "tag": "p", 
        "class": "product__price--discounts__old",
        "currency_symbol": {"tag": "span"}, 
        "fraction": {"tag": None}  
        },
        "price_sell": {
            "tag": "span", 
            "class": "price",
            "currency_symbol": {"tag": "span"},  
            "fraction": {"tag": None}  
        },
        "discount": {
            "tag": "div",
            "class": "discount-label--newDesign",
            "sub_element": {
                "tag": "span",
                "class": "label-offer"
            }
        },
        "rating": {
            "tag": "div", 
            "class": "product__item__top__rating",
            "sub_element": {
                "tag": "span",
                "class": "averageNumber"  
            }
        },
        "rating_count": { 
            "tag": "span",
            "class": "review"
        },
        "url": {
        "tag": "a", 
        "class": "product__item__top__link", 
        "attr": "href"
        },
        "description": {
        "tag": "ul", 
        "class": "product__item__information__key-features--list"
        }
    }
}