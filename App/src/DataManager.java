import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

// DATA MANAGER: Procesa el formato del JSON de Python y gestiona el ArrayList global con todos los productos
 
public class DataManager {

    // ==============================
    // NUEVO: Estructuras de datos
    // ==============================
    public AVLTree bst;
    public Heap heap;

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
        // NUEVO: Inicializar BST y Heap
        // ===================================
        bst = new AVLTree();
        heap = new Heap();

        // ===== Si ya había datos en la BD reconstruir estructuras =====
        for (Producto p : historialProductos) {
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
            if (linea.contains("'title':") && linea.contains("'price_sell':")) {
                
                int inicio = linea.indexOf("{");
                int fin = linea.lastIndexOf("}");

                if (inicio != -1 && fin != -1) {

                    String json = linea.substring(inicio, fin + 1);
                    Producto producto = extraerProductoDeJSON(json);

                    if (producto != null) {

                        historialProductos.add(producto);
                        database.insertarProducto(producto);

                        System.out.println("Producto agregado: " + producto.getTitulo());

                        // =============================================
                        // NUEVO: insertar este producto en BST y Heap
                        // =============================================
                        bst.insert(producto);
                        heap.insert(producto);
                    }
                }
            }
        }
    
        System.out.println("Productos extraídos: " + historialProductos.size());
    }
    
    
    private Producto extraerProductoDeJSON(String jsonLine) {
        try {
            String titulo = extraerValorJSON(jsonLine, "title");
            String precioOriginal = extraerValorJSON(jsonLine, "price_original");
            String precioVenta = extraerValorJSON(jsonLine, "price_sell");
            String descuento = extraerValorJSON(jsonLine, "discount");
            String imagen = extraerValorJSON(jsonLine, "image");
            String url = extraerValorJSON(jsonLine, "url");
            
            if (!titulo.isEmpty() && !precioVenta.isEmpty()) {

                String tienda = url.contains("mercadolibre") ? "MercadoLibre" : "Alkosto";
                
                Producto producto = new Producto(titulo, precioOriginal, precioVenta, descuento, imagen, url, tienda);
                
                String rating = extraerRatingJSON(jsonLine);
                if (!rating.isEmpty()) producto.setCalificacion(rating);
                 
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
    
    
    private String extraerValorJSON(String json, String clave) {
        try {
            Pattern pattern = Pattern.compile("'" + clave + "':\\s*'([^']*)'");
            Matcher matcher = pattern.matcher(json);
            if (matcher.find()) return matcher.group(1);
        } catch (Exception e) {
            System.err.println("Error extrayendo " + clave + ": " + e.getMessage());
        }
        return "";
    }
    
    
    private String extraerRatingJSON(String json) {
        try {
            Pattern pattern = Pattern.compile("'rating':\\s*\\{([^}]*)\\}");
            Matcher matcher = pattern.matcher(json);
            if (matcher.find()) return "{" + matcher.group(1) + "}";
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
            bst = new AVLTree();
            heap = new Heap();
            for (Producto p : historialProductos) {
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
            bst = new AVLTree();
            heap = new Heap();
            for (Producto p : historialProductos) {
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
        bst = new AVLTree();
        heap = new Heap();

        System.out.println("Historial limpiado (BD, ArrayList, BST, Heap)");
    }
    
    
    public ArrayList<Producto> getProductosPorTienda(String tienda) {
        ArrayList<Producto> filtrados = new ArrayList<>();
        for (Producto p : historialProductos) {
            if (p.getTienda().equals(tienda)) filtrados.add(p);
        }
        return filtrados;
    }
    public void mostrarBST() {
        if (bst == null) {
            System.out.println("BST no inicializado.");
            return;
        }
        bst.inorder();
    }

    public void mostrarHeap() {
        if (heap == null) {
            System.out.println("Heap no inicializado.");
            return;
        }
        heap.mostrarHeap();
    }
    public AVLTree getAVL() {
        return bst;
    }

    public Heap getHeap() {
        return heap;
    }
}