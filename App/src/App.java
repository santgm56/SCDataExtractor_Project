import java.util.ArrayList;
import java.util.Scanner;

public class App {
    public static void main(String[] args) throws Exception {
        DataManager manager = new DataManager();
        Scanner scanner = new Scanner(System.in);

        System.out.println("\n╔════════════════════════════════════════════╗");
        System.out.println("║     SISTEMA DE SCRAPING - E-COMMERCE      ║");
        System.out.println("║          CON PERSISTENCIA SQLite          ║");
        System.out.println("╚════════════════════════════════════════════╝\n");

        boolean salir = false;

        while (!salir) {
            System.out.println("┌────────────────────────────────────────────┐");
            System.out.println("│              MENU PRINCIPAL                │");
            System.out.println("├────────────────────────────────────────────┤");
            System.out.println("│ 1. Iniciar scraping                        │");
            System.out.println("│ 2. Ver todos los productos                 │");
            System.out.println("│ 3. Ver estadísticas                        │");
            System.out.println("│ 4. Filtrar por tienda                      │");
            System.out.println("│ 5. Limpiar historial                       │");
            System.out.println("│ 6. Salir                                   │");
            System.out.println("│ 7. Mostrar AVL Tree                        │");
            System.out.println("│ 8. Buscar producto en AVL                  │");
            System.out.println("│ 9. Mostrar Heap                            │");
            System.out.println("└────────────────────────────────────────────┘");

            System.out.print("Seleccione una opción: ");
            int opcion = scanner.nextInt();
            scanner.nextLine(); // Limpiar buffer

            switch (opcion) {
                case 1:
                    System.out.println("\n=== CONFIGURAR SCRAPING ===");
                    System.out.print("Término de búsqueda: ");
                    String termino = scanner.nextLine();

                    System.out.print("Cantidad de productos (max 10): ");
                    int cantidad = scanner.nextInt();
                    scanner.nextLine();

                    System.out.print("Cantidad de páginas a revisar (max 10): ");
                    int cantidadPag = scanner.nextInt();
                    scanner.nextLine();

                    System.out.println("\nTiendas disponibles:");
                    System.out.println("1. MercadoLibre");
                    System.out.println("2. Alkosto");
                    System.out.print("Seleccione tienda: ");
                    int tienda = scanner.nextInt();
                    scanner.nextLine();

                    System.out.println("\n🔄 Iniciando scraping...");
                    manager.aggDatosHistorial(tienda, termino, cantidad, cantidadPag, false);
                    System.out.println("✓ Scraping completado");
                    break;

                case 2:
                    System.out.println("\n╔════════════════════════════════════════════╗");
                    System.out.println("║         TODOS LOS PRODUCTOS                ║");
                    System.out.println("╚════════════════════════════════════════════╝\n");

                    ArrayList<Producto> todos = manager.getHistorialCompleto();
                    if (todos.isEmpty()) {
                        System.out.println("No hay productos en el historial.");
                    } else {
                        for (int i = 0; i < todos.size(); i++) {
                            Producto p = todos.get(i);
                            System.out.println((i + 1) + ". " + p.getTitulo());
                            System.out.println("   Precio: " + p.getPrecioVenta() + " | Tienda: " + p.getTienda());
                            if (p.getCalificacion() != null) {
                                System.out.println("   Rating: " + p.getCalificacion());
                            }
                            System.out.println();
                        }
                    }
                    break;

                case 3:
                    System.out.println("\n╔════════════════════════════════════════════╗");
                    System.out.println("║            ESTADÍSTICAS                    ║");
                    System.out.println("╚════════════════════════════════════════════╝\n");

                    ArrayList<Producto> productos = manager.getHistorialCompleto();
                    int mercadolibre = 0, alkosto = 0;
                    for (Producto p : productos) {
                        if (p.getTienda().equals("MercadoLibre")) mercadolibre++;
                        else alkosto++;
                    }

                    System.out.println("Total productos: " + manager.getTotalProductos());
                    System.out.println("MercadoLibre: " + mercadolibre);
                    System.out.println("Alkosto: " + alkosto);
                    break;

                case 4:
                    System.out.println("\n=== FILTRAR POR TIENDA ===");
                    System.out.println("1. MercadoLibre");
                    System.out.println("2. Alkosto");
                    System.out.print("Seleccione tienda: ");
                    int filtroTienda = scanner.nextInt();
                    scanner.nextLine();

                    String nombreTienda = (filtroTienda == 1) ? "MercadoLibre" : "Alkosto";
                    ArrayList<Producto> filtrados = manager.getProductosPorTienda(nombreTienda);

                    System.out.println("\n=== PRODUCTOS DE " + nombreTienda + " ===");
                    if (filtrados.isEmpty()) {
                        System.out.println("No hay productos de esta tienda.");
                    } else {
                        for (int i = 0; i < filtrados.size(); i++) {
                            Producto p = filtrados.get(i);
                            System.out.println((i + 1) + ". " + p.getTitulo());
                            System.out.println("   Precio: " + p.getPrecioVenta());
                            System.out.println();
                        }
                    }
                    break;

                case 5:
                    System.out.print("\n¿Está seguro de limpiar el historial? (S/N): ");
                    String confirmacion = scanner.nextLine();
                    if (confirmacion.equalsIgnoreCase("S")) {
                        manager.limpiarHistorial();
                        System.out.println("✓ Historial limpiado");
                    } else {
                        System.out.println("Operación cancelada");
                    }
                    break;

                case 6:
                    salir = true;
                    manager.cerrarDB();
                    System.out.println("\n¡Hasta luego!");
                    break;

                // ===============================
                //         NUEVAS OPCIONES
                // ===============================

                case 7:
                    System.out.println("\n=== AVL TREE (Orden alfabético) ===");
                    manager.getAVL().inorder();
                    break;

                case 8:
                    System.out.print("\nIngrese el nombre exacto del producto a buscar: ");
                    String busqueda = scanner.nextLine();
                    Producto encontrado = manager.getAVL().buscar(busqueda);

                    if (encontrado != null) {
                        System.out.println("\nProducto encontrado:");
                        System.out.println("Título: " + encontrado.getTitulo());
                        System.out.println("Precio: " + encontrado.getPrecioVenta());
                        System.out.println("Tienda: " + encontrado.getTienda());
                    } else {
                        System.out.println("❌ No se encontró ese producto.");
                    }
                    break;

                case 9:
                    System.out.println("\n=== HEAP (ordenado alfabéticamente) ===");
                    manager.getHeap().mostrarHeap();
                    break;

                default:
                    System.out.println("Opción inválida");
            }

            if (!salir) {
                System.out.println("\nPresione Enter para continuar...");
                scanner.nextLine();
            }
        }

        scanner.close();
    }
}