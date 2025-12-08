import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.JTableHeader;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.*;
import java.io.PrintStream;
import java.io.File;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.List;
import javax.sound.sampled.*;

public class MainWindowDashboard extends JFrame {

    // ==============================
    // TEMA EN ESCALA DE GRISES
    // ==============================
    static {
        aplicarTemaGris();
    }

    // Tamaños grandes
    private final Font FONT_TITLE = new Font("Segoe UI", Font.BOLD, 28);
    private final Font FONT_SUBTITLE = new Font("Segoe UI", Font.PLAIN, 20);
    private final Font FONT_LABEL = new Font("Segoe UI", Font.BOLD, 20);
    private final Font FONT_BUTTON = new Font("Segoe UI", Font.BOLD, 20);
    private final Font FONT_INPUT = new Font("Segoe UI", Font.PLAIN, 20);
    private final Font FONT_TABLE = new Font("Segoe UI", Font.PLAIN, 18);
    private final Font FONT_TABLE_HEADER = new Font("Segoe UI", Font.BOLD, 18);


    private Color bgColor = new Color(127, 127, 127);
    private Color panelColor = new Color(250, 250, 250);
    private Color bgTable = new Color(195, 195, 195);

    // ==============================  
    // ATRIBUTOS
    // ==============================

    private DataManager manager;

    private JTabbedPane tabs;
    private JTextArea txtLog;

    private JComboBox<String> cmbTienda;
    private JTextField txtProducto;
    private JSpinner spnItems;
    private JSpinner spnPaginas;
    private JCheckBox chkReporte;
    private JButton btnScrap;
    private JButton btnCancelarScrap;
    private SwingWorker<Void, String> worker;

    private JTable tablaResultados;
    private DefaultTableModel tableModel;
    private JButton btnRecargar;
    private JButton btnLimpiarHistorial;

    private JLabel lblTotal, lblML, lblAlk;

    private JTextArea txtAVL;

    private JTextField txtTopN;
    private JButton btnMostrarTop;
    private JTextField txtBuscarHeap;
    private JTable tablaHeap;
    private DefaultTableModel heapModel;

    private JTextField txtMinPrice, txtMaxPrice;
    private JButton btnBuscarRango;
    private JTable tablaRango;
    private DefaultTableModel rangoModel;
    private JTextField txtBuscarRangoTerm;

    private Clip backgroundClip;
    private boolean isMuted = false;

    // ==============================
    // CONSTRUCTOR
    // ==============================
    public MainWindowDashboard() {
        super("SC Data Extractor - Dashboard");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 780);
        setLocationRelativeTo(null);

        manager = new DataManager();

        initComponents();
        layoutComponents();
        attachListeners();

        playBackgroundMusic("../resources/background.wav");
        showWelcomeDialog();

        cargarHistorialEnTabla();
        actualizarEstadisticas();
    }

    // ==============================
    // INICIALIZACIÓN DE COMPONENTES
    // ==============================
    private void initComponents() {

        tabs = new JTabbedPane();
        tabs.setFont(FONT_BUTTON);

        txtLog = new JTextArea();
        txtLog.setEditable(false);
        txtLog.setLineWrap(true);
        txtLog.setFont(FONT_INPUT);

        // Scraping tab
        cmbTienda = new JComboBox<>(new String[]{"MercadoLibre", "Alkosto"});
        cmbTienda.setFont(FONT_INPUT);
        cmbTienda.setPreferredSize(new Dimension(220, 40));

        txtProducto = new JTextField(25);
        txtProducto.setFont(FONT_INPUT);
        txtProducto.setPreferredSize(new Dimension(260, 40));

        spnItems = new JSpinner(new SpinnerNumberModel(1, 1, 10, 1));
        spnItems.setFont(FONT_INPUT);
        spnItems.setPreferredSize(new Dimension(90, 40));

        spnPaginas = new JSpinner(new SpinnerNumberModel(1, 1, 10, 1));
        spnPaginas.setFont(FONT_INPUT);
        spnPaginas.setPreferredSize(new Dimension(90, 40));

        chkReporte = new JCheckBox("Generar reporte");
        chkReporte.setFont(FONT_LABEL);
        chkReporte.setBackground(bgColor);
        chkReporte.setForeground(Color.BLACK);

        btnScrap = new JButton("Ejecutar scraping");
        btnScrap.setFont(FONT_BUTTON);
        btnScrap.setPreferredSize(new Dimension(230, 50));

        btnCancelarScrap = new JButton("Cancelar");
        btnCancelarScrap.setFont(FONT_BUTTON);
        btnCancelarScrap.setPreferredSize(new Dimension(230, 50));
        btnCancelarScrap.setEnabled(false);

        // Tabla Productos
        tableModel = new DefaultTableModel(new String[]{"ID", "Nombre", "Precio", "Tienda", "URL"}, 0);
        tablaResultados = new JTable(tableModel);
        tablaResultados.setFont(FONT_TABLE);
        tablaResultados.setRowHeight(32);
        tablaResultados.setBackground(bgTable);
        

        JTableHeader header = tablaResultados.getTableHeader();
        header.setFont(FONT_TABLE_HEADER);

        btnRecargar = new JButton("Recargar productos");
        btnRecargar.setFont(FONT_BUTTON);
        btnRecargar.setPreferredSize(new Dimension(240, 50));

        btnLimpiarHistorial = new JButton("Limpiar historial");
        btnLimpiarHistorial.setFont(FONT_BUTTON);
        btnLimpiarHistorial.setPreferredSize(new Dimension(240, 50));

        lblTotal = new JLabel("Total: 0");
        lblML = new JLabel("MercadoLibre: 0");
        lblAlk = new JLabel("Alkosto: 0");

        lblTotal.setFont(FONT_LABEL);
        lblML.setFont(FONT_LABEL);
        lblAlk.setFont(FONT_LABEL);

        txtAVL = new JTextArea();
        txtAVL.setFont(FONT_INPUT);
        txtAVL.setEditable(false);

        // Heap
        txtTopN = new JTextField("5", 6);
        txtTopN.setFont(FONT_INPUT);
        txtTopN.setPreferredSize(new Dimension(80, 40));

        btnMostrarTop = new JButton("Mostrar Top N");
        btnMostrarTop.setFont(FONT_BUTTON);
        btnMostrarTop.setPreferredSize(new Dimension(200, 50));

        txtBuscarHeap = new JTextField(20);
        txtBuscarHeap.setFont(FONT_INPUT);
        txtBuscarHeap.setPreferredSize(new Dimension(240, 40));

        heapModel = new DefaultTableModel(new String[]{"Nombre", "Precio", "Tienda"}, 0);
        tablaHeap = new JTable(heapModel);
        tablaHeap.setFont(FONT_TABLE);
        tablaHeap.setRowHeight(32);
        tablaHeap.getTableHeader().setFont(FONT_TABLE_HEADER);
        tablaHeap.setBackground(bgTable);
        // Rango (BST)
        txtBuscarRangoTerm = new JTextField(20);
        txtBuscarRangoTerm.setFont(FONT_INPUT);
        txtBuscarRangoTerm.setPreferredSize(new Dimension(240, 40));

        txtMinPrice = new JTextField("0", 10);
        txtMinPrice.setFont(FONT_INPUT);
        txtMinPrice.setPreferredSize(new Dimension(140, 40));

        txtMaxPrice = new JTextField("1000000", 10);
        txtMaxPrice.setFont(FONT_INPUT);
        txtMaxPrice.setPreferredSize(new Dimension(140, 40));

        btnBuscarRango = new JButton("Buscar Rango");
        btnBuscarRango.setFont(FONT_BUTTON);
        btnBuscarRango.setPreferredSize(new Dimension(200, 50));

        rangoModel = new DefaultTableModel(new String[]{"Nombre", "Precio", "Tienda"}, 0);
        tablaRango = new JTable(rangoModel);
        tablaRango.setFont(FONT_TABLE);
        tablaRango.setRowHeight(32);
        tablaRango.getTableHeader().setFont(FONT_TABLE_HEADER);
        tablaRango.setBackground(bgTable);
    }

    // ==============================
    // LAYOUT
    // ==============================
    private void layoutComponents() {

       // PANEL SCRAPING
        JPanel pnlScrap = new JPanel(new BorderLayout());
        pnlScrap.setBackground(bgColor);
        pnlScrap.setBorder(new EmptyBorder(30, 30, 30, 30));

        // Contenedor interno para centrar todo
        JPanel contenedorCentro = new JPanel();
        contenedorCentro.setBackground(bgColor);
        contenedorCentro.setLayout(new BoxLayout(contenedorCentro, BoxLayout.Y_AXIS));

        // FILA 1
        JPanel fila1 = new JPanel(new FlowLayout(FlowLayout.CENTER, 15, 15));
        fila1.setBackground(bgColor);
        fila1.add(crearLabel("Tienda:"));
        fila1.add(cmbTienda);
        fila1.add(crearLabel("Producto:"));
        fila1.add(txtProducto);

        // FILA 2
        JPanel fila2 = new JPanel(new FlowLayout(FlowLayout.CENTER, 15, 15));
        fila2.setBackground(bgColor);
        fila2.add(crearLabel("Items:"));
        fila2.add(spnItems);
        fila2.add(crearLabel("Páginas:"));
        fila2.add(spnPaginas);
        fila2.add(chkReporte);

        // FILA 3
        JPanel fila3 = new JPanel(new FlowLayout(FlowLayout.CENTER, 15, 15));
        fila3.setBackground(bgColor);
        fila3.add(btnScrap);
        fila3.add(btnCancelarScrap);

        // Añadir filas al contenedor
        contenedorCentro.add(fila1);
        contenedorCentro.add(fila2);
        contenedorCentro.add(fila3);

        // Centrar verticalmente usando BorderLayout
        pnlScrap.add(contenedorCentro, BorderLayout.CENTER);


        // PANEL PRODUCTOS
        JPanel pnlProductos = new JPanel(new BorderLayout());
        pnlProductos.setBackground(bgColor);

        JScrollPane spProd = new JScrollPane(tablaResultados);
        aumentarScrollbars(spProd);
        pnlProductos.add(spProd, BorderLayout.CENTER);

        JPanel pnlTopProd = new JPanel(new FlowLayout(FlowLayout.LEFT));
        pnlTopProd.setBackground(bgColor);
        pnlTopProd.add(btnRecargar);
        pnlTopProd.add(btnLimpiarHistorial);
        pnlProductos.add(pnlTopProd, BorderLayout.NORTH);

        JPanel pnlStats = new JPanel(new GridLayout(1, 3));
        pnlStats.setBackground(panelColor);
        pnlStats.add(lblTotal);
        pnlStats.add(lblML);
        pnlStats.add(lblAlk);

        pnlProductos.add(pnlStats, BorderLayout.SOUTH);

        // AVL
        JPanel pnlAVL = new JPanel(new BorderLayout());
        pnlAVL.setBackground(bgColor);

        // Título del AVL
        JLabel tituloAVL = new JLabel("AVL TREE (Orden alfabético)");
        tituloAVL.setFont(new Font("Segoe UI", Font.BOLD, 22));
        tituloAVL.setHorizontalAlignment(SwingConstants.CENTER);
        tituloAVL.setBorder(new EmptyBorder(10, 0, 10, 0));
        tituloAVL.setForeground(new Color(70, 70, 70));

        pnlAVL.add(tituloAVL, BorderLayout.NORTH);
        pnlAVL.add(new JScrollPane(txtAVL), BorderLayout.CENTER);


        // HEAP
        JPanel pnlHeap = new JPanel(new BorderLayout());
        pnlHeap.setBackground(bgColor);

        JPanel heapTop = new JPanel(new FlowLayout());
        heapTop.setBackground(bgColor);
        heapTop.add(crearLabel("Buscar:"));
        heapTop.add(txtBuscarHeap);
        heapTop.add(crearLabel("N:"));
        heapTop.add(txtTopN);
        heapTop.add(btnMostrarTop);

        pnlHeap.add(heapTop, BorderLayout.NORTH);

        JScrollPane spHeap = new JScrollPane(tablaHeap);
        aumentarScrollbars(spHeap);
        pnlHeap.add(spHeap, BorderLayout.CENTER);

        // RANGO
        JPanel pnlRango = new JPanel(new BorderLayout());
        pnlRango.setBackground(bgColor);

        JPanel rangoTop = new JPanel(new FlowLayout());
        rangoTop.setBackground(bgColor);
        rangoTop.add(crearLabel("Buscar:"));
        rangoTop.add(txtBuscarRangoTerm);
        rangoTop.add(crearLabel("Min $"));
        rangoTop.add(txtMinPrice);
        rangoTop.add(crearLabel("Max $"));
        rangoTop.add(txtMaxPrice);
        rangoTop.add(btnBuscarRango);

        pnlRango.add(rangoTop, BorderLayout.NORTH);

        JScrollPane spRango = new JScrollPane(tablaRango);
        aumentarScrollbars(spRango);
        pnlRango.add(spRango, BorderLayout.CENTER);

        // TABS
        tabs.addTab("Scraping", pnlScrap);
        tabs.addTab("Productos", pnlProductos);
        tabs.addTab("AVL (inorder)", pnlAVL);
        tabs.addTab("Heap (Top N)", pnlHeap);
        tabs.addTab("BST (Rango)", pnlRango);

        tabs.setPreferredSize(new Dimension(1100, 700));

        getContentPane().add(tabs, BorderLayout.CENTER);

        // LOGS
        JPanel bottom = new JPanel(new BorderLayout());
        bottom.setBackground(bgColor);
        JLabel lblLogs = new JLabel("Logs:");
        lblLogs.setFont(FONT_LABEL);
        bottom.add(lblLogs, BorderLayout.NORTH);

        JScrollPane spLog = new JScrollPane(txtLog);
        aumentarScrollbars(spLog);
        bottom.add(spLog, BorderLayout.CENTER);
        bottom.setPreferredSize(new Dimension(getWidth(), 180));

        getContentPane().add(bottom, BorderLayout.SOUTH);
    }

    // ==============================
    // LISTENERS
    // ==============================
    private void attachListeners() {
        btnScrap.addActionListener(e -> iniciarScrapingDesdeGUI());

        btnCancelarScrap.addActionListener(e -> {
            if (worker != null && !worker.isDone()) {
                worker.cancel(true);
                appendLog("Scraping cancelado.");
                btnScrap.setEnabled(true);
                btnCancelarScrap.setEnabled(false);
            }
        });

        btnRecargar.addActionListener(e -> {
            cargarHistorialEnTabla();
            actualizarEstadisticas();
        });

        btnLimpiarHistorial.addActionListener(e -> {
            int r = JOptionPane.showConfirmDialog(this, "¿Limpiar historial?", "Confirmar",
                    JOptionPane.YES_NO_OPTION);
            if (r == JOptionPane.YES_OPTION) {
                manager.limpiarHistorial();
                cargarHistorialEnTabla();
                actualizarEstadisticas();
            }
        });

        tabs.addChangeListener(e -> {
            if (tabs.getSelectedIndex() == 2) {
                mostrarAVL();
            }
        });

        btnMostrarTop.addActionListener(e -> {
            try {
                mostrarTopN(Integer.parseInt(txtTopN.getText().trim()));
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "N inválido");
            }
        });

        btnBuscarRango.addActionListener(e -> {
            try {
                buscarPorRango(Double.parseDouble(txtMinPrice.getText()),
                        Double.parseDouble(txtMaxPrice.getText()));
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Valores inválidos");
            }
        });
    }

    // ==============================
    // FUNCIONES PRINCIPALES
    // ==============================

    private void iniciarScrapingDesdeGUI() {
        String producto = txtProducto.getText().trim();
        if (producto.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Ingrese producto");
            return;
        }

        int tienda = cmbTienda.getSelectedIndex() + 1;
        int items = (int) spnItems.getValue();
        int paginas = (int) spnPaginas.getValue();
        boolean reporte = chkReporte.isSelected();

        btnScrap.setEnabled(false);
        btnCancelarScrap.setEnabled(true);

        String termino = normalizarTexto(producto);

        worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() throws Exception {
                manager.aggDatosHistorial(tienda, termino, items, paginas, reporte);
                publish("Scraping completado.");
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
                cargarHistorialEnTabla();
                actualizarEstadisticas();
            }
        };

        worker.execute();
    }
    private void cargarHistorialEnTabla() {
        tableModel.setRowCount(0);
        ArrayList<Producto> productos = manager.getHistorialCompleto();
        int i = 1;
        for (Producto p : productos) {
            tableModel.addRow(new Object[]{
                    i++, p.getTitulo(), p.getPrecioVenta(), p.getTienda(), p.getUrl()
            });
        }
    }

    private void actualizarEstadisticas() {
        lblTotal.setText("Total: " + manager.getTotalProductos());
        lblML.setText("MercadoLibre: " + manager.getProductosPorTienda("MercadoLibre").size());
        lblAlk.setText("Alkosto: " + manager.getProductosPorTienda("Alkosto").size());
    }

    private void mostrarAVL() {
        txtAVL.setText("");

        try {
            java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();
            PrintStream ps = new PrintStream(baos);
            PrintStream old = System.out;

            System.setOut(ps);
            manager.getAVL().inorder();
            System.out.flush();
            System.setOut(old);

            txtAVL.setText(baos.toString());

        } catch (Exception ex) {
            txtAVL.setText("Error mostrando AVL.");
        }
    }

    private void mostrarTopN(int n) {
        heapModel.setRowCount(0);

        String termino = normalizarTexto(txtBuscarHeap.getText().trim());
        ArrayList<Producto> filtrados =
                termino.isEmpty() ?
                        manager.getHistorialCompleto() :
                        manager.getAVL().buscarPorTermino(termino);

        if (filtrados.isEmpty()) {
            appendLog("No se encontraron productos para el término: " + termino);
            return;
        }

        Heap temp = new Heap();
        for (Producto p : filtrados) temp.insert(p);

        List<Producto> top = temp.getNMasBaratos(n);

        if (top.isEmpty()) {
            appendLog("No hay productos dentro del Top " + n);
            return;
        }

        for (Producto p : top) {
            heapModel.addRow(new Object[]{p.getTitulo(), p.getPrecioVenta(), p.getTienda()});
        }

        appendLog("Se mostraron " + top.size() + " productos en el Top " + n);
    }

    private void buscarPorRango(double min, double max) {
        rangoModel.setRowCount(0);

        String termino = normalizarTexto(txtBuscarRangoTerm.getText().trim());
        ArrayList<Producto> filtrados =
                termino.isEmpty() ?
                        manager.getHistorialCompleto() :
                        manager.getAVL().buscarPorTermino(termino);

        if (filtrados.isEmpty()) {
            appendLog("No se encontraron productos para el término: " + termino);
            return;
        }

        BST bst = new BST(filtrados);
        ArrayList<Producto> res = bst.buscarEnRango(min, max);

        if (res.isEmpty()) {
            appendLog("No hay productos en el rango $" + min + " - $" + max);
            return;
        }

        for (Producto p : res) {
            rangoModel.addRow(new Object[]{p.getTitulo(), p.getPrecioVenta(), p.getTienda()});
        }

        appendLog("Se mostraron " + res.size() + " productos en el rango $" + min + " - $" + max);
    }

    // =====================================
    // VENTANA DE BIENVENIDA + MÚSICA
    // =====================================

    private void showWelcomeDialog() {
        JDialog dlg = new JDialog(this, true);
        dlg.setUndecorated(true);
        dlg.setSize(600, 380);
        dlg.setLocationRelativeTo(this);

        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(bgColor);
        panel.setBorder(new EmptyBorder(40, 40, 40, 40));

        JLabel title = new JLabel("¡Bienvenido a SC Data Extractor!");
        title.setFont(new Font("Segoe UI", Font.BOLD, 28));
        title.setHorizontalAlignment(SwingConstants.CENTER);

        JLabel subtitle = new JLabel("Tu dashboard inteligente de scraping");
        subtitle.setFont(new Font("Segoe UI", Font.PLAIN, 22));
        subtitle.setHorizontalAlignment(SwingConstants.CENTER);
        subtitle.setBorder(new EmptyBorder(20, 0, 30, 0));

        JButton btnStart = new JButton("Iniciar");
        btnStart.setFont(new Font("Segoe UI", Font.PLAIN, 20));
        btnStart.setPreferredSize(new Dimension(160, 50));
        btnStart.addActionListener(e -> dlg.dispose());

        JButton btnMute = new JButton("off");
        btnMute.setFont(new Font("Segoe UI", Font.PLAIN, 22));
        btnMute.setPreferredSize(new Dimension(45, 45));
        btnMute.addActionListener(e -> {
            isMuted = !isMuted;
            if (isMuted) {
                if (backgroundClip != null) backgroundClip.stop();
                btnMute.setText("on");
            } else {
                if (backgroundClip != null) backgroundClip.start();
                btnMute.setText("off");
            }
        });

        JPanel top = new JPanel(new BorderLayout());
        top.setBackground(bgColor);
        top.add(title, BorderLayout.CENTER);
        top.add(btnMute, BorderLayout.EAST);

        JPanel bottom = new JPanel();
        bottom.setBackground(bgColor);
        bottom.add(btnStart);

        panel.add(top, BorderLayout.NORTH);
        panel.add(subtitle, BorderLayout.CENTER);
        panel.add(bottom, BorderLayout.SOUTH);

        dlg.setContentPane(panel);
        dlg.setVisible(true);
    }

    private void playBackgroundMusic(String path) {
        new Thread(() -> {
            try {
                File file = new File(path);
                if (!file.exists()) return;

                AudioInputStream stream = AudioSystem.getAudioInputStream(file);
                backgroundClip = AudioSystem.getClip();
                backgroundClip.open(stream);
                backgroundClip.loop(Clip.LOOP_CONTINUOUSLY);
                backgroundClip.start();
            } catch (Exception ignored) {}
        }).start();
    }

    // =============================
    // UTILIDADES
    // =============================

    private JLabel crearLabel(String t) {
        JLabel lbl = new JLabel(t);
        lbl.setFont(FONT_LABEL);
        return lbl;
    }

    private void aumentarScrollbars(JScrollPane sp) {
        sp.getVerticalScrollBar().setPreferredSize(new Dimension(18, 0));
        sp.getHorizontalScrollBar().setPreferredSize(new Dimension(0, 18));
    }

    private void appendLog(String msg) {
        txtLog.append(msg + "\n");
        txtLog.setCaretPosition(txtLog.getDocument().getLength());
    }

    private static String normalizarTexto(String t) {
        if (t == null) return "";
        return Normalizer.normalize(t, Normalizer.Form.NFD)
                .replaceAll("[^\\p{ASCII}]", "")
                .toLowerCase();
    }

    // =====================================
    // TEMA ESCALA DE GRISES GENERAL
    // =====================================
    private static void aplicarTemaGris() {
        Color bg = new Color(240, 240, 240);
        Color mid = new Color(210, 210, 210);
        Color dark = new Color(100, 100, 100);

        UIManager.put("Panel.background", bg);
        UIManager.put("OptionPane.background", bg);

        UIManager.put("Button.background", mid);
        UIManager.put("Button.foreground", Color.BLACK);
        UIManager.put("Button.border", BorderFactory.createLineBorder(dark, 2));

        UIManager.put("TabbedPane.background", mid);
        UIManager.put("TabbedPane.selected", bg);
        UIManager.put("TabbedPane.borderHightlightColor", dark);

        UIManager.put("ComboBox.background", mid);
        UIManager.put("ComboBox.border", BorderFactory.createLineBorder(dark, 2));

        UIManager.put("Table.background", bg);
        UIManager.put("TableHeader.background", mid);
        UIManager.put("TableHeader.font", new Font("Segoe UI", Font.BOLD, 16));
        UIManager.put("Table.gridColor", mid);

        UIManager.put("ScrollBar.thumb", dark);
        UIManager.put("ScrollBar.track", mid);

        UIManager.put("TextField.border", BorderFactory.createLineBorder(dark, 2));
    }

    // =====================================
    // MAIN
    // =====================================
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new MainWindowDashboard().setVisible(true));
    }
}