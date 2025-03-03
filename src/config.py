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

# <------------------- Para Sitios Estáticos ------------------------->

STATIC_TIMEOUT_ST = 10
RETRY_COUNT_ST = 3
RETRY_DELAY_ST = 2
USER_AGENT_ST = (
    "Mozilla/5.0 (compatible; ScraperBot/1.0; +https://github.com/santgm56/SCDataExtractor_Project)"
    )
SELECTORS_ST_DEFAULT = {
    "title": {"tag": "h1", "id": "firstHeading"},
    "infobox": {"tag": "table", "class": "infobox"},
    "content": {"tag": "div", "id": "mw-content-text"},
    "paragraph": "p",
    "image": {"tag": "img"}
}
SELECTORS_ST_BY_SITE = {
    "wikipedia.org": {
        "title": {"tag": "h1", 
                "id": "firstHeading", 
                "class": "firstHeading mw-first-heading"},
        "infobox": {"tag": "table", "class": "infobox"},
        "content": {"tag": "div", "class": "mw-parser-output"},
        "paragraph": "p",
        "image": {"tag": "img", "parent": [
        {"tag": "div", "class": "mw-parser-output"},  # Artículo principal
        {"tag": "table", "class": "infobox"}  # Imágenes de la infobox
        ]},
        "lists": {"tag": "ul", "parent": {"tag": "div", "class": "mw-parser-output"}},
        "tables": {"tag": "table"}
    },
    "fandom.com": {
        "title": {"tag": "h1", "id": "firstHeading", "class": "page-header__title"},
        "infobox": {"tag": "aside", "class": "portable-infobox"},
        "content": {"tag": "div", "class": "mw-parser-output"},
        "paragraph": "p",
        "image": {"tag": "img", "class": "gallery-icon-container view-image"},
        "lists": {"tag": "div", "class": "quotebox"},
        "tables": {"tag": "table", "class": "wikitable"}
    }
}

CACHE_DIR = 'cache'
# Crea la carpeta si no existe
os.makedirs(CACHE_DIR, exist_ok=True)


# <------------------- Para Sitios Dinámicos ------------------------->

DYNAMIC_TIMEOUT = 25  

USER_AGENT_DINAMICOS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

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
    },   
    "metrocuadrado": {
        "propiedad": {
            "tag": "li",
            "class": ["sc-gPEVay", "dibcyk"],  # Clases como lista
            "children": {
                "title": {
                    "tag": "h2",
                    "class": ["sc-dxgOiQ", "BSoGx", "card-title"],
                    "sub_element": {"tag": "div"}
                },
                "price": {
                    "tag": "li",
                    "contexto": {"texto_padre": "Precio de venta"},
                    "sub_element": {"tag": "p", "class": "ZUMHA"}
                },
                "area": {
                    "tag": "li",
                    "contexto": {"texto_padre": "Área Construida"},
                    "sub_element": {"tag": "p", "class": "ZUMHA"}
                },
                "rooms": {
                    "tag": "li",
                    "contexto": {"texto_padre": "Hab."},
                    "sub_element": {"tag": "p", "class": "ZUMHA"}
                },
                "baths": {
                    "tag": "li",
                    "contexto": {"texto_padre": "Baños"},
                    "sub_element": {"tag": "p", "class": "ZUMHA"}
                },
                "url": {
                    "tag": "a",
                    "class": ["sc-bdVaJa", "ebNrSm"],  # Clases como lista
                    "attr": "href",
                    "padre": {
                        "tag": "div",
                        "class": ["card-header"]  # Clases como lista
                    }
                }
            }
        }
    }
}