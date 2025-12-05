import java.util.ArrayList;
import java.util.Scanner;
import java.text.Normalizer;

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
            System.out.println("│ 8. Top N productos más baratos (Heap)      │");
            System.out.println("│ 9. Buscar por rango de precio (BST)        │");
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

                    System.out.println("\n✅ Iniciando scraping...");
                    // Normalizar caracteres especiales para compatibilidad
                    String terminoNormalizado = normalizarTexto(termino);
                    manager.aggDatosHistorial(tienda, terminoNormalizado, cantidad, cantidadPag, false);
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
                    System.out.println("\n╔════════════════════════════════════════════╗");
                    System.out.println("║         AVL TREE (Orden alfabético)       ║");
                    System.out.println("╚════════════════════════════════════════════╝\n");
                    manager.getAVL().inorder();
                    break;

                case 8:
                    // TOP N MÁS BARATOS (HEAP) CON FILTRO
                    System.out.println("\n╔════════════════════════════════════════════╗");
                    System.out.println("║    TOP N PRODUCTOS MÁS BARATOS (HEAP)     ║");
                    System.out.println("╚════════════════════════════════════════════╝\n");
                    
                    if (manager.getHeap().isEmpty()) {
                        System.out.println("No hay productos disponibles.");
                        break;
                    }
                    
                    // FILTRO: Buscar por término primero
                    System.out.print("Ingrese término de búsqueda (o Enter para todos): ");
                    String terminoBusqueda = scanner.nextLine().trim();
                    
                    ArrayList<Producto> productosFiltrados;
                    if (terminoBusqueda.isEmpty()) {
                        productosFiltrados = manager.getHistorialCompleto();
                    } else {
                        // Normalizar el término de búsqueda (muñeca -> muneca)
                        String terminoBusquedaNorm = normalizarTexto(terminoBusqueda);
                        productosFiltrados = manager.getAVL().buscarPorTermino(terminoBusquedaNorm);
                        if (productosFiltrados.isEmpty()) {
                            System.out.println("❌ No se encontraron productos con ese término.");
                            break;
                        }
                        System.out.println("✓ Se encontraron " + productosFiltrados.size() + " productos con '" + terminoBusqueda + "'\n");
                    }
                    
                    System.out.print("¿Cuántos productos más baratos desea ver? ");
                    int n = scanner.nextInt();
                    scanner.nextLine();
                    
                    // Crear Heap temporal con productos filtrados
                    Heap heapFiltrado = new Heap();
                    for (Producto p : productosFiltrados) {
                        heapFiltrado.insert(p);
                    }
                    
                    ArrayList<Producto> masBaratos = heapFiltrado.getNMasBaratos(n);
                    
                    System.out.println("\n=== TOP " + n + " MÁS BARATOS" + 
                        (terminoBusqueda.isEmpty() ? "" : " (de '" + terminoBusqueda + "')") + " ===\n");
                    for (int i = 0; i < masBaratos.size(); i++) {
                        Producto p = masBaratos.get(i);
                        System.out.println((i + 1) + ". " + p.getTitulo());
                        System.out.println("   Precio: " + p.getPrecioVenta() + " (" + p.getPrecioNumerico() + ")");
                        System.out.println("   Tienda: " + p.getTienda());
                        System.out.println();
                    }
                    break;

                case 9:
                    // BÚSQUEDA POR RANGO DE PRECIO (BST) CON FILTRO
                    System.out.println("\n╔════════════════════════════════════════════╗");
                    System.out.println("║     BUSCAR POR RANGO DE PRECIO (BST)      ║");
                    System.out.println("╚════════════════════════════════════════════╝\n");
                    
                    ArrayList<Producto> historial = manager.getHistorialCompleto();
                    if (historial.isEmpty()) {
                        System.out.println("No hay productos disponibles.");
                        break;
                    }
                    
                    // FILTRO: Buscar por término primero
                    System.out.print("Ingrese término de búsqueda (o Enter para todos): ");
                    String terminoRango = scanner.nextLine().trim();
                    
                    ArrayList<Producto> productosParaBST;
                    if (terminoRango.isEmpty()) {
                        productosParaBST = historial;
                    } else {
                        // Normalizar el término de búsqueda (muñeca -> muneca)
                        String terminoRangoNorm = normalizarTexto(terminoRango);
                        productosParaBST = manager.getAVL().buscarPorTermino(terminoRangoNorm);
                        if (productosParaBST.isEmpty()) {
                            System.out.println("❌ No se encontraron productos con ese término.");
                            break;
                        }
                        System.out.println("✓ Se encontraron " + productosParaBST.size() + " productos con '" + terminoRango + "'\n");
                    }
                    
                    System.out.print("Precio mínimo: $");
                    double precioMin = scanner.nextDouble();
                    System.out.print("Precio máximo: $");
                    double precioMax = scanner.nextDouble();
                    scanner.nextLine();
                    
                    // Crear BST con productos filtrados
                    BST bst = new BST(productosParaBST);
                    ArrayList<Producto> enRango = bst.buscarEnRango(precioMin, precioMax);
                    
                    System.out.println("\n=== PRODUCTOS EN RANGO $" + precioMin + " - $" + precioMax + 
                        (terminoRango.isEmpty() ? "" : " (de '" + terminoRango + "')") + " ===");
                    if (enRango.isEmpty()) {
                        System.out.println("No se encontraron productos en ese rango.");
                    } else {
                        System.out.println("Encontrados: " + enRango.size() + " productos\n");
                        for (int i = 0; i < enRango.size(); i++) {
                            Producto p = enRango.get(i);
                            System.out.println((i + 1) + ". " + p.getTitulo());
                            System.out.println("   Precio: " + p.getPrecioVenta() + " | Tienda: " + p.getTienda());
                            System.out.println();
                        }
                    }
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
    
    // Normaliza texto removiendo acentos (muñeca -> muneca)
    private static String normalizarTexto(String texto) {
        if (texto == null) return "";
        String normalizado = Normalizer.normalize(texto, Normalizer.Form.NFD);
        normalizado = normalizado.replaceAll("[^\\p{ASCII}]", "");
        return normalizado.toLowerCase();
    }
}