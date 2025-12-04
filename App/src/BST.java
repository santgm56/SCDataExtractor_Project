import java.util.ArrayList;

public class BST {
    private class Nodo {
        Producto producto;
        Nodo izquierdo;
        Nodo derecho;
        
        Nodo(Producto p) {
            this.producto = p;
        }
    }
    
    private Nodo raiz;
    
    // Constructor: recibe el ArrayList del DataManager
    public BST(ArrayList<Producto> productos) {
        this.raiz = null;
        for (Producto p : productos) {
            insertar(p);
        }
    }
    
    public void insertar(Producto p) {
        raiz = insertarRecursivo(raiz, p);
    }
    
    private Nodo insertarRecursivo(Nodo nodo, Producto p) {
        if (nodo == null) {
            return new Nodo(p);
        }
        
        // Ordenar por precio numérico
        if (p.getPrecioNumerico() < nodo.producto.getPrecioNumerico()) {
            nodo.izquierdo = insertarRecursivo(nodo.izquierdo, p);
        } else {
            nodo.derecho = insertarRecursivo(nodo.derecho, p);
        }
        
        return nodo;
    }
    
    // Buscar productos en rango de precios
    public ArrayList<Producto> buscarEnRango(double min, double max) {
        ArrayList<Producto> resultado = new ArrayList<>();
        buscarEnRangoRecursivo(raiz, min, max, resultado);
        return resultado;
    }
    
    private void buscarEnRangoRecursivo(Nodo nodo, double min, double max, 
                                        ArrayList<Producto> resultado) {
        if (nodo == null) return;
        
        double precio = nodo.producto.getPrecioNumerico();
        
        if (precio >= min && precio <= max) {
            resultado.add(nodo.producto);
        }
        
        if (precio > min) {
            buscarEnRangoRecursivo(nodo.izquierdo, min, max, resultado);
        }
        if (precio < max) {
            buscarEnRangoRecursivo(nodo.derecho, min, max, resultado);
        }
    }
    
    // Recorrido inorden (ordenado por precio)
    public ArrayList<Producto> getOrdenadoPorPrecio() {
        ArrayList<Producto> resultado = new ArrayList<>();
        inorden(raiz, resultado);
        return resultado;
    }
    
    private void inorden(Nodo nodo, ArrayList<Producto> resultado) {
        if (nodo == null) return;
        inorden(nodo.izquierdo, resultado);
        resultado.add(nodo.producto);
        inorden(nodo.derecho, resultado);
    }
}
