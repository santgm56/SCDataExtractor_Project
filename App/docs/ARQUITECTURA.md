# 🏗️ ARQUITECTURA TÉCNICA DEL SISTEMA - Guía para Desarrolladores

## 📐 Visión General de la Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        App.java                             │
│                  (Menú Interactivo)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    DataManager.java                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ArrayList<Producto> historialProductos              │   │
│  │  (Estructura principal en RAM)                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│         ┌────────────────┼────────────────┐                 │
│         ▼                ▼                ▼                 │
│   ┌─────────┐    ┌─────────────┐   ┌──────────┐            │
│   │RunPython│    │HistorialDB  │   │Producto  │            │
│   │  .java  │    │   .java     │   │  .java   │            │
│   └─────────┘    └─────────────┘   └──────────┘            │
│        │                │                                    │
└────────┼────────────────┼────────────────────────────────────┘
         │                │
         ▼                ▼
  ┌────────────┐   ┌──────────────────┐
  │   Python   │   │  SQLite Database │
  │  Scraper   │   │ historial_       │
  │   (venv)   │   │ productos.db     │
  └────────────┘   └──────────────────┘
```

---

## 🔄 Flujo de Datos Completo

### 1. **Al Iniciar el Programa**

```java
// App.java - main()
DataManager manager = new DataManager();
```

**¿Qué pasa internamente?**

```java
// DataManager.java - constructor
public DataManager() {
    this.database = new HistorialDB();  // ← Paso 1
    this.historialProductos = new ArrayList<>();
    this.historialProductos = database.cargarTodosProductos();  // ← Paso 2
}
```

**Paso 1: `new HistorialDB()`**
```java
// HistorialDB.java
public HistorialDB() {
    Class.forName("org.sqlite.JDBC");  // Carga el driver
    conectar();  // Abre conexión a historial_productos.db
    crearTabla();  // CREATE TABLE IF NOT EXISTS productos
}
```

**Paso 2: `database.cargarTodosProductos()`**
```sql
SELECT * FROM productos ORDER BY id ASC
```
- Crea un `ArrayList<Producto>` temporal
- Por cada fila del `ResultSet`:
  - Crea un `new Producto(...)` con los datos
  - Lo agrega al ArrayList
- Retorna el ArrayList completo

**Resultado:**
```
✓ Conexión a SQLite establecida
✓ Tabla productos verificada/creada
✓ Cargados 12 productos desde BD

Historial cargado: 12 productos
```

---

### 2. **Al Hacer un Scraping (Opción 1 del menú)**

```java
// App.java
manager.aggDatosHistorial(1, "laptop", 10, 2, true);
```

**Flujo completo:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DataManager.aggDatosHistorial()                          │
│    ├─ Llama a RunPython.ejecutarScraping()                  │
│    │   └─ Ejecuta: venv\Scripts\python.exe main.py ...      │
│    │       └─ Python scraper devuelve JSON en stdout        │
│    │                                                         │
│    ├─ RunPython.ejecutarScraping() retorna List<String>     │
│    │   (cada línea del output de Python)                    │
│    │                                                         │
│    └─ procesarJSONReal(List<String>)                        │
│        └─ Por cada línea que contiene JSON:                 │
│            ├─ Extrae el JSON entre { y }                    │
│            ├─ extraerProductoDeJSON(String json)            │
│            │   └─ Regex para extraer campos                 │
│            │       ('title': 'valor', 'price_sell': ...)    │
│            │                                                 │
│            ├─ new Producto(titulo, precio, ...)             │
│            ├─ historialProductos.add(producto)  ← RAM       │
│            └─ database.insertarProducto(producto) ← BD      │
└─────────────────────────────────────────────────────────────┘
```

**En la Base de Datos:**

```java
// HistorialDB.insertarProducto()
String sql = """
    INSERT INTO productos (titulo, precio_original, precio_venta, 
                         descuento, imagen, url, tienda, 
                         calificacion, descripcion, precio_numerico)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """;
PreparedStatement pstmt = conexion.prepareStatement(sql);
pstmt.setString(1, producto.getTitulo());
pstmt.setString(2, producto.getPrecioOriginal());
// ... etc
pstmt.executeUpdate();
```

**Resultado:**
```
✓ Producto guardado en BD: Laptop HP 15 pulgadas Intel Core i5...
✓ Producto guardado en BD: Laptop Lenovo IdeaPad 3 AMD Ryzen 5...
✓ Producto guardado en BD: Laptop ASUS VivoBook 14 Intel Core i3...

Scraping completado. Total en historial: 15
```

---

### 3. **Al Ver Productos (Opción 2 del menú)**

```java
// App.java
ArrayList<Producto> productos = manager.getHistorialCompleto();
```

**¿Qué pasa?**

```java
// DataManager.java
public ArrayList<Producto> getHistorialCompleto() {
    return new ArrayList<>(historialProductos);  // Copia defensiva
}
```

**IMPORTANTE:** Esto NO consulta la BD, solo devuelve una copia del ArrayList en RAM.

**¿Por qué?**
- El ArrayList ya está sincronizado con la BD
- Más rápido (O(1) vs consulta SQL)
- La BD solo se consulta al inicio y cuando se eliminan productos

---

### 4. **Al Eliminar un Producto**

```java
// Si agregas esta función al menú:
manager.eliminarProducto(5);  // Elimina el producto con ID=5
```

**Flujo:**

```java
// DataManager.java
public boolean eliminarProducto(int id) {
    boolean eliminado = database.eliminarProducto(id);  // ← BD
    if (eliminado) {
        historialProductos = database.cargarTodosProductos();  // ← Recarga
    }
    return eliminado;
}
```

**En la BD:**

```sql
DELETE FROM productos WHERE id = 5
```

**Luego:**

```sql
SELECT * FROM productos ORDER BY id ASC
```

**¿Por qué recargar todo?**
- Garantiza sincronización 100% entre RAM y BD
- Más simple que buscar y eliminar del ArrayList manualmente
- Pequeño overhead aceptable (la BD está en disco local)

---

## 🧩 Componentes del Sistema

### **1. Producto.java** (Modelo de Datos)

```java
public class Producto {
    // Campos obligatorios
    private String titulo;
    private String precioOriginal;
    private String precioVenta;
    private String descuento;
    private String imagen;
    private String url;
    private String tienda;
    
    // Campos opcionales
    private String calificacion;
    private String descripcion;
    private double precioNumerico;
}
```

**Responsabilidades:**
- Almacenar información de un producto
- Getters y setters
- **NO tiene lógica de negocio**

---

### **2. HistorialDB.java** (Capa de Persistencia)

```java
public class HistorialDB {
    private Connection conexion;
    
    // MÉTODOS PÚBLICOS:
    public void insertarProducto(Producto p)
    public ArrayList<Producto> cargarTodosProductos()
    public int contarProductos()
    public boolean eliminarProducto(int id)
    public int eliminarPorTienda(String tienda)
    public void limpiarHistorial()
    public void cerrar()
}
```

**Responsabilidades:**
- Gestionar conexión SQLite
- CRUD completo (Create, Read, Update, Delete)
- Convertir filas de BD → objetos `Producto`
- Convertir objetos `Producto` → filas de BD
- **NO conoce la lógica de scraping**

**Tabla en SQLite:**

```sql
CREATE TABLE IF NOT EXISTS productos (
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

---

### **3. DataManager.java** (Controlador Principal)

```java
public class DataManager {
    private ArrayList<Producto> historialProductos;  // ← RAM
    private HistorialDB database;  // ← BD
    
    // MÉTODOS PÚBLICOS:
    public void aggDatosHistorial(...)  // Scraping + guardar
    public ArrayList<Producto> getHistorialCompleto()  // Lectura
    public int getTotalProductos()  // Estadísticas
    public boolean eliminarProducto(int id)  // Eliminación
    public int eliminarPorTienda(String tienda)  // Eliminación masiva
    public void limpiarHistorial()  // Borrar todo
    public void cerrarDB()  // Cierre limpio
}
```

**Responsabilidades:**
- Coordinar RunPython + HistorialDB
- Mantener sincronización RAM ↔ BD
- Procesar JSON del scraper
- Exponer API simple para App.java o GUI

**Principio clave:**
```
┌──────────────────────────────────────┐
│  ArrayList es el MASTER en RAM       │
│  BD es el BACKUP persistente         │
│                                       │
│  Cada inserción → RAM + BD           │
│  Cada eliminación → BD + reload RAM  │
└──────────────────────────────────────┘
```

---

### **4. RunPython.java** (Interfaz con Python)

```java
public class RunPython {
    private static final String PYTHON_PATH = "..\\venv\\Scripts\\python.exe";
    private static final String SCRIPT_PATH = "..\\main.py";
    
    public static List<String> ejecutarScraping(...) {
        ProcessBuilder pb = new ProcessBuilder(
            PYTHON_PATH, SCRIPT_PATH,
            String.valueOf(tienda),
            producto,
            // ... más args
        );
        
        Process proceso = pb.start();
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(proceso.getInputStream())
        );
        
        List<String> salida = new ArrayList<>();
        String linea;
        while ((linea = reader.readLine()) != null) {
            salida.add(linea);
        }
        
        return salida;
    }
}
```

**Responsabilidades:**
- Ejecutar el script de Python
- Capturar stdout (salida del scraper)
- Convertir a `List<String>` para DataManager
- **NO procesa JSON** (eso lo hace DataManager)

---

## 🌲 ¿Cómo Implementar BST y Heap?

### **Opción A: Estructuras Independientes** (Recomendado)

```java
// BST.java (nuevo archivo en src/)
public class BST {
    private class Nodo {
        Producto producto;
        Nodo izquierdo;
        Nodo derecho;
        
        Nodo(Producto p) {
            this.producto = p;
        }
    }
    
    private Nodo raiz;
    
    // Constructor: recibe el ArrayList del DataManager
    public BST(ArrayList<Producto> productos) {
        this.raiz = null;
        for (Producto p : productos) {
            insertar(p);
        }
    }
    
    public void insertar(Producto p) {
        raiz = insertarRecursivo(raiz, p);
    }
    
    private Nodo insertarRecursivo(Nodo nodo, Producto p) {
        if (nodo == null) {
            return new Nodo(p);
        }
        
        // Ordenar por precio numérico
        if (p.getPrecioNumerico() < nodo.producto.getPrecioNumerico()) {
            nodo.izquierdo = insertarRecursivo(nodo.izquierdo, p);
        } else {
            nodo.derecho = insertarRecursivo(nodo.derecho, p);
        }
        
        return nodo;
    }
    
    // Buscar productos en rango de precios
    public ArrayList<Producto> buscarEnRango(double min, double max) {
        ArrayList<Producto> resultado = new ArrayList<>();
        buscarEnRangoRecursivo(raiz, min, max, resultado);
        return resultado;
    }
    
    private void buscarEnRangoRecursivo(Nodo nodo, double min, double max, 
                                        ArrayList<Producto> resultado) {
        if (nodo == null) return;
        
        double precio = nodo.producto.getPrecioNumerico();
        
        if (precio >= min && precio <= max) {
            resultado.add(nodo.producto);
        }
        
        if (precio > min) {
            buscarEnRangoRecursivo(nodo.izquierdo, min, max, resultado);
        }
        if (precio < max) {
            buscarEnRangoRecursivo(nodo.derecho, min, max, resultado);
        }
    }
    
    // Recorrido inorden (ordenado por precio)
    public ArrayList<Producto> getOrdenadoPorPrecio() {
        ArrayList<Producto> resultado = new ArrayList<>();
        inorden(raiz, resultado);
        return resultado;
    }
    
    private void inorden(Nodo nodo, ArrayList<Producto> resultado) {
        if (nodo == null) return;
        inorden(nodo.izquierdo, resultado);
        resultado.add(nodo.producto);
        inorden(nodo.derecho, resultado);
    }
}
```

**Uso desde App.java o GUI:**

```java
// Obtener datos del DataManager
ArrayList<Producto> productos = manager.getHistorialCompleto();

// Construir BST
BST arbol = new BST(productos);

// Buscar productos entre $500,000 y $1,000,000
ArrayList<Producto> enRango = arbol.buscarEnRango(500000, 1000000);

// Obtener productos ordenados por precio
ArrayList<Producto> ordenados = arbol.getOrdenadoPorPrecio();
```

---

### **Heap.java** (Min-Heap para encontrar más baratos)

```java
// Heap.java (nuevo archivo en src/)
public class Heap {
    private ArrayList<Producto> heap;
    
    public Heap(ArrayList<Producto> productos) {
        this.heap = new ArrayList<>(productos);
        construirHeap();
    }
    
    private void construirHeap() {
        // Heapify desde el último padre hasta la raíz
        for (int i = heap.size() / 2 - 1; i >= 0; i--) {
            heapifyDown(i);
        }
    }
    
    private void heapifyDown(int index) {
        int menor = index;
        int izq = 2 * index + 1;
        int der = 2 * index + 2;
        
        if (izq < heap.size() && 
            heap.get(izq).getPrecioNumerico() < heap.get(menor).getPrecioNumerico()) {
            menor = izq;
        }
        
        if (der < heap.size() && 
            heap.get(der).getPrecioNumerico() < heap.get(menor).getPrecioNumerico()) {
            menor = der;
        }
        
        if (menor != index) {
            // Swap
            Producto temp = heap.get(index);
            heap.set(index, heap.get(menor));
            heap.set(menor, temp);
            
            heapifyDown(menor);
        }
    }
    
    // Obtener el producto más barato (raíz del min-heap)
    public Producto getMasBarato() {
        if (heap.isEmpty()) return null;
        return heap.get(0);
    }
    
    // Obtener los N productos más baratos
    public ArrayList<Producto> getNMasBaratos(int n) {
        ArrayList<Producto> resultado = new ArrayList<>();
        Heap copia = new Heap(new ArrayList<>(heap));  // Copia para no destruir
        
        for (int i = 0; i < n && !copia.heap.isEmpty(); i++) {
            resultado.add(copia.extraerMinimo());
        }
        
        return resultado;
    }
    
    private Producto extraerMinimo() {
        if (heap.isEmpty()) return null;
        
        Producto minimo = heap.get(0);
        Producto ultimo = heap.remove(heap.size() - 1);
        
        if (!heap.isEmpty()) {
            heap.set(0, ultimo);
            heapifyDown(0);
        }
        
        return minimo;
    }
}
```

**Uso:**

```java
ArrayList<Producto> productos = manager.getHistorialCompleto();
Heap heap = new Heap(productos);

// Producto más barato
Producto masBarato = heap.getMasBarato();
System.out.println("Más barato: " + masBarato.getTitulo() + 
                   " - " + masBarato.getPrecioVenta());

// Top 5 más baratos
ArrayList<Producto> top5 = heap.getNMasBaratos(5);
for (Producto p : top5) {
    System.out.println(p.getTitulo() + " - " + p.getPrecioVenta());
}
```

---

## 🖥️ Integración con GUI (para el equipo de interfaz)

### **Arquitectura Recomendada:**

```java
// InterfazGrafica.java
import javax.swing.*;
import java.awt.*;

public class InterfazGrafica extends JFrame {
    private DataManager manager;
    private JTable tablaProductos;
    private DefaultTableModel modeloTabla;
    
    public InterfazGrafica() {
        this.manager = new DataManager();  // ← PUNTO DE ENTRADA
        
        inicializarComponentes();
        cargarDatosEnTabla();
    }
    
    private void inicializarComponentes() {
        setTitle("Sistema de Scraping - E-Commerce");
        setSize(1200, 700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        
        // Panel principal con BorderLayout
        JPanel panelPrincipal = new JPanel(new BorderLayout());
        
        // NORTE: Botones de acción
        JPanel panelBotones = new JPanel();
        JButton btnScraping = new JButton("Nuevo Scraping");
        JButton btnOrdenar = new JButton("Ordenar por Precio (BST)");
        JButton btnTop5 = new JButton("Top 5 Baratos (Heap)");
        JButton btnLimpiar = new JButton("Limpiar");
        
        btnScraping.addActionListener(e -> mostrarDialogoScraping());
        btnOrdenar.addActionListener(e -> ordenarPorPrecio());
        btnTop5.addActionListener(e -> mostrarTop5());
        btnLimpiar.addActionListener(e -> limpiarHistorial());
        
        panelBotones.add(btnScraping);
        panelBotones.add(btnOrdenar);
        panelBotones.add(btnTop5);
        panelBotones.add(btnLimpiar);
        
        // CENTRO: Tabla de productos
        String[] columnas = {"Tienda", "Título", "Precio Original", 
                            "Precio Venta", "Descuento"};
        modeloTabla = new DefaultTableModel(columnas, 0);
        tablaProductos = new JTable(modeloTabla);
        JScrollPane scrollPane = new JScrollPane(tablaProductos);
        
        // SUR: Panel de estadísticas
        JPanel panelEstadisticas = new JPanel();
        panelEstadisticas.setPreferredSize(new Dimension(1200, 50));
        
        panelPrincipal.add(panelBotones, BorderLayout.NORTH);
        panelPrincipal.add(scrollPane, BorderLayout.CENTER);
        panelPrincipal.add(panelEstadisticas, BorderLayout.SOUTH);
        
        add(panelPrincipal);
    }
    
    private void cargarDatosEnTabla() {
        modeloTabla.setRowCount(0);  // Limpiar tabla
        
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        
        for (Producto p : productos) {
            Object[] fila = {
                p.getTienda(),
                p.getTitulo(),
                p.getPrecioOriginal(),
                p.getPrecioVenta(),
                p.getDescuento()
            };
            modeloTabla.addRow(fila);
        }
    }
    
    private void mostrarDialogoScraping() {
        // Crear diálogo para pedir datos
        JDialog dialogo = new JDialog(this, "Nuevo Scraping", true);
        dialogo.setLayout(new GridLayout(6, 2, 10, 10));
        
        JComboBox<String> comboTienda = new JComboBox<>(
            new String[]{"MercadoLibre", "Alkosto"}
        );
        JTextField txtProducto = new JTextField();
        JSpinner spinnerItems = new JSpinner(new SpinnerNumberModel(10, 1, 50, 1));
        JSpinner spinnerPaginas = new JSpinner(new SpinnerNumberModel(2, 1, 5, 1));
        JCheckBox chkReporte = new JCheckBox();
        
        dialogo.add(new JLabel("Tienda:"));
        dialogo.add(comboTienda);
        dialogo.add(new JLabel("Producto:"));
        dialogo.add(txtProducto);
        dialogo.add(new JLabel("Items por página:"));
        dialogo.add(spinnerItems);
        dialogo.add(new JLabel("Número de páginas:"));
        dialogo.add(spinnerPaginas);
        dialogo.add(new JLabel("Generar reporte:"));
        dialogo.add(chkReporte);
        
        JButton btnEjecutar = new JButton("Ejecutar");
        btnEjecutar.addActionListener(e -> {
            int tienda = comboTienda.getSelectedIndex() + 1;
            String producto = txtProducto.getText();
            int items = (int) spinnerItems.getValue();
            int paginas = (int) spinnerPaginas.getValue();
            boolean reporte = chkReporte.isSelected();
            
            // ← LLAMADA AL DATAMANAGER
            manager.aggDatosHistorial(tienda, producto, items, paginas, reporte);
            
            cargarDatosEnTabla();  // Refrescar tabla
            dialogo.dispose();
            
            JOptionPane.showMessageDialog(this, 
                "Scraping completado!\nTotal: " + manager.getTotalProductos()
            );
        });
        
        dialogo.add(btnEjecutar);
        dialogo.pack();
        dialogo.setLocationRelativeTo(this);
        dialogo.setVisible(true);
    }
    
    private void ordenarPorPrecio() {
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        BST arbol = new BST(productos);
        ArrayList<Producto> ordenados = arbol.getOrdenadoPorPrecio();
        
        // Actualizar tabla con productos ordenados
        modeloTabla.setRowCount(0);
        for (Producto p : ordenados) {
            Object[] fila = {
                p.getTienda(),
                p.getTitulo(),
                p.getPrecioOriginal(),
                p.getPrecioVenta(),
                p.getDescuento()
            };
            modeloTabla.addRow(fila);
        }
    }
    
    private void mostrarTop5() {
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        Heap heap = new Heap(productos);
        ArrayList<Producto> top5 = heap.getNMasBaratos(5);
        
        // Mostrar en diálogo o actualizar tabla
        StringBuilder sb = new StringBuilder("Top 5 Productos Más Baratos:\n\n");
        for (int i = 0; i < top5.size(); i++) {
            Producto p = top5.get(i);
            sb.append((i + 1)).append(". ")
              .append(p.getTitulo().substring(0, Math.min(50, p.getTitulo().length())))
              .append("\n   ").append(p.getPrecioVenta()).append("\n\n");
        }
        
        JOptionPane.showMessageDialog(this, sb.toString());
    }
    
    private void limpiarHistorial() {
        int confirmacion = JOptionPane.showConfirmDialog(this,
            "¿Estás seguro? Esto eliminará TODOS los productos",
            "Confirmar",
            JOptionPane.YES_NO_OPTION
        );
        
        if (confirmacion == JOptionPane.YES_OPTION) {
            manager.limpiarHistorial();
            cargarDatosEnTabla();
        }
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            InterfazGrafica gui = new InterfazGrafica();
            gui.setVisible(true);
        });
    }
}
```

---

## 📊 Diagrama de Dependencias

```
App.java (main)
    │
    └─── DataManager
            ├─── ArrayList<Producto>
            ├─── HistorialDB
            │      └─── SQLite JDBC
            ├─── RunPython
            │      └─── Python venv
            └─── Producto

BST.java (independiente)
    └─── ArrayList<Producto> (recibido como parámetro)

Heap.java (independiente)
    └─── ArrayList<Producto> (recibido como parámetro)

GUI.java (opcional)
    ├─── DataManager
    ├─── BST
    └─── Heap
```

---

## ⚡ Complejidades Temporales

| Operación | ArrayList | BST (balanceado) | Heap |
|-----------|-----------|------------------|------|
| Insertar | O(1) | O(log n) | O(log n) |
| Buscar | O(n) | O(log n) | O(n) |
| Eliminar | O(n) | O(log n) | O(log n) |
| Obtener mínimo | O(n) | O(log n) | O(1) |
| Ordenar | O(n log n) | O(n) (inorden) | O(n log n) |

**Recomendaciones:**
- **ArrayList**: Almacenamiento principal, iteración completa
- **BST**: Búsquedas por rango de precios, ordenamiento
- **Heap**: Encontrar N productos más baratos/caros rápidamente

---

## 🔐 Garantías de Consistencia

### **Sincronización RAM ↔ BD:**

1. **Al insertar:** `historialProductos.add()` + `database.insertarProducto()` en la misma operación
2. **Al eliminar:** `database.eliminar()` + `historialProductos = database.cargarTodos()`
3. **Al iniciar:** `historialProductos = database.cargarTodos()`

### **¿Qué pasa si el programa se cierra inesperadamente?**

**Los datos están seguros** porque cada inserción se guarda inmediatamente en BD
**No hay rollback** si el scraping falla a mitad (se guardan los productos hasta ese punto)

---

## 🚨 Puntos Críticos

### **1. NO modificar directamente `historialProductos` sin actualizar BD**

**INCORRECTO:**
```java
manager.getHistorialCompleto().clear();  // Solo limpia la copia, no la BD
```

**CORRECTO:**
```java
manager.limpiarHistorial();  // Limpia BD y ArrayList
```

### **2. SIEMPRE cerrar la conexión de BD al salir**

```java
// App.java - main()
manager.cerrarDB();  // ← CRÍTICO al final del programa
```

### **3. BST y Heap son VISTAS del ArrayList, no estructuras persistentes**

```java
// Cada vez que quieras datos actualizados:
ArrayList<Producto> productos = manager.getHistorialCompleto();
BST arbol = new BST(productos);  // ← Reconstruir
```

---

## **Lo que YA funciona:**
Persistencia SQLite completa  
ArrayList sincronizado con BD  
Scraping de MercadoLibre y Alkosto  
Menú interactivo por consola  
Eliminación de productos  

## **Lo que FALTA implementar:**
⏳ BST para búsquedas por rango de precios  
⏳ Heap para encontrar productos más baratos  
⏳ GUI con Swing/JavaFX (opcional)  

### **Regla:**
> **DataManager es el ÚNICO punto de entrada para acceder/modificar datos.**  
> Nunca manipules `historial_productos.db` directamente.

---

**Última actualización:** 2025-11-29  

