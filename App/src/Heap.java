import java.util.ArrayList;

public class Heap {
    private ArrayList<Producto> heap;
    
    public Heap(ArrayList<Producto> productos) {
        this.heap = new ArrayList<>(productos);
        construirHeap();
    }
    
    private void construirHeap() {
        // Heapify desde el último padre hasta la raíz
        for (int i = heap.size() / 2 - 1; i >= 0; i--) {
            heapifyDown(i);
        }
    }
    
    private void heapifyDown(int index) {
        int menor = index;
        int izq = 2 * index + 1;
        int der = 2 * index + 2;
        
        if (izq < heap.size() && 
            heap.get(izq).getPrecioNumerico() < heap.get(menor).getPrecioNumerico()) {
            menor = izq;
        }
        
        if (der < heap.size() && 
            heap.get(der).getPrecioNumerico() < heap.get(menor).getPrecioNumerico()) {
            menor = der;
        }
        
        if (menor != index) {
            // Swap
            Producto temp = heap.get(index);
            heap.set(index, heap.get(menor));
            heap.set(menor, temp);
            
            heapifyDown(menor);
        }
    }
    
    // Obtener el producto más barato (raíz del min-heap)
    public Producto getMasBarato() {
        if (heap.isEmpty()) return null;
        return heap.get(0);
    }
    
    // Obtener los N productos más baratos
    public ArrayList<Producto> getNMasBaratos(int n) {
        ArrayList<Producto> resultado = new ArrayList<>();
        Heap copia = new Heap(new ArrayList<>(heap));
        
        for (int i = 0; i < n && !copia.heap.isEmpty(); i++) {
            resultado.add(copia.extraerMinimo());
        }
        
        return resultado;
    }
    
    private Producto extraerMinimo() {
        if (heap.isEmpty()) return null;
        
        Producto minimo = heap.get(0);
        Producto ultimo = heap.remove(heap.size() - 1);
        
        if (!heap.isEmpty()) {
            heap.set(0, ultimo);
            heapifyDown(0);
        }
        
        return minimo;
    }
}
