import java.util.ArrayList;

public class Heap {

    private ArrayList<Producto> heap;

    public Heap() {
        heap = new ArrayList<>();
    }

    public Heap(ArrayList<Producto> productos) {
        heap = new ArrayList<>(productos);
        buildHeap();
    }

    private void buildHeap() {
        for (int i = heap.size() / 2; i >= 0; i--) {
            heapifyDown(i);
        }
    }

    // 🔥 INSERTAR PRODUCTO EN EL HEAP
    public void insert(Producto nuevo) {
        heap.add(nuevo);
        heapifyUp(heap.size() - 1);
    }

    private void heapifyUp(int index) {
        while (index > 0) {
            int parent = (index - 1) / 2;

            if (heap.get(index).getPrecioNumerico() < heap.get(parent).getPrecioNumerico()) {
                swap(index, parent);
                index = parent;
            } else {
                break;
            }
        }
    }

    private void heapifyDown(int index) {
        int left, right, smallest;

        while (true) {
            left = 2 * index + 1;
            right = 2 * index + 2;
            smallest = index;

            if (left < heap.size() &&
                heap.get(left).getPrecioNumerico() < heap.get(smallest).getPrecioNumerico()) {
                smallest = left;
            }

            if (right < heap.size() &&
                heap.get(right).getPrecioNumerico() < heap.get(smallest).getPrecioNumerico()) {
                smallest = right;
            }

            if (smallest == index) break;

            swap(index, smallest);
            index = smallest;
        }
    }

    public Producto extractMin() {
        if (heap.isEmpty()) return null;

        Producto min = heap.get(0);
        Producto last = heap.remove(heap.size() - 1);

        if (!heap.isEmpty()) {
            heap.set(0, last);
            heapifyDown(0);
        }

        return min;
    }

    private void swap(int i, int j) {
        Producto temp = heap.get(i);
        heap.set(i, heap.get(j));
        heap.set(j, temp);
    }

    public boolean isEmpty() { return heap.isEmpty(); }

    public int size() { return heap.size(); }

    public Producto peek() {
        return heap.isEmpty() ? null : heap.get(0);
    }

    // =============================================
    // OBTENER N PRODUCTOS MÁS BARATOS
    // =============================================
    public ArrayList<Producto> getNMasBaratos(int n) {
        ArrayList<Producto> resultado = new ArrayList<>();
        
        // Crear copia del heap para no modificar el original
        Heap copia = new Heap();
        for (Producto p : this.heap) {
            copia.insert(p);
        }
        
        // Extraer los N más baratos
        int cantidad = Math.min(n, copia.size());
        for (int i = 0; i < cantidad; i++) {
            Producto min = copia.extractMin();
            if (min != null) {
                resultado.add(min);
            }
        }
        
        return resultado;
    }

    public void mostrarHeap() {
        if (heap.isEmpty()) {
            System.out.println("El heap está vacío.");
            return;
        }

        System.out.println("=== CONTENIDO DEL HEAP (MIN-HEAP POR PRECIO) ===");
        for (int i = 0; i < heap.size(); i++) {
            Producto p = heap.get(i);
            System.out.println(
                i + ". Precio: " + p.getPrecioNumerico() +
                " | Título: " + p.getTitulo() +
                " | Tienda: " + p.getTienda()
            );
        }
    }
}
