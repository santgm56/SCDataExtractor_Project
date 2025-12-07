import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.*;
import java.io.PrintStream;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.List;

/**
 * MainWindowDashboard.java
 * GUI tipo dashboard para tu SC Data Extractor.
 *
 * Requiere las clases externas del proyecto:
 * - DataManager
 * - Producto
 * - RunPython
 * - AVLTree, BST, Heap, HistorialDB (ya usados por DataManager)
 *
 * Instrucciones:
 * - Coloca este archivo en el paquete gui.
 * - Compila con el resto del proyecto.
 * - Ejecuta desde run.ps1 / run.bat tal como lo configuraste para que el entorno y venv estén correctos.
 */
public class MainWindowDashboard extends JFrame {

    private DataManager manager;

    // COMPONENTES GENERALES
    private JTabbedPane tabs;
    private JTextArea txtLog;

    // TAB: Scraping
    private JComboBox<String> cmbTienda;
    private JTextField txtProducto;
    private JSpinner spnItems;
    private JSpinner spnPaginas;
    private JCheckBox chkReporte;
    private JButton btnScrap;
    private JButton btnCancelarScrap;
    private SwingWorker<Void, String> worker; // para cancelar si se necesita

    // TAB: Productos (tabla)
    private JTable tablaResultados;
    private DefaultTableModel tableModel;
    private JButton btnRecargar;
    private JButton btnLimpiarHistorial;

    // TAB: Estadísticas
    private JLabel lblTotal, lblML, lblAlk;

    // TAB: AVL
    private JTextArea txtAVL;

    // TAB: Heap (Top N)
    private JTextField txtTopN;
    private JButton btnMostrarTop;
    private JTextField txtBuscarHeap;
    private JTable tablaHeap;
    private DefaultTableModel heapModel;

    // TAB: BST (Rango)
    private JTextField txtMinPrice, txtMaxPrice;
    private JButton btnBuscarRango;
    private JTable tablaRango;
    private DefaultTableModel rangoModel;
    private JTextField txtBuscarRangoTerm;

    public MainWindowDashboard() {
        super("SC Data Extractor - Dashboard");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1100, 700);
        setLocationRelativeTo(null);

        // Inicializar DataManager
        manager = new DataManager();

        initComponents();
        layoutComponents();
        attachListeners();

        // Cargar tabla inicial
        cargarHistorialEnTabla();
        actualizarEstadisticas();
    }

    private void initComponents() {
        tabs = new JTabbedPane();

        // Logging
        txtLog = new JTextArea();
        txtLog.setEditable(false);
        txtLog.setLineWrap(true);

        // Scraping tab
        cmbTienda = new JComboBox<>(new String[]{"MercadoLibre", "Alkosto"});
        txtProducto = new JTextField(20);
        spnItems = new JSpinner(new SpinnerNumberModel(1, 1, 10, 1));
        spnPaginas = new JSpinner(new SpinnerNumberModel(1, 1, 10, 1));
        chkReporte = new JCheckBox("Generar reporte");
        btnScrap = new JButton("Ejecutar scraping");
        btnCancelarScrap = new JButton("Cancelar");
        btnCancelarScrap.setEnabled(false);

        // Productos table
        tableModel = new DefaultTableModel();
        tableModel.addColumn("ID");
        tableModel.addColumn("Nombre");
        tableModel.addColumn("Precio");
        tableModel.addColumn("Tienda");
        tableModel.addColumn("URL");

        tablaResultados = new JTable(tableModel);
        tablaResultados.setAutoCreateRowSorter(true);

        btnRecargar = new JButton("Recargar productos");
        btnLimpiarHistorial = new JButton("Limpiar historial");

        // Estadísticas
        lblTotal = new JLabel("Total: 0");
        lblML = new JLabel("MercadoLibre: 0");
        lblAlk = new JLabel("Alkosto: 0");

        // AVL
        txtAVL = new JTextArea();
        txtAVL.setEditable(false);

        // Heap (Top N)
        txtTopN = new JTextField("5", 4);
        btnMostrarTop = new JButton("Mostrar Top N");
        txtBuscarHeap = new JTextField(15);
        heapModel = new DefaultTableModel();
        heapModel.addColumn("Nombre");
        heapModel.addColumn("Precio");
        heapModel.addColumn("Tienda");
        tablaHeap = new JTable(heapModel);


        // BST (rango)
        txtBuscarRangoTerm = new JTextField(15);
        txtMinPrice = new JTextField("0", 6);
        txtMaxPrice = new JTextField("1000000", 6);
        btnBuscarRango = new JButton("Buscar Rango");
        rangoModel = new DefaultTableModel();
        rangoModel.addColumn("Nombre");
        rangoModel.addColumn("Precio");
        rangoModel.addColumn("Tienda");
        tablaRango = new JTable(rangoModel);
    }

    private void layoutComponents() {
        // Panel Scraping
        JPanel pnlScrap = new JPanel();
        pnlScrap.setLayout(new GridLayout(3, 1, 10, 10));

        JPanel fila1 = new JPanel(new FlowLayout(FlowLayout.LEFT));
        fila1.add(new JLabel("Tienda:"));
        fila1.add(cmbTienda);
        fila1.add(new JLabel("Producto:"));
        fila1.add(txtProducto);

        JPanel fila2 = new JPanel(new FlowLayout(FlowLayout.LEFT));
        fila2.add(new JLabel("Items:"));
        fila2.add(spnItems);
        fila2.add(new JLabel("Páginas:"));
        fila2.add(spnPaginas);
        fila2.add(chkReporte);

        JPanel fila3 = new JPanel(new FlowLayout(FlowLayout.LEFT));
        fila3.add(btnScrap);
        fila3.add(btnCancelarScrap);

        pnlScrap.add(fila1);
        pnlScrap.add(fila2);
        pnlScrap.add(fila3);


        // Panel Productos
        JPanel pnlProductos = new JPanel(new BorderLayout(6, 6));
        pnlProductos.add(new JScrollPane(tablaResultados), BorderLayout.CENTER);
        JPanel pnlStatsBottom = new JPanel(new GridLayout(1, 3, 10, 10));
        pnlStatsBottom.setBorder(BorderFactory.createTitledBorder("Estadísticas"));
        pnlStatsBottom.add(lblTotal);
        pnlStatsBottom.add(lblML);
        pnlStatsBottom.add(lblAlk);
        pnlProductos.add(pnlStatsBottom, BorderLayout.SOUTH);
        JPanel pnlProdButtons = new JPanel(new FlowLayout(FlowLayout.LEFT));
        pnlProdButtons.add(btnRecargar);
        pnlProdButtons.add(btnLimpiarHistorial);
        pnlProductos.add(pnlProdButtons, BorderLayout.NORTH);

        // Panel Estadísticas
        JPanel pnlStats = new JPanel(new BorderLayout());

        JPanel statsBox = new JPanel(new GridLayout(1, 3, 10, 10));
        statsBox.setBorder(BorderFactory.createTitledBorder("Resumen"));

        statsBox.add(lblTotal);
        statsBox.add(lblML);
        statsBox.add(lblAlk);

        pnlStats.add(statsBox, BorderLayout.NORTH);


        // Panel AVL
        JPanel pnlAVL = new JPanel(new BorderLayout());
        pnlAVL.add(new JScrollPane(txtAVL), BorderLayout.CENTER);

        // Panel Heap (Top N)
        JPanel pnlHeap = new JPanel(new BorderLayout());
        JPanel topForm = new JPanel(new FlowLayout(FlowLayout.LEFT));
        topForm.add(new JLabel("Buscar:"));
        topForm.add(txtBuscarHeap);
        topForm.add(new JLabel("N:"));
        topForm.add(txtTopN);
        topForm.add(btnMostrarTop);
        pnlHeap.add(topForm, BorderLayout.NORTH);
        pnlHeap.add(new JScrollPane(tablaHeap), BorderLayout.CENTER);

        // Panel BST Rango
        JPanel pnlRango = new JPanel(new BorderLayout());
        JPanel rangoForm = new JPanel(new FlowLayout(FlowLayout.LEFT));
        rangoForm.add(new JLabel("Buscar:"));
        rangoForm.add(txtBuscarRangoTerm);
        rangoForm.add(new JLabel("Min $"));
        rangoForm.add(txtMinPrice);
        rangoForm.add(new JLabel("Max $"));
        rangoForm.add(txtMaxPrice);
        rangoForm.add(btnBuscarRango);
        pnlRango.add(rangoForm, BorderLayout.NORTH);
        pnlRango.add(new JScrollPane(tablaRango), BorderLayout.CENTER);

        // Añadir pestañas
        tabs.addTab("Scraping", pnlScrap);
        tabs.addTab("Productos", pnlProductos);
        tabs.addTab("AVL (inorder)", pnlAVL);
        tabs.addTab("Heap (Top N)", pnlHeap);
        tabs.addTab("BST (Rango)", pnlRango);

        // Layout general: pestañas + log lateral
        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(tabs, BorderLayout.CENTER);

        // Barra inferior con logs rápidos
        JPanel bottom = new JPanel(new BorderLayout());
        bottom.add(new JLabel("Logs:"), BorderLayout.NORTH);
        bottom.add(new JScrollPane(txtLog), BorderLayout.CENTER);
        bottom.setPreferredSize(new Dimension(getWidth(), 180));
        getContentPane().add(bottom, BorderLayout.SOUTH);
    }

    private void attachListeners() {
        // Botón ejecutar scraping
        btnScrap.addActionListener(e -> iniciarScrapingDesdeGUI());

        btnCancelarScrap.addActionListener(e -> {
            if (worker != null && !worker.isDone()) {
                worker.cancel(true);
                appendLog("Operación de scraping cancelada por el usuario.");
                btnCancelarScrap.setEnabled(false);
                btnScrap.setEnabled(true);
            }
        });

        btnRecargar.addActionListener(e -> {
            cargarHistorialEnTabla();
            actualizarEstadisticas();
            appendLog("Tabla recargada desde DB.");
        });

        btnLimpiarHistorial.addActionListener(e -> {
            int r = JOptionPane.showConfirmDialog(this, "¿Limpiar todo el historial (BD)?", "Confirmar", JOptionPane.YES_NO_OPTION);
            if (r == JOptionPane.YES_OPTION) {
                manager.limpiarHistorial();
                cargarHistorialEnTabla();
                actualizarEstadisticas();
                appendLog("Historial limpiado.");
            }
        });

        // AVL: mostrar inorder en textarea al cambiar a pestaña
        tabs.addChangeListener(evt -> {
            int idx = tabs.getSelectedIndex();
            String title = tabs.getTitleAt(idx);
            if ("AVL (inorder)".equals(title)) {
                mostrarAVL();
            }
        });

        btnMostrarTop.addActionListener(e -> {
            try {
                int n = Integer.parseInt(txtTopN.getText().trim());
                mostrarTopN(n);
            } catch (NumberFormatException ex) {
                JOptionPane.showMessageDialog(this, "Ingrese un número válido para N.");
            }
        });

        btnBuscarRango.addActionListener(e -> {
            try {
                double min = Double.parseDouble(txtMinPrice.getText().replaceAll("[^0-9.]", ""));
                double max = Double.parseDouble(txtMaxPrice.getText().replaceAll("[^0-9.]", ""));
                buscarPorRango(min, max);
            } catch (NumberFormatException ex) {
                JOptionPane.showMessageDialog(this, "Ingrese valores numéricos válidos para rango.");
            }
        });
    }

    // ---------- ACCIONES PRINCIPALES ----------

    private void iniciarScrapingDesdeGUI() {
        String producto = txtProducto.getText().trim();
        if (producto.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Ingrese un término de búsqueda.");
            return;
        }
        int tienda = cmbTienda.getSelectedIndex() + 1;
        int items = (int) spnItems.getValue();
        int paginas = (int) spnPaginas.getValue();
        boolean generarReporte = chkReporte.isSelected();

        String productoNorm = normalizarTexto(producto);

        // Deshabilitar botón y habilitar cancelar
        btnScrap.setEnabled(false);
        btnCancelarScrap.setEnabled(true);

        appendLog("Iniciando scraping para: " + producto + " (tienda " + tienda + ") ...");

        // Usar SwingWorker para no bloquear la UI
        worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() throws Exception {
                // manager.aggDatosHistorial hace RunPython internamente y actualiza BD
                manager.aggDatosHistorial(tienda, productoNorm, items, paginas, generarReporte);
                publish("Scraping finalizado (background).");
                return null;
            }

            @Override
            protected void process(List<String> chunks) {
                for (String s : chunks) appendLog(s);
            }

            @Override
            protected void done() {
                btnScrap.setEnabled(true);
                btnCancelarScrap.setEnabled(false);
                try {
                    get(); // para lanzar excepción si falló
                    appendLog("Tarea finalizada con éxito. Actualizando tabla...");
                    cargarHistorialEnTabla();
                    actualizarEstadisticas();
                } catch (Exception ex) {
                    appendLog("Error durante scraping: " + ex.getMessage());
                    JOptionPane.showMessageDialog(MainWindowDashboard.this, "Error: " + ex.getMessage());
                }
            }
        };

        worker.execute();
    }

    private void cargarHistorialEnTabla() {
        tableModel.setRowCount(0);
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        int idx = 1;
        for (Producto p : productos) {
            tableModel.addRow(new Object[]{
                    idx++,
                    p.getTitulo(),
                    p.getPrecioVenta(),
                    p.getTienda(),
                    p.getUrl()
            });
        }
    }

    private void actualizarEstadisticas() {
        int total = manager.getTotalProductos();
        int ml = manager.getProductosPorTienda("MercadoLibre").size();
        int alk = manager.getProductosPorTienda("Alkosto").size();

        lblTotal.setText("Total productos: " + total);
        lblML.setText("MercadoLibre: " + ml);
        lblAlk.setText("Alkosto: " + alk);
    }

    private void mostrarAVL() {
        txtAVL.setText("");

        try {
            // CAPTURAR la salida de System.out TEMPORALMENTE
            java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();
            java.io.PrintStream ps = new java.io.PrintStream(baos);
            PrintStream old = System.out;

            System.setOut(ps);
            manager.getAVL().inorder(); // imprime aquí

            System.out.flush();
            System.setOut(old);

            txtAVL.setText(baos.toString());

        } catch (Exception ex) {
            txtAVL.setText("Error mostrando AVL.");
        }
    }


    private void mostrarTopN(int n) {

        if (manager.getHeap() == null || manager.getHeap().isEmpty()) {
            JOptionPane.showMessageDialog(this, "No hay productos en el Heap.");
            return;
        }

        heapModel.setRowCount(0);

        // --- 1. Obtener término de búsqueda ---
        String termino = txtBuscarHeap.getText().trim().toLowerCase();
        String terminoNorm = normalizarTexto(termino);

        ArrayList<Producto> filtrados;

        if (termino.isEmpty()) {
            filtrados = manager.getHistorialCompleto();
        } else {
            // Usamos AVL como filtro rápido (sin modificarlo)
            filtrados = manager.getAVL().buscarPorTermino(terminoNorm);

            if (filtrados.isEmpty()) {
                JOptionPane.showMessageDialog(this, "No hay productos que coincidan con el término.");
                return;
            }
        }

        // --- 2. Crear heap temporal con los filtrados ---
        Heap temp = new Heap();
        for (Producto p : filtrados) temp.insert(p);

        List<Producto> top = temp.getNMasBaratos(n);

        // --- 3. Llenar tabla ---
        for (Producto p : top) {
            heapModel.addRow(new Object[]{
                p.getTitulo(),
                p.getPrecioVenta(),
                p.getTienda()
            });
        }

        appendLog("Top " + n + " productos más baratos: " + top.size() + " resultados.");
    }


    private void buscarPorRango(double min, double max) {

        rangoModel.setRowCount(0);

        // --- 1. Obtener término de búsqueda ---
        String termino = txtBuscarRangoTerm.getText().trim().toLowerCase();
        String terminoNorm = normalizarTexto(termino);

        ArrayList<Producto> filtrados;

        if (termino.isEmpty()) {
            filtrados = manager.getHistorialCompleto();
        } else {
            filtrados = manager.getAVL().buscarPorTermino(terminoNorm);

            if (filtrados.isEmpty()) {
                appendLog("No se encontraron productos con el término.");
                return;
            }
        }

        // --- 2. Crear BST temporal con filtrados ---
        BST bst = new BST(filtrados);

        // --- 3. Buscar por rango ---
        ArrayList<Producto> enRango = bst.buscarEnRango(min, max);

        for (Producto p : enRango) {
            rangoModel.addRow(new Object[]{
                p.getTitulo(),
                p.getPrecioVenta(),
                p.getTienda()
            });
        }

        appendLog("Búsqueda en rango completada. Encontrados: " + enRango.size());
    }


    // ------------ UTILIDADES -------------
    private void appendLog(String msg) {
        txtLog.append(msg + "\n");
        // autoscroll
        txtLog.setCaretPosition(txtLog.getDocument().getLength());
    }

    private static String normalizarTexto(String texto) {
        if (texto == null) return "";
        String normalizado = Normalizer.normalize(texto, Normalizer.Form.NFD);
        normalizado = normalizado.replaceAll("[^\\p{ASCII}]", "");
        return normalizado.toLowerCase();
    }

    // -------------- MAIN ---------------
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            MainWindowDashboard w = new MainWindowDashboard();
            w.setVisible(true);
        });
    }
}
