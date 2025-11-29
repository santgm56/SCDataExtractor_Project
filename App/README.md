# 🛒 App Java - Sistema de Scraping con Persistencia SQLite

Aplicación Java que gestiona y almacena productos scrapeados de e-commerce (MercadoLibre y Alkosto) con persistencia en base de datos SQLite.

---

## 🚀 Inicio Rápido

### **Primera vez:**

```powershell
.\setup.ps1      # Descarga librerías SQLite + SLF4J
.\compile.ps1    # Compila el proyecto
.\run.ps1        # Ejecuta la aplicación
```

### **Después de modificar código:**

```powershell
.\compile.ps1
.\run.ps1
```

**IMPORTANTE:** Usa siempre `.\run.ps1` (NO el botón Run de VS Code). [Ver por qué](docs/INSTALACION.md#importante-powershell-scripts-vs-botón-run-de-vs-code)

---

## 📁 Estructura del Proyecto

```
App/
├── src/                         # Código fuente Java
│   ├── App.java                # Menú interactivo (punto de entrada)
│   ├── DataManager.java        # Coordinador principal
│   ├── HistorialDB.java        # Persistencia SQLite
│   ├── Producto.java           # Modelo de datos
│   └── RunPython.java          # Puente Java ↔ Python
├── bin/                         # Archivos compilados (.class) - NO subir a Git
├── libs/                        # Librerías JAR (SQLite, SLF4J) - NO subir a Git
├── docs/                        # Documentación
│   ├── INSTALACION.md          # Guía de instalación
│   ├── ARQUITECTURA.md         # Arquitectura técnica
│   └── DESARROLLO.md           # Guía para BST/Heap/GUI
├── setup.ps1                    # Script de instalación
├── compile.ps1                  # Script de compilación
├── run.ps1                      # Script de ejecución
├── historial_productos.db       # Base de datos SQLite - NO subir a Git
└── .gitignore                   # Excluye libs/, bin/, *.db
```

---

## Características

- **Persistencia SQLite** - Productos sobreviven al cierre
- **Sincronización RAM ↔ BD** - ArrayList + Base de Datos
- **Menú interactivo** - 6 opciones funcionales
- **Scraping automatizado** - Integración con Python
- **BST y Heap** - En desarrollo
- **GUI** - En desarrollo

---

## 🗄️ Base de Datos

**Ubicación:** `historial_productos.db`

**Tabla:** `productos` (11 campos + timestamp)

**Operaciones:**
- Insertar productos automáticamente después de cada scraping
- Cargar historial completo al iniciar
- Limpiar historial (con confirmación)
- Eliminar por ID o tienda (métodos disponibles)

---

## 🛠️ Tecnologías

- **Java JDK 21**
- **SQLite JDBC 3.44.0.0** - Persistencia
- **SLF4J 2.0.9** - Logging
- **Python 3.x** - Scraper backend

---

## 📚 Documentación

- 📖 **[docs/INSTALACION.md](docs/INSTALACION.md)** - Guía completa de instalación
- 🏗️ **[docs/ARQUITECTURA.md](docs/ARQUITECTURA.md)** - Arquitectura técnica detallada
- 💻 **[docs/DESARROLLO.md](docs/DESARROLLO.md)** - Implementar BST, Heap y GUI

---

**Última actualización:** 2025-11-29
