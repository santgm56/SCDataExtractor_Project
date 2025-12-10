# 📋 Guía de Instalación y Configuración

## 🎯 ¿Qué se implementó?

Se ha agregado **persistencia en base de datos SQLite** al sistema de scraping. Esto significa que:
- Los productos **NO se pierden** cuando se cierra el programa
- Se acumulan en una base de datos `historial_productos.db`
- Cada vez se ejecuta, los productos **se cargan automáticamente**

---

## 🚀 Inicio Rápido

### **Primera vez (después de `git pull`):**

```powershell
cd App
.\setup.ps1      # Solo se ejecuta UNA vez - descarga las librerías
.\compile.ps1    # Compila el código
.\run.ps1        # Ejecuta el programa con persistencia
```

### **Después de modificar el código en Java se debe:**

```powershell
cd App
.\compile.ps1    # Recompila
.\run.ps1        # Ejecuta
```

---

## ⚠️ IMPORTANTE: PowerShell Scripts vs Botón Run de VS Code

### **El Problema**

VS Code tiene un bug en su Java Language Server que causa este error:

```
Exception in thread "main" java.lang.NoClassDefFoundError: org/sqlite/JDBC
```

### **La Causa**

El botón **Run** de VS Code usa este classpath:
```bash
-cp "bin/"  # FALTA libs/
```

Pero nuestro `run.ps1` usa:
```bash
-cp "bin;libs/*"  # INCLUYE todas las librerías (SQLite, SLF4J)
```

### **La Solución**

**Usar PowerShell Scripts:**

```powershell
cd App
.\run.ps1
```

**Alternativa (Avanzado):** Configurar `launch.json` en `.vscode/` para que el botón Run funcione correctamente.

---

## 📂 Archivos del Sistema

| Archivo | ¿Qué hace? | ¿Modificar? |
|---------|------------|-------------|
| `HistorialDB.java` | Maneja la base de datos SQLite |NO |
| `DataManager.java` | Coordinador principal (scraping + BD) | Solo si es necesario para implementar las demás estructuras |
| `App.java` | Menú interactivo (punto de entrada) |Sí (para agregar opciones) |
| `Producto.java` | Modelo de datos |NO |
| `RunPython.java` | Puente Java ↔ Python |NO |
| `setup.ps1` | Descarga las 3 librerías JAR necesarias |NO |
| `compile.ps1` | Compila con las librerías en el classpath | NO |
| `run.ps1` | Ejecuta con el classpath correcto | NO |
| `.gitignore` | Ignora `libs/`, `bin/`, `*.db` | NO |

---

## 🗄️ Base de Datos SQLite

### **Ubicación:**
```
App/historial_productos.db
```

### **Estructura:**
```sql
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    precio_original TEXT,
    precio_venta TEXT NOT NULL,
    descuento TEXT,
    imagen TEXT,
    url TEXT,
    tienda TEXT NOT NULL,
    calificacion TEXT,
    descripcion TEXT,
    precio_numerico REAL,
    fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### **IMPORTANTE:**
- ⚠️ **NO subir** `historial_productos.db` a Git (está en `.gitignore`)
- ⚠️ **NO subir** carpetas `libs/` y `bin/` a Git

---

## 🧪 Validar que Funciona

### **Test 1: Persistencia Básica**

```powershell
# Primera ejecución
cd App
.\run.ps1
# → Escoge opción 1 (scraping)
# → Buscar "laptop", 3 items, 1 página
# → Escoge opción 6 (salir)

# Segunda ejecución
.\run.ps1
# → DEBE mostrar "Historial cargado: 3 productos"
# → Escoge opción 2 para ver los productos
# → DEBEN aparecer los 3 anteriores
```

### **Test 2: Acumulación**

```powershell
.\run.ps1
# → Opción 1: Hacer scraping (3 productos más)
# → Total debe ser 6 productos
# → Opción 6: Salir

.\run.ps1
# → DEBE mostrar "Historial cargado: 6 productos"
```

---

## 🐛 Solución de Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `NoClassDefFoundError: org/sqlite/JDBC` | Usaste botón Run de VS Code | Ejecuta con `.\run.ps1` |
| `No existe bin/App.class` | No compilaste | Ejecuta `.\compile.ps1` |
| `libs/sqlite-jdbc-3.44.0.0.jar no encontrado` | No descargaste librerías | Ejecuta `.\setup.ps1` |
| `BD no se limpia con "Limpiar historial"` | Archivo bloqueado | Cierra programa (opción 6) antes de borrar |
| `Scanner closed` error | Cerraste scanner prematuramente | Usa opción 6 para salir correctamente |

---

## 🔍 Verificación Rápida

Si algo no funciona, revisar:

1. ¿Estás en la carpeta `App/`?
2. ¿Ejecutaste `setup.ps1` alguna vez?
3. ¿Usaste `run.ps1` o el botón de VS Code?
4. ¿Compilaste con `compile.ps1` después de hacer cambios?

---

## 📚 Documentación Adicional

- **Para desarrolladores:** Leer [`ARQUITECTURA.md`](ARQUITECTURA.md)
- **Para implementar BST/Heap/GUI:** Leer [`DESARROLLO.md`](DESARROLLO.md)

---

**Última actualización:** 2025-11-29  
