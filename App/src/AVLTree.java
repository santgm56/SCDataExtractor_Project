import java.util.ArrayList;

public class AVLTree {
    private class Nodo {
        Producto producto;
        Nodo left, right;
        int height;

        Nodo(Producto p) {
            this.producto = p;
            this.height = 1;
        }
    }

    private Nodo root;

    public AVLTree() {}

    public AVLTree(ArrayList<Producto> productos) {
        for (Producto p : productos)
            insert(p);
    }

    private int height(Nodo n) {
        return (n == null) ? 0 : n.height;
    }

    private int getBalance(Nodo n) {
        return (n == null) ? 0 : height(n.left) - height(n.right);
    }

    private Nodo rotateRight(Nodo y) {
        Nodo x = y.left;
        Nodo T2 = x.right;

        x.right = y;
        y.left = T2;

        y.height = Math.max(height(y.left), height(y.right)) + 1;
        x.height = Math.max(height(x.left), height(x.right)) + 1;

        return x;
    }

    private Nodo rotateLeft(Nodo x) {
        Nodo y = x.right;
        Nodo T2 = y.left;

        y.left = x;
        x.right = T2;

        x.height = Math.max(height(x.left), height(x.right)) + 1;
        y.height = Math.max(height(y.left), height(y.right)) + 1;

        return y;
    }

    // =============================================
    // INSERTAR POR tituloNormalizado
    // =============================================
    public void insert(Producto nuevo) {
        root = insertRec(root, nuevo);
    }

    private Nodo insertRec(Nodo node, Producto nuevo) {
        if (node == null)
            return new Nodo(nuevo);

        int cmp = nuevo.getTituloNormalizado()
                       .compareTo(node.producto.getTituloNormalizado());

        if (cmp < 0) {
            node.left = insertRec(node.left, nuevo);
        } else if (cmp > 0) {
            node.right = insertRec(node.right, nuevo);
        } else {
            return node; // evitar duplicado exacto
        }

        node.height = 1 + Math.max(height(node.left), height(node.right));

        int balance = getBalance(node);

        // Rotaciones
        if (balance > 1 && nuevo.getTituloNormalizado()
                .compareTo(node.left.producto.getTituloNormalizado()) < 0) {
            return rotateRight(node);
        }

        if (balance < -1 && nuevo.getTituloNormalizado()
                .compareTo(node.right.producto.getTituloNormalizado()) > 0) {
            return rotateLeft(node);
        }

        if (balance > 1 && nuevo.getTituloNormalizado()
                .compareTo(node.left.producto.getTituloNormalizado()) > 0) {
            node.left = rotateLeft(node.left);
            return rotateRight(node);
        }

        if (balance < -1 && nuevo.getTituloNormalizado()
                .compareTo(node.right.producto.getTituloNormalizado()) < 0) {
            node.right = rotateRight(node.right);
            return rotateLeft(node);
        }

        return node;
    }

    // =============================================
    // BÚSQUEDA NORMALIZADA (sin tildes)
    // =============================================
    public Producto buscar(String titulo) {
        return buscarRec(root, Producto.normalizar(titulo));
    }

    private Producto buscarRec(Nodo node, String tituloNorm) {
        if (node == null) return null;

        int cmp = tituloNorm.compareTo(node.producto.getTituloNormalizado());

        if (cmp == 0) return node.producto;
        if (cmp < 0) return buscarRec(node.left, tituloNorm);
        else return buscarRec(node.right, tituloNorm);

    }

    // =============================================
    // BÚSQUEDA PARCIAL (encuentra todos los que contengan el término)
    // =============================================
    public ArrayList<Producto> buscarPorTermino(String termino) {
        ArrayList<Producto> resultados = new ArrayList<>();
        String terminoNorm = Producto.normalizar(termino);
        buscarPorTerminoRec(root, terminoNorm, resultados);
        return resultados;
    }

    private void buscarPorTerminoRec(Nodo node, String terminoNorm, ArrayList<Producto> resultados) {
        if (node == null) return;

        buscarPorTerminoRec(node.left, terminoNorm, resultados);
        
        String tituloNorm = node.producto.getTituloNormalizado().toLowerCase();
        String busqueda = terminoNorm.toLowerCase();
        
        if (tituloNorm.contains(busqueda)) {
            resultados.add(node.producto);
        }
        
        buscarPorTerminoRec(node.right, terminoNorm, resultados);
    }

    // =============================================
    // MOSTRAR INORDER
    // =============================================
    public void inorder() {
        inorderRec(root);
    }

    private void inorderRec(Nodo node) {
        if (node == null) return;

        inorderRec(node.left);
        System.out.println(node.producto.getTitulo() +
                           " | Precio: " + node.producto.getPrecioVenta() +
                           " | Tienda: " + node.producto.getTienda());
        inorderRec(node.right);
    }

    // Mostrar árbol rotado
    public void mostrarAVL() {
        imprimirRec(root, 0);
    }

    private void imprimirRec(Nodo node, int nivel) {
        if (node == null) return;

        imprimirRec(node.right, nivel + 1);
        System.out.println("   ".repeat(nivel) + "• " + node.producto.getTitulo());
        imprimirRec(node.left, nivel + 1);
    }
}
