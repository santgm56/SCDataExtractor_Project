import java.util.ArrayList;

// BST: Binary Search Tree ordenado por PRECIO para búsquedas por rango
public class BST {
    
    private class Nodo {
        Producto producto;
        Nodo left, right;
        
        Nodo(Producto p) {
            this.producto = p;
        }
    }
    
    private Nodo root;
    
    public BST() {
        this.root = null;
    }
    
    public BST(ArrayList<Producto> productos) {
        this.root = null;
        for (Producto p : productos) {
            insert(p);
        }
    }
    
    // Insertar producto ordenado por precio
    public void insert(Producto producto) {
        root = insertRec(root, producto);
    }
    
    private Nodo insertRec(Nodo node, Producto producto) {
        if (node == null) {
            return new Nodo(producto);
        }
        
        // Comparar por precio numérico
        if (producto.getPrecioNumerico() < node.producto.getPrecioNumerico()) {
            node.left = insertRec(node.left, producto);
        } else {
            node.right = insertRec(node.right, producto);
        }
        
        return node;
    }
    
    // =============================================
    // BÚSQUEDA POR RANGO DE PRECIO
    // =============================================
    public ArrayList<Producto> buscarEnRango(double precioMin, double precioMax) {
        ArrayList<Producto> resultado = new ArrayList<>();
        buscarEnRangoRec(root, precioMin, precioMax, resultado);
        return resultado;
    }
    
    private void buscarEnRangoRec(Nodo node, double min, double max, ArrayList<Producto> resultado) {
        if (node == null) return;
        
        double precio = node.producto.getPrecioNumerico();
        
        // Si el precio está en el rango, agregarlo
        if (precio >= min && precio <= max) {
            resultado.add(node.producto);
        }
        
        // Buscar en subárbol izquierdo si puede haber precios en rango
        if (precio > min) {
            buscarEnRangoRec(node.left, min, max, resultado);
        }
        
        // Buscar en subárbol derecho si puede haber precios en rango
        if (precio < max) {
            buscarEnRangoRec(node.right, min, max, resultado);
        }
    }
    
    // =============================================
    // OBTENER PRODUCTOS ORDENADOS POR PRECIO
    // =============================================
    public ArrayList<Producto> getOrdenadoPorPrecio() {
        ArrayList<Producto> resultado = new ArrayList<>();
        inorderRec(root, resultado);
        return resultado;
    }
    
    private void inorderRec(Nodo node, ArrayList<Producto> resultado) {
        if (node == null) return;
        
        inorderRec(node.left, resultado);
        resultado.add(node.producto);
        inorderRec(node.right, resultado);
    }
}
