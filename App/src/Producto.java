import java.text.Normalizer;

// CLASE PRODUCTO: Representa cada item scrapeado con sus atributos
public class Producto {
    private static int contadorId = 0;
    private int id;

    private String titulo;             // Título original con tildes
    private String tituloNormalizado;  // Título sin tildes para AVL

    private String precioOriginal;
    private String precioVenta;
    private String descuento;
    private String imagen;
    private String url;
    private String tienda;
    private String calificacion;
    private String descripcion;
    private double precioNumerico;

    public Producto(String titulo, String precioOriginal, String precioVenta, 
                   String descuento, String imagen, String url, String tienda) {

        this.id = contadorId++;

        this.titulo = titulo;
        String tituloReparado = repararUTF(titulo);
        this.titulo = tituloReparado;
        this.tituloNormalizado = normalizar(tituloReparado);
        this.precioOriginal = precioOriginal;
        this.precioVenta = precioVenta;
        this.descuento = descuento;
        this.imagen = imagen;
        this.url = url;
        this.tienda = tienda;

        this.precioNumerico = extraerPrecioNumerico(precioVenta);
    }

    // ------------------------------
    // NORMALIZAR (sin tildes)
    // ------------------------------
    public static String normalizar(String texto) {
        if (texto == null) return null;
        String n = Normalizer.normalize(texto, Normalizer.Form.NFD);
        // Eliminar caracteres no-ASCII y símbolos especiales
        n = n.replaceAll("[^\\p{ASCII}]", "");
        // Eliminar signos de puntuación excepto espacios y letras
        n = n.replaceAll("[^a-zA-Z0-9\\s]", "");
        return n.toLowerCase();
    }

    // Convierte precio de texto a número para ordenamiento
    private double extraerPrecioNumerico(String precioStr) {
        try {
            if (precioStr.equals("Precio no encontrado") || precioStr.isEmpty()) {
                return 0.0;
            }
            String numeros = precioStr.replace("$", "").replace(".", "").replace(",", ".");
            return Double.parseDouble(numeros);
        } catch (Exception e) {
            return 0.0;
        }
    }

    // GETTERS
    public int getId() { return id; }
    public String getTitulo() { return titulo; }
    public String getTituloNormalizado() { return tituloNormalizado; }
    public String getPrecioOriginal() { return precioOriginal; }
    public String getPrecioVenta() { return precioVenta; }
    public String getDescuento() { return descuento; }
    public String getImagen() { return imagen; }
    public String getUrl() { return url; }
    public String getTienda() { return tienda; }
    public double getPrecioNumerico() { return precioNumerico; }
    public String getCalificacion() { return calificacion; }
    public void setCalificacion(String calificacion) { this.calificacion = calificacion; }
    public String getDescripcion() { return descripcion; }
    public void setDescripcion(String descripcion) { this.descripcion = descripcion; }

    @Override
    public String toString() {
        return String.format("[%d] %s | %s | Descuento: %s",
                id, tienda, precioVenta, descuento);
    }

    public String toStringCompleto() {
        return String.format(
            "ID: %d\nTítulo: %s\nPrecio Original: %s\nPrecio Venta: %s\n" +
            "Descuento: %s\nTienda: %s\nURL: %s\nImagen: %s",
            id, titulo, precioOriginal, precioVenta, descuento, tienda, url, imagen
        );
    }

    public static String repararUTF(String texto) {
        if (texto == null) return null;
        byte[] bytes = texto.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);
        return new String(bytes, java.nio.charset.StandardCharsets.UTF_8);
    }
}