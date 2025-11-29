import java.sql.*;
import java.util.ArrayList;

// HISTORIAL DB: Maneja la persistencia de productos en SQLite
public class HistorialDB {
    private static final String DB_URL = "jdbc:sqlite:historial_productos.db";
    private Connection conexion;
    
    public HistorialDB() {
        try {
            // Cargar el driver de SQLite
            Class.forName("org.sqlite.JDBC");
            conectar();
            crearTabla();
        } catch (ClassNotFoundException e) {
            System.err.println("Error: Driver SQLite no encontrado");
            e.printStackTrace();
        }
    }
    
    // Conectar a la base de datos
    private void conectar() {
        try {
            conexion = DriverManager.getConnection(DB_URL);
            System.out.println("Conexión a SQLite establecida");
        } catch (SQLException e) {
            System.err.println("Error conectando a SQLite: " + e.getMessage());
        }
    }
    
    // Crear tabla de productos si no existe
    private void crearTabla() {
        String sql = """
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
            """;
        
        try (Statement stmt = conexion.createStatement()) {
            stmt.execute(sql);
            System.out.println("Tabla productos verificada/creada");
        } catch (SQLException e) {
            System.err.println("Error creando tabla: " + e.getMessage());
        }
    }
    
    // Insertar un producto en la base de datos
    public void insertarProducto(Producto producto) {
        String sql = """
            INSERT INTO productos (titulo, precio_original, precio_venta, descuento, 
                                 imagen, url, tienda, calificacion, descripcion, precio_numerico)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """;
        
        try (PreparedStatement pstmt = conexion.prepareStatement(sql)) {
            pstmt.setString(1, producto.getTitulo());
            pstmt.setString(2, producto.getPrecioOriginal());
            pstmt.setString(3, producto.getPrecioVenta());
            pstmt.setString(4, producto.getDescuento());
            pstmt.setString(5, producto.getImagen());
            pstmt.setString(6, producto.getUrl());
            pstmt.setString(7, producto.getTienda());
            pstmt.setString(8, producto.getCalificacion());
            pstmt.setString(9, producto.getDescripcion());
            pstmt.setDouble(10, producto.getPrecioNumerico());
            
            pstmt.executeUpdate();
            System.out.println("✓ Producto guardado en BD: " + producto.getTitulo().substring(0, Math.min(50, producto.getTitulo().length())));
        } catch (SQLException e) {
            System.err.println("Error insertando producto: " + e.getMessage());
        }
    }
    
    // Cargar TODOS los productos desde la base de datos
    public ArrayList<Producto> cargarTodosProductos() {
        ArrayList<Producto> productos = new ArrayList<>();
        String sql = "SELECT * FROM productos ORDER BY id ASC";
        
        try (Statement stmt = conexion.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                String titulo = rs.getString("titulo");
                String precioOriginal = rs.getString("precio_original");
                String precioVenta = rs.getString("precio_venta");
                String descuento = rs.getString("descuento");
                String imagen = rs.getString("imagen");
                String url = rs.getString("url");
                String tienda = rs.getString("tienda");
                
                Producto producto = new Producto(titulo, precioOriginal, precioVenta, 
                                                descuento, imagen, url, tienda);
                
                // Agregar campos opcionales
                String calificacion = rs.getString("calificacion");
                if (calificacion != null && !calificacion.isEmpty()) {
                    producto.setCalificacion(calificacion);
                }
                
                String descripcion = rs.getString("descripcion");
                if (descripcion != null && !descripcion.isEmpty()) {
                    producto.setDescripcion(descripcion);
                }
                
                productos.add(producto);
            }
            
            System.out.println("✓ Cargados " + productos.size() + " productos desde BD");
        } catch (SQLException e) {
            System.err.println("Error cargando productos: " + e.getMessage());
        }
        
        return productos;
    }
    
    // Obtener el total de productos en la BD
    public int contarProductos() {
        String sql = "SELECT COUNT(*) as total FROM productos";
        
        try (Statement stmt = conexion.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            if (rs.next()) {
                return rs.getInt("total");
            }
        } catch (SQLException e) {
            System.err.println("Error contando productos: " + e.getMessage());
        }
        
        return 0;
    }
    
    // Eliminar un producto específico por ID
    public boolean eliminarProducto(int id) {
        String sql = "DELETE FROM productos WHERE id = ?";
        
        try (PreparedStatement pstmt = conexion.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            int filasAfectadas = pstmt.executeUpdate();
            
            if (filasAfectadas > 0) {
                System.out.println("✓ Producto ID " + id + " eliminado");
                return true;
            } else {
                System.out.println("❌ Producto ID " + id + " no encontrado");
                return false;
            }
        } catch (SQLException e) {
            System.err.println("Error eliminando producto: " + e.getMessage());
            return false;
        }
    }
    
    // Eliminar todos los productos de una tienda específica
    public int eliminarPorTienda(String tienda) {
        String sql = "DELETE FROM productos WHERE tienda = ?";
        
        try (PreparedStatement pstmt = conexion.prepareStatement(sql)) {
            pstmt.setString(1, tienda);
            int filasAfectadas = pstmt.executeUpdate();
            System.out.println("✓ Eliminados " + filasAfectadas + " productos de " + tienda);
            return filasAfectadas;
        } catch (SQLException e) {
            System.err.println("Error eliminando por tienda: " + e.getMessage());
            return 0;
        }
    }
    
    // Limpiar todo el historial (útil para testing)
    public void limpiarHistorial() {
        String sql = "DELETE FROM productos";
        
        try (Statement stmt = conexion.createStatement()) {
            stmt.executeUpdate(sql);
            System.out.println("Historial limpiado");
        } catch (SQLException e) {
            System.err.println("Error limpiando historial: " + e.getMessage());
        }
    }
    
    // Cerrar conexión
    public void cerrar() {
        try {
            if (conexion != null && !conexion.isClosed()) {
                conexion.close();
                System.out.println("Conexión SQLite cerrada");
            }
        } catch (SQLException e) {
            System.err.println("Error cerrando conexión: " + e.getMessage());
        }
    }
}
