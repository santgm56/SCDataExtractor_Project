import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

// DATA MANAGER: Procesa el formato del JSON de Python y gestiona el ArrayList global con todos los productos
 
public class DataManager {
    // ARRAYLIST GLOBAL con todos los productos scrapeados
    private ArrayList<Producto> historialProductos;
    
    public DataManager() {
        this.historialProductos = new ArrayList<>();
    }
    
    // Ejecuta scraping y procesa los datos del JSON
    public void aggDatosHistorial(int tienda, String producto, int cantidadItems, int cantidadPag, boolean generarReportes) {
        System.out.println("Ejecutando scraping para: " + producto);
        
        // Ejecutar Python y obtener salida
        List<String> salidaPython = RunPython.ejecutarScraping(tienda, producto, cantidadItems, cantidadPag, generarReportes);
        
        // Procesar el formato REAL del JSON
        procesarJSONReal(salidaPython);
        
        System.out.println("Scraping completado. Total en historial: " + historialProductos.size());
    }
    
    //Procesa el formato del JSON: {'title': '...', 'price_sell': '...', etc}
    private void procesarJSONReal(List<String> lineas) {
    System.out.println("=== BUSCANDO PRODUCTOS EN LA SALIDA ===");
    
    for (String linea : lineas) {
        // Buscar cualquier línea que tenga formato de producto
        if (linea.contains("'title':") && linea.contains("'price_sell':")) {
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
    
    // Extrae un valor simple del JSON: 'clave': 'valor'
    private String extraerValorJSON(String json, String clave) {
        try {
            Pattern pattern = Pattern.compile("'" + clave + "':\\s*'([^']*)'");
            Matcher matcher = pattern.matcher(json);
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
            Pattern pattern = Pattern.compile("'rating':\\s*\\{([^}]*)\\}");
            Matcher matcher = pattern.matcher(json);
            if (matcher.find()) {
                return "{" + matcher.group(1) + "}";
            }
        } catch (Exception e) {
            System.err.println("Error extrayendo rating: " + e.getMessage());
        }
        return "";
    }
    
    // MÉTODOS DE ACCESO AL ARRAYLIST GLOBAL
    public ArrayList<Producto> getHistorialCompleto() {
        return new ArrayList<>(historialProductos);
    }
    
    public int getTotalProductos() {
        return historialProductos.size();
    }
}