import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

// DATA MANAGER: Procesa el formato del JSON de Python y gestiona el ArrayList global con todos los productos
 
public class DataManager {

    // ==============================
    // NUEVO: Estructuras de datos
    // ==============================
    public AVLTree avl;  // Para búsqueda alfabética
    public BST bst;      // Para búsqueda por rango de precio
    public Heap heap;    // Para obtener los más baratos

    // ARRAYLIST GLOBAL con todos los productos scrapeados
    private ArrayList<Producto> historialProductos;
    private HistorialDB database;
    
    public DataManager() {
        this.database = new HistorialDB();
        this.historialProductos = new ArrayList<>();
        
        System.out.println("\n=== CARGANDO HISTORIAL DESDE BD ===");
        this.historialProductos = database.cargarTodosProductos();
        System.out.println("Historial cargado: " + historialProductos.size() + " productos\n");

        // ===================================
        // NUEVO: Inicializar AVL, BST y Heap
        // ===================================
        avl = new AVLTree();
        bst = new BST();
        heap = new Heap();

        // ===== Si ya había datos en la BD reconstruir estructuras =====
        for (Producto p : historialProductos) {
            avl.insert(p);
            bst.insert(p);
            heap.insert(p);
        }
    }
    
    // Ejecuta scraping y procesa los datos del JSON
    public void aggDatosHistorial(int tienda, String producto, int cantidadItems, int cantidadPag, boolean generarReportes) {
        System.out.println("Ejecutando scraping para: " + producto);

        int sizeAntes = historialProductos.size();
        
        // Ejecutar Python y obtener salida
        List<String> salidaPython = RunPython.ejecutarScraping(tienda, producto, cantidadItems, cantidadPag, generarReportes);
        
        // Procesar el formato REAL del JSON
        procesarJSONReal(salidaPython);

        int sizeDespues = historialProductos.size();
        int nuevos = sizeDespues - sizeAntes;

        System.out.println("Scraping completado. Total en historial: " + historialProductos.size());
        System.out.println("Productos nuevos agregados: " + nuevos + "\n");
    }
    
    
    //Procesa el formato del JSON: {'title': '...', 'price_sell': '...', etc}
    private void procesarJSONReal(List<String> lineas) {
        System.out.println("=== BUSCANDO PRODUCTOS EN LA SALIDA ===");
        
        for (String linea : lineas) {
            // Buscar cualquier línea que tenga formato de producto (comillas simples o dobles)
            if ((linea.contains("'title':") || linea.contains("\"title\":")) && 
                (linea.contains("'price_sell':") || linea.contains("\"price_sell\":"))) {
                System.out.println("Línea detectada: " + linea.substring(0, Math.min(200, linea.length())));
                
                // Extraer la parte JSON (entre { y })
                int inicio = linea.indexOf("{");
                int fin = linea.lastIndexOf("}");
                if (inicio != -1 && fin != -1) {
                    String json = linea.substring(inicio, fin + 1);
                    System.out.println("JSON extraído: " + json.substring(0, Math.min(100, json.length())) + "...");
                    
                    Producto producto = extraerProductoDeJSON(json);
                    if (producto != null) {
                        historialProductos.add(producto);
                        database.insertarProducto(producto); // GUARDAR EN BD
                        
                        // NUEVO: insertar en las 3 estructuras
                        avl.insert(producto);
                        bst.insert(producto);
                        heap.insert(producto);
                        
                        System.out.println("Producto agregado: " + producto.getTitulo());
                    }
                }
            }
        }
        
        System.out.println("Productos extraídos: " + historialProductos.size());
    }
    
    
    private Producto extraerProductoDeJSON(String jsonLine) {
        try {
            // Extraer TODOS los campos del JSON
            String titulo = extraerValorJSON(jsonLine, "title");
            String precioOriginal = extraerValorJSON(jsonLine, "price_original");
            String precioVenta = extraerValorJSON(jsonLine, "price_sell");
            String descuento = extraerValorJSON(jsonLine, "discount");
            String imagen = extraerValorJSON(jsonLine, "image");
            String url = extraerValorJSON(jsonLine, "url");
            
            // Validar que tenemos datos mínimos
            if (!titulo.isEmpty() && !precioVenta.isEmpty()) {
                // Determinar tienda basado en la URL
                String tienda = url.contains("mercadolibre") ? "MercadoLibre" : "Alkosto";
                
                // Crear producto con TODOS los campos
                Producto producto = new Producto(titulo, precioOriginal, precioVenta, descuento, imagen, url, tienda);
                
                // Extraer campos adicionales si existen 
                String rating = extraerRatingJSON(jsonLine);
                if (!rating.isEmpty()) {
                    producto.setCalificacion(rating);
                }
                 
                String descripcion = extraerValorJSON(jsonLine, "description");
                if (!descripcion.isEmpty() && !descripcion.equals("None")) {
                    producto.setDescripcion(descripcion);
                }
                
                return producto;
            }
        } catch (Exception e) {
            System.err.println("Error procesando JSON: " + e.getMessage());
        }
        return null;
    }
    
    // Extrae un valor simple del JSON: 'clave': 'valor' o "clave": "valor"
    private String extraerValorJSON(String json, String clave) {
        try {
            // Primero intentar con comillas dobles
            Pattern pattern = Pattern.compile("\"" + clave + "\":\\s*\"([^\"]*)\"");
            Matcher matcher = pattern.matcher(json);
            if (matcher.find()) {
                return matcher.group(1);
            }
            
            // Si no encuentra, intentar con comillas simples
            pattern = Pattern.compile("'" + clave + "':\\s*'([^']*)'");
            matcher = pattern.matcher(json);
            if (matcher.find()) {
                return matcher.group(1);
            }
        } catch (Exception e) {
            System.err.println("Error extrayendo " + clave + ": " + e.getMessage());
        }
        return "";
    }
    
    // Extrae el objeto rating completo
    private String extraerRatingJSON(String json) {
        try {
            // Intentar con comillas dobles
            Pattern pattern = Pattern.compile("\"rating\":\\s*\\{([^}]*)\\}");
            Matcher matcher = pattern.matcher(json);
            if (matcher.find()) {
                return "{" + matcher.group(1) + "}";
            }
            
            // Intentar con comillas simples
            pattern = Pattern.compile("'rating':\\s*\\{([^}]*)\\}");
            matcher = pattern.matcher(json);
            if (matcher.find()) {
                return "{" + matcher.group(1) + "}";
            }
        } catch (Exception e) {
            System.err.println("Error extrayendo rating: " + e.getMessage());
        }
        return "";
    }
    
    
    public ArrayList<Producto> getHistorialCompleto() {
        return new ArrayList<>(historialProductos);
    }
    
    public int getTotalProductos() {
        return historialProductos.size();
    }
    
    public void cerrarDB() {
        database.cerrar();
    }
    
    
    public boolean eliminarProducto(int id) {
        boolean eliminado = database.eliminarProducto(id);
        if (eliminado) {
            historialProductos = database.cargarTodosProductos();

            // RECONSTRUIR ESTRUCTURAS
            avl = new AVLTree();
            bst = new BST();
            heap = new Heap();
            for (Producto p : historialProductos) {
                avl.insert(p);
                bst.insert(p);
                heap.insert(p);
            }
        }
        return eliminado;
    }
    
    
    public int eliminarPorTienda(String tienda) {
        int eliminados = database.eliminarPorTienda(tienda);
        if (eliminados > 0) {

            historialProductos = database.cargarTodosProductos();

            // RECONSTRUIR ESTRUCTURAS
            avl = new AVLTree();
            bst = new BST();
            heap = new Heap();
            for (Producto p : historialProductos) {
                avl.insert(p);
                bst.insert(p);
                heap.insert(p);
            }
        }
        return eliminados;
    }
    
    
    public void limpiarHistorial() {
        database.limpiarHistorial();
        historialProductos.clear();

        // Reiniciar estructuras
        avl = new AVLTree();
        bst = new BST();
        heap = new Heap();

        System.out.println("Historial limpiado (BD, ArrayList, AVL, BST, Heap)");
    }
    
    
    public ArrayList<Producto> getProductosPorTienda(String tienda) {
        ArrayList<Producto> filtrados = new ArrayList<>();
        for (Producto p : historialProductos) {
            if (p.getTienda().equals(tienda)) filtrados.add(p);
        }
        return filtrados;
    }
    public void mostrarAVL() {
        if (avl == null) {
            System.out.println("AVL no inicializado.");
            return;
        }
        avl.inorder();
    }

    public void mostrarHeap() {
        if (heap == null) {
            System.out.println("Heap no inicializado.");
            return;
        }
        heap.mostrarHeap();
    }
    
    public AVLTree getAVL() {
        return avl;
    }
    
    public BST getBST() {
        return bst;
    }

    public Heap getHeap() {
        return heap;
    }
}