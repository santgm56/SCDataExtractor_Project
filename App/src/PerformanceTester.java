import java.util.ArrayList;
import java.util.Random;
//import java.util.List;

public class PerformanceTester {

    // Constantes para la generación de datos
    private static final String[] PALABRAS = {"Laptop", "Mouse", "Teclado", "Monitor", "Cámara", "Celular", "Tablet", "Audífonos", "Cargador", "Cable", "Gamer", "Oficina", "Pro", "Ultra", "Max", "Lite", "Negro", "Blanco", "Rojo", "Azul"};
    private static final String[] TIENDAS = {"MercadoLibre", "Alkosto", "Metrocuadrado"};
    
    // Tamaños de prueba (10^4, 10^5, 10^6)
    // 1,000,000 de objetos puede requerir aumentar la memoria RAM de Java (-Xmx4G)
    private static final int[] TAMANOS_PRUEBA = {10000, 50000, 100000, 500000, 1000000}; 

    public static void main(String[] args) {
        System.out.println("================================================================");
        System.out.println("   ANÁLISIS DE RENDIMIENTO - ESTRUCTURAS DE DATOS ");
        System.out.println("================================================================");
        System.out.println("Estructura,Operacion,N(Tamaño),Tiempo(ns),Tiempo(ms)");

        for (int n : TAMANOS_PRUEBA) {
            try {
                // 1. Generación de Mockup Data
                // Se excluye del tiempo de medición de las estructuras
                System.err.println("Generando " + n + " datos de prueba..."); // Log a stderr para no ensuciar el CSV
                ArrayList<Producto> datosPrueba = generarDatosMock(n);

                // 2. Pruebas AVL Tree
                testAVL(datosPrueba, n);

                // 3. Pruebas BST (Binary Search Tree)
                testBST(datosPrueba, n);

                // 4. Pruebas Heap (Cola de Prioridad)
                testHeap(datosPrueba, n);

                // Limpiar memoria entre iteraciones grandes
                datosPrueba = null;
                System.gc(); 

            } catch (OutOfMemoryError e) {
                System.err.println("ERROR: Memoria insuficiente para N=" + n + ". Intenta correr java con -Xmx4G");
                break;
            }
        }
        System.out.println("================================================================");
    }


    private static ArrayList<Producto> generarDatosMock(int cantidad) {
        ArrayList<Producto> lista = new ArrayList<>(cantidad);
        Random rand = new Random();

        for (int i = 0; i < cantidad; i++) {
            // Generar título aleatorio combinando 3 palabras
            String titulo = PALABRAS[rand.nextInt(PALABRAS.length)] + " " +
                            PALABRAS[rand.nextInt(PALABRAS.length)] + " " +
                            rand.nextInt(1000);
            
            // Generar precio aleatorio entre 10.000 y 5.000.000
            // Formato necesario para que Producto.java lo parsee: "$ 10.000"
            int precioRaw = 10000 + rand.nextInt(4990000);
            String precioVenta = "$ " + String.format("%,d", precioRaw).replace(',', '.');

            // Crear objeto Producto compatible con el constructor
            Producto p = new Producto(
                titulo,                 // Título
                precioVenta,            // Precio Original 
                precioVenta,            // Precio Venta
                "0%",                   // Descuento
                "img_mock.jpg",         // Imagen
                "http://mock.url/" + i, // URL única
                TIENDAS[rand.nextInt(TIENDAS.length)] // Tienda
            );
            
            lista.add(p);
        }
        return lista;
    }

    private static void testAVL(ArrayList<Producto> datos, int n) {
        AVLTree avl = new AVLTree();

        // Medir Inserción
        long inicio = System.nanoTime();
        for (Producto p : datos) {
            avl.insert(p);
        }
        long fin = System.nanoTime();
        imprimirResultado("AVL", "Insercion", n, (fin - inicio));

        // Medir Búsqueda (Buscamos 1000 elementos aleatorios existentes)
        // No buscamos los N elementos para no hacer el test demasiado extenso, sino una muestra representativa
        int muestras = 1000;
        Random rand = new Random();
        
        inicio = System.nanoTime();
        for (int i = 0; i < muestras; i++) {
            Producto pObjetivo = datos.get(rand.nextInt(n));
            avl.buscar(pObjetivo.getTitulo());
        }
        fin = System.nanoTime();
        // Normalizamos el tiempo al equivalente de N operaciones para comparar en la gráfica
        double tiempoPromedioPorOp = (double)(fin - inicio) / muestras;
        long tiempoProyectadoN = (long)(tiempoPromedioPorOp * n);
        
        imprimirResultado("AVL", "Busqueda_Proyectada", n, tiempoProyectadoN);
    }


    private static void testBST(ArrayList<Producto> datos, int n) {
        BST bst = new BST();

        // Medir Inserción
        long inicio = System.nanoTime();
        for (Producto p : datos) {
            bst.insert(p);
        }
        long fin = System.nanoTime();
        imprimirResultado("BST", "Insercion", n, (fin - inicio));

        // Medir Búsqueda por Rango
        // Simulamos un rango que cubra aprox el 10% de los precios
        double min = 100000;
        double max = 500000;
        
        inicio = System.nanoTime();
        bst.buscarEnRango(min, max);
        fin = System.nanoTime();
        imprimirResultado("BST", "Busqueda_Rango", n, (fin - inicio));
    }


    private static void testHeap(ArrayList<Producto> datos, int n) {
        Heap heap = new Heap();

        // Medir Inserción
        long inicio = System.nanoTime();
        for (Producto p : datos) {
            heap.insert(p);
        }
        long fin = System.nanoTime();
        imprimirResultado("Heap", "Insercion", n, (fin - inicio));

        // Medir Extracción de los N más baratos (implica vaciar el heap o extraer N veces)
        // En el código tenemos getNMasBaratos
        inicio = System.nanoTime();
        // Extraemos el Top 100 para ver rendimiento
        heap.getNMasBaratos(100); 
        fin = System.nanoTime();
        imprimirResultado("Heap", "Get_Top_100", n, (fin - inicio));
    }

    private static void imprimirResultado(String estructura, String operacion, int n, long nanosegundos) {
        double milisegundos = nanosegundos / 1_000_000.0;
        // Formato CSV: Estructura, Operacion, N, Tiempo(ns), Tiempo(ms)
        System.out.printf("%s,%s,%d,%d,%.4f%n", estructura, operacion, n, nanosegundos, milisegundos);
    }
}