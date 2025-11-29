import java.util.ArrayList;
import java.util.Scanner;

public class App {
    private static DataManager manager;
    private static Scanner scanner;
    private static boolean salir = false;

    public static void main(String[] args) throws Exception {
        manager = new DataManager();
        scanner = new Scanner(System.in);

        System.out.println("╔════════════════════════════════════════════╗");
        System.out.println("║     SISTEMA DE SCRAPING - E-COMMERCE      ║");
        System.out.println("║          CON PERSISTENCIA SQLite          ║");
        System.out.println("╚════════════════════════════════════════════╝");
        System.out.println("Historial cargado: " + manager.getTotalProductos() + " productos\n");

        // Loop principal - NO se cierra hasta que el usuario elija salir
        while (!salir) {
            mostrarMenu();
            procesarOpcion();
        }

        manager.cerrarDB();
        scanner.close();
        System.out.println("\n¡Hasta luego!");
    }

    private static void mostrarMenu() {
        System.out.println("\n╔════════════════════════════════════════════╗");
        System.out.println("║              MENU PRINCIPAL               ║");
        System.out.println("╠════════════════════════════════════════════╣");
        System.out.println("║ 1. Hacer nuevo scraping                   ║");
        System.out.println("║ 2. Ver todos los productos                ║");
        System.out.println("║ 3. Ver estadísticas                       ║");
        System.out.println("║ 4. Buscar productos por tienda            ║");
        System.out.println("║ 5. Limpiar historial                      ║");
        System.out.println("║ 6. Salir                                  ║");
        System.out.println("╚════════════════════════════════════════════╝");
        System.out.print("Elige una opción: ");
    }

    private static void procesarOpcion() {
        try {
            int opcion = scanner.nextInt();
            scanner.nextLine(); // Limpiar buffer

            switch (opcion) {
                case 1:
                    hacerScraping();
                    break;
                case 2:
                    verProductos();
                    break;
                case 3:
                    verEstadisticas();
                    break;
                case 4:
                    buscarPorTienda();
                    break;
                case 5:
                    limpiarHistorial();
                    break;
                case 6:
                    salir = true;
                    break;
                default:
                    System.out.println("❌ Opción no válida");
            }
        } catch (Exception e) {
            System.out.println("❌ Error: " + e.getMessage());
            scanner.nextLine(); // Limpiar buffer en caso de error
        }
    }

    private static void hacerScraping() {
        System.out.println("\n╔════════════════════════════════════════════╗");
        System.out.println("║            NUEVO SCRAPING                 ║");
        System.out.println("╚════════════════════════════════════════════╝");

        System.out.print("Selecciona tienda (1=MercadoLibre, 2=Alkosto): ");
        int tienda = scanner.nextInt();
        
        if (tienda != 1 && tienda != 2) {
            System.out.println("❌ Tienda no válida");
            return;
        }

        scanner.nextLine();
        System.out.print("¿Qué producto deseas buscar?: ");
        String producto = scanner.nextLine();

        System.out.print("¿Cuántos items?: ");
        int cantidadItems = scanner.nextInt();

        System.out.print("¿Cuántas páginas?: ");
        int cantidadPaginas = scanner.nextInt();

        System.out.print("¿Generar reporte? (s/n): ");
        scanner.nextLine();
        String generarReporte = scanner.nextLine();
        boolean reporteBoolean = generarReporte.equalsIgnoreCase("s");

        System.out.println("\n⏳ Ejecutando scraping...\n");
        manager.aggDatosHistorial(tienda, producto, cantidadItems, cantidadPaginas, reporteBoolean);
        System.out.println("\n✅ Scraping completado! Total: " + manager.getTotalProductos() + " productos");
    }

    private static void verProductos() {
        ArrayList<Producto> productos = manager.getHistorialCompleto();

        if (productos.isEmpty()) {
            System.out.println("\n❌ No hay productos en el historial");
            return;
        }

        System.out.println("\n╔════════════════════════════════════════════╗");
        System.out.println("║         TODOS LOS PRODUCTOS               ║");
        System.out.println("╚════════════════════════════════════════════╝\n");

        for (int i = 0; i < productos.size(); i++) {
            Producto p = productos.get(i);
            String tituloCorto = p.getTitulo().length() > 50 ?
                    p.getTitulo().substring(0, 50) + "..." : p.getTitulo();

            System.out.printf("%2d. [%-12s] %s | %s%n",
                    (i + 1),
                    p.getTienda(),
                    p.getPrecioVenta(),
                    tituloCorto
            );
        }

        System.out.println("\nTotal: " + productos.size() + " productos");
    }

    private static void verEstadisticas() {
        ArrayList<Producto> productos = manager.getHistorialCompleto();

        if (productos.isEmpty()) {
            System.out.println("\n❌ No hay productos para mostrar estadísticas");
            return;
        }

        int mercadolibre = 0, alkosto = 0;
        double precioPromedio = 0;

        for (Producto p : productos) {
            if (p.getTienda().equals("MercadoLibre")) {
                mercadolibre++;
            } else {
                alkosto++;
            }
            precioPromedio += p.getPrecioNumerico();
        }

        precioPromedio /= productos.size();

        System.out.println("\n╔════════════════════════════════════════════╗");
        System.out.println("║         ESTADÍSTICAS DEL HISTORIAL        ║");
        System.out.println("╠════════════════════════════════════════════╣");
        System.out.println("║ Total productos: " + String.format("%-27d", productos.size()) + "║");
        System.out.println("║ MercadoLibre: " + String.format("%-32d", mercadolibre) + "║");
        System.out.println("║ Alkosto: " + String.format("%-37d", alkosto) + "║");
        System.out.println("║ Precio promedio: $" + String.format("%-26.0f", precioPromedio) + "║");
        System.out.println("╚════════════════════════════════════════════╝");
    }

    private static void buscarPorTienda() {
        System.out.print("\n¿Qué tienda deseas ver? (1=MercadoLibre, 2=Alkosto): ");
        int opcion = scanner.nextInt();

        String tiendaBuscada = (opcion == 1) ? "MercadoLibre" : "Alkosto";
        ArrayList<Producto> productos = manager.getHistorialCompleto();

        ArrayList<Producto> resultados = new ArrayList<>();
        for (Producto p : productos) {
            if (p.getTienda().equals(tiendaBuscada)) {
                resultados.add(p);
            }
        }

        if (resultados.isEmpty()) {
            System.out.println("\n❌ No hay productos de " + tiendaBuscada);
            return;
        }

        System.out.println("\n╔════════════════════════════════════════════╗");
        System.out.println("║         PRODUCTOS DE " + String.format("%-17s", tiendaBuscada.toUpperCase()) + "║");
        System.out.println("╚════════════════════════════════════════════╝\n");

        for (int i = 0; i < resultados.size(); i++) {
            Producto p = resultados.get(i);
            String tituloCorto = p.getTitulo().length() > 40 ?
                    p.getTitulo().substring(0, 40) + "..." : p.getTitulo();
            System.out.printf("%2d. %s | %s%n", (i + 1), p.getPrecioVenta(), tituloCorto);
        }

        System.out.println("\nTotal: " + resultados.size() + " productos");
    }

    private static void limpiarHistorial() {
        System.out.print("\n⚠️  ¿Estás seguro? Esto eliminará TODOS los productos (s/n): ");
        String confirmacion = scanner.nextLine();

        if (confirmacion.equalsIgnoreCase("s")) {
            manager.limpiarHistorial();
            System.out.println("✅ Historial limpiado");
        } else {
            System.out.println("❌ Operación cancelada");
        }
    }
}
