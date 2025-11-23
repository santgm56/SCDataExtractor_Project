import java.util.ArrayList;

public class App {
    public static void main(String[] args) throws Exception {
        DataManager manager = new DataManager();
        
        System.out.println("=== DEMOSTRACION DATA MANAGER ===");
        System.out.println("ArrayList inicial: " + manager.getTotalProductos() + " productos");
        
        // PRUEBA 1: Primer scraping
        System.out.println("\n--- SCRAPING 1: Zapatos en MercadoLibre ---");
        manager.aggDatosHistorial(1, "zapatos", 3, 1, false);
        
        // Mostrar resultados del primer scraping
        System.out.println("\n--- PRODUCTOS OBTENIDOS ---");
        ArrayList<Producto> productos1 = manager.getHistorialCompleto();
        for (int i = 0; i < productos1.size(); i++) {
            Producto p = productos1.get(i);
            System.out.println((i + 1) + ". " + p.getTitulo());
            System.out.println("   Precio: " + p.getPrecioVenta() + " | Descuento: " + p.getDescuento() + " | Tienda: " + p.getTienda());
            if (p.getCalificacion() != null) {
                System.out.println("   Rating: " + p.getCalificacion());
            }
            System.out.println();
        }
        
        // PRUEBA 2: Segundo scraping (se acumula)
        System.out.println("--- SCRAPING 2: Laptops en Alkosto ---");
        manager.aggDatosHistorial(2, "laptop", 2, 1, false);
        
        // PRUEBA 3: Tercer scraping (mas acumulacion)
        System.out.println("--- SCRAPING 3: Telefonos en MercadoLibre ---");
        manager.aggDatosHistorial(1, "telefono", 2, 1, false);
        
        // RESUMEN FINAL
        System.out.println("=== RESUMEN FINAL ===");
        System.out.println("Total productos en ArrayList: " + manager.getTotalProductos());
        
        // Mostrar todos los productos acumulados
        System.out.println("\n--- TODOS LOS PRODUCTOS EN ARRAYLIST ---");
        ArrayList<Producto> todosProductos = manager.getHistorialCompleto();
        
        int mercadolibre = 0, alkosto = 0;
        for (int i = 0; i < todosProductos.size(); i++) {
            Producto p = todosProductos.get(i);
            String tituloCorto = p.getTitulo().length() > 40 ? 
                p.getTitulo().substring(0, 40) + "..." : p.getTitulo();
                
            System.out.printf("%2d. [%s] %s | %s%n", 
                (i + 1), 
                p.getTienda(), 
                p.getPrecioVenta(), 
                tituloCorto
            );
            
            if (p.getTienda().equals("MercadoLibre")) mercadolibre++;
            else alkosto++;
        }
        
        System.out.println("\n--- ESTADISTICAS ---");
        System.out.println("MercadoLibre: " + mercadolibre + " productos");
        System.out.println("Alkosto: " + alkosto + " productos");
        System.out.println("Total acumulado: " + manager.getTotalProductos() + " productos");
        
        System.out.println("\n=== DEMOSTRACION EXITOSA ===");
        System.out.println("El ArrayList global mantiene " + manager.getTotalProductos() + " productos");
        System.out.println("Listo para integracion con BST y Heap");
        
        System.exit(0);
    }
}