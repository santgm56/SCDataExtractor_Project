# 💻 Guía de Desarrollo - BST, Heap y GUI

## 🎯 Objetivo

Esta guía te ayudará a implementar las estructuras de datos faltantes (BST y Heap) y la interfaz gráfica, integrándolas con la arquitectura existente.

---

## 🌲 Implementación de BST (Binary Search Tree)

### **Archivo: `App/src/BST.java`**

```java
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

### **Uso desde App.java:**

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

## 🏔️ Implementación de Heap

### **Archivo: `App/src/Heap.java`**

```java
import java.util.ArrayList;

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
        Heap copia = new Heap(new ArrayList<>(heap));
        
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

### **Uso desde App.java:**

```java
ArrayList<Producto> productos = manager.getHistorialCompleto();
Heap heap = new Heap(productos);

// Producto más barato
Producto masBarato = heap.getMasBarato();
System.out.println("Más barato: " + masBarato.getTitulo());

// Top 5 más baratos
ArrayList<Producto> top5 = heap.getNMasBaratos(5);
```

---

## 🖥️ Implementación de GUI (Swing)

### **Archivo: `App/src/InterfazGrafica.java`**

```java
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.ArrayList;

public class InterfazGrafica extends JFrame {
    private DataManager manager;
    private JTable tablaProductos;
    private DefaultTableModel modeloTabla;
    private JLabel lblTotal;
    
    public InterfazGrafica() {
        this.manager = new DataManager();
        
        setTitle("Sistema de Scraping - E-Commerce");
        setSize(1200, 700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        
        inicializarComponentes();
        cargarDatosEnTabla();
        actualizarEstadisticas();
    }
    
    private void inicializarComponentes() {
        // Panel principal
        JPanel panelPrincipal = new JPanel(new BorderLayout(10, 10));
        panelPrincipal.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        
        // NORTE: Panel de botones
        JPanel panelBotones = crearPanelBotones();
        
        // CENTRO: Tabla de productos
        JScrollPane scrollPane = crearTablaProductos();
        
        // SUR: Panel de estadísticas
        JPanel panelEstadisticas = crearPanelEstadisticas();
        
        panelPrincipal.add(panelBotones, BorderLayout.NORTH);
        panelPrincipal.add(scrollPane, BorderLayout.CENTER);
        panelPrincipal.add(panelEstadisticas, BorderLayout.SOUTH);
        
        add(panelPrincipal);
    }
    
    private JPanel crearPanelBotones() {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        
        JButton btnScraping = new JButton("🔍 Nuevo Scraping");
        btnScraping.addActionListener(e -> mostrarDialogoScraping());
        
        JButton btnOrdenar = new JButton("📊 Ordenar por Precio (BST)");
        btnOrdenar.addActionListener(e -> ordenarPorPrecio());
        
        JButton btnTop5 = new JButton("🏆 Top 5 Baratos (Heap)");
        btnTop5.addActionListener(e -> mostrarTop5());
        
        JButton btnFiltrar = new JButton("🔎 Filtrar por Tienda");
        btnFiltrar.addActionListener(e -> filtrarPorTienda());
        
        JButton btnLimpiar = new JButton("🗑️ Limpiar Historial");
        btnLimpiar.addActionListener(e -> limpiarHistorial());
        
        JButton btnActualizar = new JButton("🔄 Actualizar");
        btnActualizar.addActionListener(e -> {
            cargarDatosEnTabla();
            actualizarEstadisticas();
        });
        
        panel.add(btnScraping);
        panel.add(btnOrdenar);
        panel.add(btnTop5);
        panel.add(btnFiltrar);
        panel.add(btnLimpiar);
        panel.add(btnActualizar);
        
        return panel;
    }
    
    private JScrollPane crearTablaProductos() {
        String[] columnas = {"ID", "Tienda", "Título", "Precio Original", 
                            "Precio Venta", "Descuento", "Calificación"};
        modeloTabla = new DefaultTableModel(columnas, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false; // Tabla no editable
            }
        };
        
        tablaProductos = new JTable(modeloTabla);
        tablaProductos.setRowHeight(25);
        tablaProductos.getColumnModel().getColumn(2).setPreferredWidth(300);
        
        return new JScrollPane(tablaProductos);
    }
    
    private JPanel crearPanelEstadisticas() {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        panel.setBorder(BorderFactory.createTitledBorder("Estadísticas"));
        
        lblTotal = new JLabel("Total productos: 0");
        lblTotal.setFont(new Font("Arial", Font.BOLD, 14));
        
        panel.add(lblTotal);
        return panel;
    }
    
    private void cargarDatosEnTabla() {
        modeloTabla.setRowCount(0);
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        
        int id = 1;
        for (Producto p : productos) {
            Object[] fila = {
                id++,
                p.getTienda(),
                truncarTexto(p.getTitulo(), 60),
                p.getPrecioOriginal(),
                p.getPrecioVenta(),
                p.getDescuento(),
                p.getCalificacion()
            };
            modeloTabla.addRow(fila);
        }
    }
    
    private void actualizarEstadisticas() {
        int total = manager.getTotalProductos();
        lblTotal.setText("Total productos: " + total);
    }
    
    private void mostrarDialogoScraping() {
        JDialog dialogo = new JDialog(this, "Nuevo Scraping", true);
        dialogo.setLayout(new GridLayout(6, 2, 10, 10));
        dialogo.setSize(400, 250);
        dialogo.setLocationRelativeTo(this);
        
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
            if (txtProducto.getText().isEmpty()) {
                JOptionPane.showMessageDialog(dialogo, "Ingresa un producto");
                return;
            }
            
            int tienda = comboTienda.getSelectedIndex() + 1;
            String producto = txtProducto.getText();
            int items = (int) spinnerItems.getValue();
            int paginas = (int) spinnerPaginas.getValue();
            boolean reporte = chkReporte.isSelected();
            
            dialogo.dispose();
            
            // Mostrar progreso
            JOptionPane.showMessageDialog(this, 
                "Scraping iniciado. Por favor espera...", 
                "Procesando", 
                JOptionPane.INFORMATION_MESSAGE
            );
            
            manager.aggDatosHistorial(tienda, producto, items, paginas, reporte);
            
            cargarDatosEnTabla();
            actualizarEstadisticas();
            
            JOptionPane.showMessageDialog(this, 
                "Scraping completado!\nTotal: " + manager.getTotalProductos()
            );
        });
        
        JButton btnCancelar = new JButton("Cancelar");
        btnCancelar.addActionListener(e -> dialogo.dispose());
        
        dialogo.add(btnEjecutar);
        dialogo.add(btnCancelar);
        
        dialogo.setVisible(true);
    }
    
    private void ordenarPorPrecio() {
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        BST arbol = new BST(productos);
        ArrayList<Producto> ordenados = arbol.getOrdenadoPorPrecio();
        
        modeloTabla.setRowCount(0);
        int id = 1;
        for (Producto p : ordenados) {
            Object[] fila = {
                id++,
                p.getTienda(),
                truncarTexto(p.getTitulo(), 60),
                p.getPrecioOriginal(),
                p.getPrecioVenta(),
                p.getDescuento(),
                p.getCalificacion()
            };
            modeloTabla.addRow(fila);
        }
        
        JOptionPane.showMessageDialog(this, "Productos ordenados por precio");
    }
    
    private void mostrarTop5() {
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        
        if (productos.isEmpty()) {
            JOptionPane.showMessageDialog(this, "No hay productos");
            return;
        }
        
        Heap heap = new Heap(productos);
        ArrayList<Producto> top5 = heap.getNMasBaratos(5);
        
        StringBuilder sb = new StringBuilder("<html><h2>Top 5 Productos Más Baratos:</h2><br>");
        for (int i = 0; i < top5.size(); i++) {
            Producto p = top5.get(i);
            sb.append("<b>").append(i + 1).append(".</b> ")
              .append(truncarTexto(p.getTitulo(), 50))
              .append("<br>&nbsp;&nbsp;&nbsp;&nbsp;")
              .append(p.getPrecioVenta())
              .append(" - ").append(p.getTienda())
              .append("<br><br>");
        }
        sb.append("</html>");
        
        JOptionPane.showMessageDialog(this, sb.toString());
    }
    
    private void filtrarPorTienda() {
        String[] opciones = {"MercadoLibre", "Alkosto", "Todas"};
        String seleccion = (String) JOptionPane.showInputDialog(
            this,
            "Selecciona una tienda:",
            "Filtrar por Tienda",
            JOptionPane.QUESTION_MESSAGE,
            null,
            opciones,
            opciones[0]
        );
        
        if (seleccion == null) return;
        
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        modeloTabla.setRowCount(0);
        
        int id = 1;
        for (Producto p : productos) {
            if (seleccion.equals("Todas") || p.getTienda().equals(seleccion)) {
                Object[] fila = {
                    id++,
                    p.getTienda(),
                    truncarTexto(p.getTitulo(), 60),
                    p.getPrecioOriginal(),
                    p.getPrecioVenta(),
                    p.getDescuento(),
                    p.getCalificacion()
                };
                modeloTabla.addRow(fila);
            }
        }
    }
    
    private void limpiarHistorial() {
        int confirmacion = JOptionPane.showConfirmDialog(
            this,
            "¿Estás seguro? Esto eliminará TODOS los productos",
            "Confirmar",
            JOptionPane.YES_NO_OPTION,
            JOptionPane.WARNING_MESSAGE
        );
        
        if (confirmacion == JOptionPane.YES_OPTION) {
            manager.limpiarHistorial();
            cargarDatosEnTabla();
            actualizarEstadisticas();
            JOptionPane.showMessageDialog(this, "Historial limpiado");
        }
    }
    
    private String truncarTexto(String texto, int maxLen) {
        if (texto == null) return "";
        return texto.length() > maxLen ? 
            texto.substring(0, maxLen) + "..." : texto;
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            InterfazGrafica gui = new InterfazGrafica();
            gui.setVisible(true);
        });
    }
}
```

### **Para ejecutar la GUI:**

```powershell
# Opción 1: Modificar run.ps1 temporalmente
java -cp "bin;libs/*" InterfazGrafica

# Opción 2: Crear run-gui.ps1
```

---

## ✅ Checklist de Implementación

### **BST:**
- [ ] Crear archivo `BST.java` en `src/`
- [ ] Copiar código proporcionado
- [ ] Compilar con `.\compile.ps1`
- [ ] Probar desde `App.java` (opción nueva en menú)

### **Heap:**
- [ ] Crear archivo `Heap.java` en `src/`
- [ ] Copiar código proporcionado
- [ ] Compilar con `.\compile.ps1`
- [ ] Probar desde `App.java` (opción nueva en menú)

### **GUI:**
- [ ] Crear archivo `InterfazGrafica.java` en `src/`
- [ ] Copiar código proporcionado
- [ ] Compilar con `.\compile.ps1`
- [ ] Crear `run-gui.ps1` para ejecutar GUI
- [ ] Probar todas las funcionalidades

---

## 📊 Complejidades Temporales

| Operación | ArrayList | BST | Heap |
|-----------|-----------|-----|------|
| Insertar | O(1) | O(log n) | O(log n) |
| Buscar | O(n) | O(log n) | O(n) |
| Obtener mínimo | O(n) | O(log n) | O(1) |
| Ordenar | O(n log n) | O(n) | O(n log n) |

---

**Última actualización:** 2025-11-29
