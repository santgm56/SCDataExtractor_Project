import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.JTableHeader;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.border.EmptyBorder;
import javax.swing.border.AbstractBorder;
import java.awt.*;
import java.awt.event.*;
import java.awt.geom.RoundRectangle2D;
import java.io.PrintStream;
import java.io.File;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.List;
import javax.sound.sampled.*;

public class MainWindowDashboard extends JFrame {

    static {
        aplicarTemaAzulClaro();
    }

    private final Font FONT_TITLE = new Font("Segoe UI", Font.BOLD, 26);
    private final Font FONT_SUBTITLE = new Font("Segoe UI", Font.PLAIN, 18);
    private final Font FONT_LABEL = new Font("Segoe UI", Font.BOLD, 18);
    private final Font FONT_BUTTON = new Font("Segoe UI", Font.BOLD, 18);
    private final Font FONT_INPUT = new Font("Segoe UI", Font.PLAIN, 17);
    private final Font FONT_TABLE = new Font("Segoe UI", Font.PLAIN, 16);
    private final Font FONT_TABLE_HEADER = new Font("Segoe UI", Font.BOLD, 16);


    private final Color PRIMARY = new Color(0, 120, 212);
    private final Color PRIMARY_LIGHT = new Color(232, 241, 251);
    private final Color BG = new Color(247, 249, 252);
    private final Color PANEL = Color.WHITE;
    private final Color BORDER = new Color(227, 231, 239);
    private final Color TEXT = new Color(31, 41, 51);
    private final Color MUTED = new Color(98, 112, 127);

    private final Color bgColor = BG;
    private final Color panelColor = PANEL;
    private final Color bgTable = PRIMARY_LIGHT;
    private final Color INPUT_BG = new Color(240, 242, 245); // Fondo gris claro para inputs

    private DataManager manager;

    // Nueva navegación con CardLayout
    private CardLayout cardLayout;
    private JPanel contentPanel;
    private JButton[] navButtons;
    private int currentNavIndex = 0;
    
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

    private JTable tablaAVL;
    private DefaultTableModel avlModel;

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

    public MainWindowDashboard() {
        super("SC Data Extractor - Dashboard");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1050, 700);
        setMinimumSize(new Dimension(900, 600));
        setLocationRelativeTo(null);

        Image logo = cargarLogo();
        if (logo != null) {
            setIconImage(logo);
        }

        getContentPane().setBackground(BG);

        manager = new DataManager();

        initComponents();
        layoutComponents();
        attachListeners();

        playBackgroundMusic("../resources/background.wav");
        showWelcomeDialog();

        cargarHistorialEnTabla();
        actualizarEstadisticas();
    }

    private void initComponents() {
        
        // CardLayout para cambiar entre vistas
        cardLayout = new CardLayout();
        contentPanel = new JPanel(cardLayout);
        contentPanel.setBackground(BG);

        txtLog = new JTextArea();
        txtLog.setEditable(false);
        txtLog.setLineWrap(true);
        txtLog.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        txtLog.setBackground(new Color(250, 250, 250));

        // Scraping - inputs estilizados
        cmbTienda = new JComboBox<>(new String[]{"MercadoLibre", "Alkosto"});
        estilizarComboBox(cmbTienda);

        txtProducto = new JTextField(25);
        estilizarInputModerno(txtProducto);

        spnItems = new JSpinner(new SpinnerNumberModel(10, 1, 200, 1));
        estilizarSpinner(spnItems);

        spnPaginas = new JSpinner(new SpinnerNumberModel(1, 1, 50, 1));
        estilizarSpinner(spnPaginas);

        chkReporte = new JCheckBox("Generar reporte");
        chkReporte.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        chkReporte.setOpaque(false);
        chkReporte.setForeground(TEXT);
        chkReporte.setCursor(new Cursor(Cursor.HAND_CURSOR));

        btnScrap = crearBotonPrincipal("Ejecutar Scraping");
        btnCancelarScrap = crearBotonSecundario("Cancelar");
        btnCancelarScrap.setEnabled(false);

        // Tabla Productos
        tableModel = new DefaultTableModel(new String[]{"ID", "Nombre", "Precio", "Tienda", "URL"}, 0);
        tablaResultados = new JTable(tableModel);
        estilizarTablaModerna(tablaResultados);

        btnRecargar = crearBotonPrincipal("Recargar Productos");
        btnLimpiarHistorial = crearBotonSecundario("Limpiar Historial");

        lblTotal = new JLabel("Total: 0");
        lblML = new JLabel("MercadoLibre: 0");
        lblAlk = new JLabel("Alkosto: 0");
        
        for (JLabel lbl : new JLabel[]{lblTotal, lblML, lblAlk}) {
            lbl.setFont(new Font("Segoe UI", Font.BOLD, 14));
            lbl.setForeground(TEXT);
        }

        // Tabla AVL
        avlModel = new DefaultTableModel(new String[]{"#", "Nombre", "Precio", "Tienda"}, 0);
        tablaAVL = new JTable(avlModel);
        estilizarTablaModerna(tablaAVL);

        // Heap
        txtTopN = new JTextField("5", 6);
        estilizarInputModerno(txtTopN);

        btnMostrarTop = crearBotonPrincipal("Mostrar Top N");

        txtBuscarHeap = new JTextField(20);
        estilizarInputModerno(txtBuscarHeap);

        heapModel = new DefaultTableModel(new String[]{"Nombre", "Precio", "Tienda"}, 0);
        tablaHeap = new JTable(heapModel);
        estilizarTablaModerna(tablaHeap);

        // Rango (BST)
        txtBuscarRangoTerm = new JTextField(20);
        estilizarInputModerno(txtBuscarRangoTerm);

        txtMinPrice = new JTextField("0", 10);
        estilizarInputModerno(txtMinPrice);

        txtMaxPrice = new JTextField("1000000", 10);
        estilizarInputModerno(txtMaxPrice);

        btnBuscarRango = crearBotonPrincipal("Buscar Rango");

        rangoModel = new DefaultTableModel(new String[]{"Nombre", "Precio", "Tienda"}, 0);
        tablaRango = new JTable(rangoModel);
        estilizarTablaModerna(tablaRango);
    }

    private void layoutComponents() {
        setLayout(new BorderLayout());
        
        // =============================================
        // BARRA DE NAVEGACIÓN SUPERIOR
        // =============================================
        JPanel navBar = crearBarraNavegacion();
        add(navBar, BorderLayout.NORTH);
        
        // =============================================
        // PANEL DE CONTENIDO CON CARDLAYOUT
        // =============================================
        contentPanel.setBorder(new EmptyBorder(20, 40, 20, 40));
        
        // Vista 1: Scraping (tarjeta centrada)
        contentPanel.add(crearVistaScrapingModerna(), "scraping");
        
        // Vista 2: Productos
        contentPanel.add(crearVistaProductos(), "productos");
        
        // Vista 3: AVL
        contentPanel.add(crearVistaAVL(), "avl");
        
        // Vista 4: Heap
        contentPanel.add(crearVistaHeap(), "heap");
        
        // Vista 5: BST Rango
        contentPanel.add(crearVistaBST(), "bst");
        
        add(contentPanel, BorderLayout.CENTER);
        
        // =============================================
        // PANEL DE LOGS (inferior, compacto con padding)
        // =============================================
        JPanel logPanel = new JPanel(new BorderLayout());
        logPanel.setBackground(Color.WHITE);
        logPanel.setBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, BORDER));
        
        JLabel lblLogs = new JLabel("Logs");
        lblLogs.setFont(new Font("Segoe UI", Font.BOLD, 11));
        lblLogs.setForeground(MUTED);
        lblLogs.setBorder(new EmptyBorder(6, 20, 6, 20));
        logPanel.add(lblLogs, BorderLayout.NORTH);
        
        // Agregar padding al área de logs
        txtLog.setBorder(new EmptyBorder(5, 20, 10, 20));
        txtLog.setMargin(new Insets(5, 20, 10, 20));
        
        JScrollPane spLog = new JScrollPane(txtLog);
        spLog.setBorder(BorderFactory.createEmptyBorder());
        spLog.setPreferredSize(new Dimension(getWidth(), 80));
        logPanel.add(spLog, BorderLayout.CENTER);
        
        add(logPanel, BorderLayout.SOUTH);
        
        // Mostrar la primera vista
        cardLayout.show(contentPanel, "scraping");
        actualizarEstadoNavegacion(0);
    }
    
    // =============================================
    // BARRA DE NAVEGACIÓN MODERNA
    // =============================================
    private JPanel crearBarraNavegacion() {
        JPanel navBar = new JPanel(new BorderLayout());
        navBar.setBackground(Color.WHITE);
        navBar.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, BORDER));
        navBar.setPreferredSize(new Dimension(getWidth(), 55));
        
        // Logo y título a la izquierda
        JPanel leftPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 10));
        leftPanel.setOpaque(false);
        
        JLabel logoLabel = new JLabel();
        try {
            File logoFile = new File("../resources/logo.png");
            if (logoFile.exists()) {
                Image img = new ImageIcon(logoFile.getAbsolutePath()).getImage();
                Image scaled = img.getScaledInstance(45, 45, Image.SCALE_SMOOTH);
                logoLabel.setIcon(new ImageIcon(scaled));
            }
        } catch (Exception ignored) {}
        
        JLabel titleLabel = new JLabel("SCData Extractor");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 20));
        titleLabel.setForeground(PRIMARY);
        
        leftPanel.add(logoLabel);
        leftPanel.add(titleLabel);
        navBar.add(leftPanel, BorderLayout.WEST);
        
        // Botones de navegación en el centro
        JPanel navButtonsPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 5, 10));
        navButtonsPanel.setOpaque(false);
        
        String[] labels = {"Scraping", "Productos", "AVL", "Heap", "BST"};
        String[] cards = {"scraping", "productos", "avl", "heap", "bst"};
        navButtons = new JButton[labels.length];
        
        for (int i = 0; i < labels.length; i++) {
            final int index = i;
            final String cardName = cards[i];
            
            navButtons[i] = crearBotonNavegacion(labels[i]);
            navButtons[i].addActionListener(e -> {
                cardLayout.show(contentPanel, cardName);
                actualizarEstadoNavegacion(index);
                
                // Actualizar AVL cuando se selecciona
                if (index == 2) mostrarAVL();
            });
            navButtonsPanel.add(navButtons[i]);
        }
        
        navBar.add(navButtonsPanel, BorderLayout.CENTER);
        
        return navBar;
    }
    
    private JButton crearBotonNavegacion(String texto) {
        JButton btn = new JButton(texto);
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        btn.setForeground(MUTED);
        btn.setBackground(Color.WHITE);
        btn.setBorder(new EmptyBorder(12, 20, 12, 20));
        btn.setFocusPainted(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setOpaque(true);
        
        btn.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                if (!btn.getForeground().equals(PRIMARY)) {
                    btn.setBackground(PRIMARY_LIGHT);
                }
            }
            @Override
            public void mouseExited(MouseEvent e) {
                if (!btn.getForeground().equals(PRIMARY)) {
                    btn.setBackground(Color.WHITE);
                }
            }
        });
        
        return btn;
    }
    
    private void actualizarEstadoNavegacion(int selectedIndex) {
        currentNavIndex = selectedIndex;
        for (int i = 0; i < navButtons.length; i++) {
            if (i == selectedIndex) {
                navButtons[i].setForeground(PRIMARY);
                navButtons[i].setFont(new Font("Segoe UI", Font.BOLD, 14));
                navButtons[i].setBackground(PRIMARY_LIGHT);
            } else {
                navButtons[i].setForeground(MUTED);
                navButtons[i].setFont(new Font("Segoe UI", Font.PLAIN, 14));
                navButtons[i].setBackground(Color.WHITE);
            }
        }
    }
    
    // =============================================
    // VISTA SCRAPING - TARJETA CENTRADA
    // =============================================
    private JPanel crearVistaScrapingModerna() {
        JPanel wrapper = new JPanel(new GridBagLayout());
        wrapper.setBackground(BG);
        
        // Tarjeta central con bordes redondeados
        JPanel card = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setColor(getBackground());
                g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), 20, 20));
                g2.setColor(BORDER);
                g2.draw(new RoundRectangle2D.Float(0, 0, getWidth()-1, getHeight()-1, 20, 20));
                g2.dispose();
            }
        };
        card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
        card.setBackground(Color.WHITE);
        card.setBorder(new EmptyBorder(40, 50, 40, 50));
        card.setOpaque(false);
        card.setPreferredSize(new Dimension(550, 530));
        card.setMaximumSize(new Dimension(550, 530));
        
        // Título de la tarjeta
        JLabel titulo = new JLabel("Búsqueda de Productos");
        titulo.setFont(new Font("Segoe UI", Font.BOLD, 24));
        titulo.setForeground(TEXT);
        titulo.setAlignmentX(Component.CENTER_ALIGNMENT);
        card.add(titulo);
        card.add(Box.createRigidArea(new Dimension(0, 14)));
        
        JLabel subtitulo = new JLabel("Configura los parámetros de scraping");
        subtitulo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        subtitulo.setForeground(MUTED);
        subtitulo.setAlignmentX(Component.CENTER_ALIGNMENT);
        card.add(subtitulo);
        card.add(Box.createRigidArea(new Dimension(0, 4)));
        
        // Campo: Tienda
        card.add(crearCampoFormulario("Tienda", cmbTienda));
        card.add(Box.createRigidArea(new Dimension(0, 14)));
        
        // Campo: Producto
        card.add(crearCampoFormulario("Producto a buscar", txtProducto));
        card.add(Box.createRigidArea(new Dimension(0, 4)));
        
        // Fila: Items y Páginas
        JPanel filaNumeros = new JPanel(new GridLayout(1, 2, 20, 0));
        filaNumeros.setOpaque(false);
        filaNumeros.setMaximumSize(new Dimension(450, 70));
        filaNumeros.add(crearCampoFormularioCompacto("Items", spnItems));
        filaNumeros.add(crearCampoFormularioCompacto("Páginas", spnPaginas));
        card.add(filaNumeros);
        card.add(Box.createRigidArea(new Dimension(0, 4)));
        
        // Checkbox
        JPanel checkPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 0));
        checkPanel.setOpaque(false);
        checkPanel.setMaximumSize(new Dimension(450, 30));
        checkPanel.add(chkReporte);
        card.add(checkPanel);
        card.add(Box.createRigidArea(new Dimension(0, 20)));
        
        // Botones
        JPanel botonesPanel = new JPanel(new GridLayout(1, 2, 15, 0));
        botonesPanel.setOpaque(false);
        botonesPanel.setMaximumSize(new Dimension(450, 48));
        
        btnScrap.setPreferredSize(new Dimension(200, 48));
        btnCancelarScrap.setPreferredSize(new Dimension(200, 48));
        
        botonesPanel.add(btnScrap);
        botonesPanel.add(btnCancelarScrap);
        card.add(botonesPanel);
        
        wrapper.add(card);
        return wrapper;
    }
    
    private JPanel crearCampoFormulario(String label, JComponent input) {
        JPanel campo = new JPanel();
        campo.setLayout(new BoxLayout(campo, BoxLayout.Y_AXIS));
        campo.setOpaque(false);
        campo.setMaximumSize(new Dimension(450, 65));
        campo.setAlignmentX(Component.CENTER_ALIGNMENT);
        
        JLabel lbl = new JLabel(label);
        lbl.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        lbl.setForeground(MUTED);
        lbl.setAlignmentX(Component.LEFT_ALIGNMENT);
        campo.add(lbl);
        campo.add(Box.createRigidArea(new Dimension(0, 6)));
        
        input.setMaximumSize(new Dimension(450, 38));
        input.setAlignmentX(Component.LEFT_ALIGNMENT);
        campo.add(input);
        
        return campo;
    }
    
    private JPanel crearCampoFormularioCompacto(String label, JComponent input) {
        JPanel campo = new JPanel();
        campo.setLayout(new BoxLayout(campo, BoxLayout.Y_AXIS));
        campo.setOpaque(false);
        
        JLabel lbl = new JLabel(label);
        lbl.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        lbl.setForeground(MUTED);
        lbl.setAlignmentX(Component.LEFT_ALIGNMENT);
        campo.add(lbl);
        campo.add(Box.createRigidArea(new Dimension(0, 6)));
        
        input.setMaximumSize(new Dimension(Integer.MAX_VALUE, 42));
        input.setAlignmentX(Component.LEFT_ALIGNMENT);
        campo.add(input);
        
        return campo;
    }
    
    // =============================================
    // VISTA PRODUCTOS
    // =============================================
    private JPanel crearVistaProductos() {
        JPanel panel = new JPanel(new BorderLayout(0, 15));
        panel.setBackground(BG);
        
        // Header con botones y estadísticas
        JPanel header = new JPanel(new BorderLayout());
        header.setOpaque(false);
        
        JPanel botonesHeader = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        botonesHeader.setOpaque(false);
        btnRecargar.setPreferredSize(new Dimension(180, 40));
        btnLimpiarHistorial.setPreferredSize(new Dimension(160, 40));
        botonesHeader.add(btnRecargar);
        botonesHeader.add(btnLimpiarHistorial);
        header.add(botonesHeader, BorderLayout.WEST);
        
        JPanel statsPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 20, 5));
        statsPanel.setOpaque(false);
        statsPanel.add(lblTotal);
        statsPanel.add(lblML);
        statsPanel.add(lblAlk);
        header.add(statsPanel, BorderLayout.EAST);
        
        panel.add(header, BorderLayout.NORTH);
        
        // Tabla en tarjeta
        JPanel tableCard = crearTarjetaTabla(tablaResultados);
        panel.add(tableCard, BorderLayout.CENTER);
        
        return panel;
    }
    
    // =============================================
    // VISTA AVL
    // =============================================
    private JPanel crearVistaAVL() {
        JPanel panel = new JPanel(new BorderLayout(0, 15));
        panel.setBackground(BG);
        
        // Header
        JPanel header = new JPanel(new BorderLayout());
        header.setOpaque(false);
        
        JLabel titulo = new JLabel("AVL Tree - Productos Ordenados Alfabéticamente");
        titulo.setFont(new Font("Segoe UI", Font.BOLD, 20));
        titulo.setForeground(PRIMARY);
        header.add(titulo, BorderLayout.WEST);
        
        JButton btnRefresh = crearBotonSecundario("Actualizar");
        btnRefresh.addActionListener(e -> mostrarAVL());
        header.add(btnRefresh, BorderLayout.EAST);
        
        panel.add(header, BorderLayout.NORTH);
        
        // Tabla
        panel.add(crearTarjetaTabla(tablaAVL), BorderLayout.CENTER);
        
        // Info
        JLabel info = new JLabel("Los productos se muestran en orden alfabético usando recorrido inorder del árbol AVL");
        info.setFont(new Font("Segoe UI", Font.ITALIC, 12));
        info.setForeground(MUTED);
        panel.add(info, BorderLayout.SOUTH);
        
        return panel;
    }
    
    // =============================================
    // VISTA HEAP
    // =============================================
    private JPanel crearVistaHeap() {
        JPanel panel = new JPanel(new BorderLayout(0, 15));
        panel.setBackground(BG);
        
        // Header
        JLabel titulo = new JLabel("Heap - Top N Productos Más Baratos");
        titulo.setFont(new Font("Segoe UI", Font.BOLD, 20));
        titulo.setForeground(PRIMARY);
        panel.add(titulo, BorderLayout.NORTH);
        
        // Controles en tarjeta
        JPanel controlsCard = new JPanel();
        controlsCard.setLayout(new FlowLayout(FlowLayout.LEFT, 15, 10));
        controlsCard.setBackground(Color.WHITE);
        controlsCard.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(BORDER, 1),
            new EmptyBorder(15, 20, 15, 20)
        ));
        
        controlsCard.add(new JLabel("Buscar:"));
        txtBuscarHeap.setPreferredSize(new Dimension(200, 40));
        controlsCard.add(txtBuscarHeap);
        
        controlsCard.add(Box.createHorizontalStrut(20));
        controlsCard.add(new JLabel("Cantidad (N):"));
        txtTopN.setPreferredSize(new Dimension(80, 40));
        controlsCard.add(txtTopN);
        
        controlsCard.add(Box.createHorizontalStrut(20));
        JButton btnMostrar = crearBotonPrincipal("Mostrar Top N");
        btnMostrar.setPreferredSize(new Dimension(150, 40));
        btnMostrar.addActionListener(e -> {
            try {
                mostrarTopN(Integer.parseInt(txtTopN.getText().trim()));
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "N inválido");
            }
        });
        controlsCard.add(btnMostrar);
        
        JPanel centerPanel = new JPanel(new BorderLayout(0, 15));
        centerPanel.setOpaque(false);
        centerPanel.add(controlsCard, BorderLayout.NORTH);
        centerPanel.add(crearTarjetaTabla(tablaHeap), BorderLayout.CENTER);
        
        panel.add(centerPanel, BorderLayout.CENTER);
        
        return panel;
    }
    
    // =============================================
    // VISTA BST (RANGO)
    // =============================================
    private JPanel crearVistaBST() {
        JPanel panel = new JPanel(new BorderLayout(0, 15));
        panel.setBackground(BG);
        
        // Header
        JLabel titulo = new JLabel("BST - Búsqueda por Rango de Precios");
        titulo.setFont(new Font("Segoe UI", Font.BOLD, 20));
        titulo.setForeground(PRIMARY);
        panel.add(titulo, BorderLayout.NORTH);
        
        // Controles en tarjeta con mejor layout
        JPanel controlsCard = new JPanel();
        controlsCard.setLayout(new BoxLayout(controlsCard, BoxLayout.Y_AXIS));
        controlsCard.setBackground(Color.WHITE);
        controlsCard.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(BORDER, 1),
            new EmptyBorder(20, 25, 20, 25)
        ));
        
        // Primera fila: Buscar
        JPanel filaBuscar = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        filaBuscar.setOpaque(false);
        filaBuscar.setMaximumSize(new Dimension(Integer.MAX_VALUE, 45));
        
        JLabel lblBuscar = new JLabel("Buscar:");
        lblBuscar.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        lblBuscar.setForeground(TEXT);
        filaBuscar.add(lblBuscar);
        
        txtBuscarRangoTerm.setPreferredSize(new Dimension(300, 38));
        filaBuscar.add(txtBuscarRangoTerm);
        
        controlsCard.add(filaBuscar);
        controlsCard.add(Box.createRigidArea(new Dimension(0, 15)));
        
        // Segunda fila: Rango de precios y botón
        JPanel filaRango = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 0));
        filaRango.setOpaque(false);
        filaRango.setMaximumSize(new Dimension(Integer.MAX_VALUE, 45));
        
        JLabel lblMin = new JLabel("Precio mín $");
        lblMin.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        lblMin.setForeground(TEXT);
        filaRango.add(lblMin);
        
        txtMinPrice.setPreferredSize(new Dimension(120, 38));
        filaRango.add(txtMinPrice);
        
        JLabel lblMax = new JLabel("Precio máx $");
        lblMax.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        lblMax.setForeground(TEXT);
        filaRango.add(lblMax);
        
        txtMaxPrice.setPreferredSize(new Dimension(120, 38));
        filaRango.add(txtMaxPrice);
        
        filaRango.add(Box.createHorizontalStrut(10));
        
        JButton btnBuscar = crearBotonPrincipal("Buscar");
        btnBuscar.setPreferredSize(new Dimension(140, 38));
        btnBuscar.addActionListener(e -> {
            try {
                buscarPorRango(Double.parseDouble(txtMinPrice.getText()),
                        Double.parseDouble(txtMaxPrice.getText()));
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Valores inválidos");
            }
        });
        filaRango.add(btnBuscar);
        
        controlsCard.add(filaRango);
        
        JPanel centerPanel = new JPanel(new BorderLayout(0, 15));
        centerPanel.setOpaque(false);
        centerPanel.add(controlsCard, BorderLayout.NORTH);
        centerPanel.add(crearTarjetaTabla(tablaRango), BorderLayout.CENTER);
        
        panel.add(centerPanel, BorderLayout.CENTER);
        
        return panel;
    }
    
    // =============================================
    // TARJETA PARA TABLAS
    // =============================================
    private JPanel crearTarjetaTabla(JTable tabla) {
        JPanel card = new JPanel(new BorderLayout());
        card.setBackground(Color.WHITE);
        card.setBorder(BorderFactory.createLineBorder(BORDER, 1));
        
        JScrollPane scroll = new JScrollPane(tabla);
        scroll.setBorder(BorderFactory.createEmptyBorder());
        scroll.getViewport().setBackground(Color.WHITE);
        
        card.add(scroll, BorderLayout.CENTER);
        return card;
    }

    private void attachListeners() {
        btnScrap.addActionListener(e -> iniciarScrapingDesdeGUI());

        btnCancelarScrap.addActionListener(e -> {
            if (worker != null && !worker.isDone()) {
                RunPython.cancelarScraping();
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

        // Los listeners de navegación ya están en los botones de nav

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
                try {
                    manager.aggDatosHistorial(tienda, termino, items, paginas, reporte);
                    if (!isCancelled()) {
                        publish("Scraping completado.");
                    }
                } catch (InterruptedException ie) {
                    publish("Scraping cancelado por usuario.");
                    Thread.currentThread().interrupt();
                } catch (Exception ex) {
                    publish("Error en scraping: " + ex.getMessage());
                }
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
                if (isCancelled()) {
                    appendLog("Scraping cancelado.");
                    return;
                }
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
        avlModel.setRowCount(0);

        try {
            // Obtener productos en orden desde el AVL
            AVLTree avl = manager.getAVL();
            ArrayList<Producto> ordenados = avl.getInorderList();
            
            int i = 1;
            for (Producto p : ordenados) {
                avlModel.addRow(new Object[]{
                    i++, 
                    p.getTitulo(), 
                    p.getPrecioVenta(),  // Ya es String
                    p.getTienda()
                });
            }
            
            appendLog("AVL Tree actualizado: " + ordenados.size() + " productos en orden alfabético.");

        } catch (Exception ex) {
            appendLog("Error mostrando AVL: " + ex.getMessage());
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

    private void showWelcomeDialog() {
        JDialog dlg = new JDialog(this, true);
        dlg.setUndecorated(true);
        dlg.setSize(500, 520);
        dlg.setLocationRelativeTo(this);
        
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(Color.WHITE);
        mainPanel.setBorder(BorderFactory.createLineBorder(BORDER, 1));
        
        JPanel topBar = new JPanel(new FlowLayout(FlowLayout.RIGHT, 15, 10));
        topBar.setOpaque(false);
        
        JButton btnMute = crearBotonMuteModerno();
        btnMute.addActionListener(e -> {
            isMuted = !isMuted;
            if (isMuted) {
                if (backgroundClip != null) backgroundClip.stop();
                btnMute.setToolTipText("Activar sonido");
            } else {
                if (backgroundClip != null) backgroundClip.start();
                btnMute.setToolTipText("Silenciar");
            }
        });
        topBar.add(btnMute);
        
        JPanel centerContent = new JPanel();
        centerContent.setLayout(new BoxLayout(centerContent, BoxLayout.Y_AXIS));
        centerContent.setOpaque(false);
        centerContent.setBorder(new EmptyBorder(20, 50, 40, 50));
        
        JLabel logoLabel = crearLogoCircular();
        logoLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        centerContent.add(Box.createVerticalGlue());
        centerContent.add(logoLabel);
        centerContent.add(Box.createRigidArea(new Dimension(0, 25)));
        
        JLabel appName = new JLabel("SCData Extractor");
        appName.setFont(new Font("Segoe UI", Font.BOLD, 32));
        appName.setForeground(PRIMARY);
        appName.setAlignmentX(Component.CENTER_ALIGNMENT);
        centerContent.add(appName);
        centerContent.add(Box.createRigidArea(new Dimension(0, 35)));
        
        JLabel welcomeLabel = new JLabel("Bienvenido/a");
        welcomeLabel.setFont(new Font("Segoe UI", Font.PLAIN, 24));
        welcomeLabel.setForeground(TEXT);
        welcomeLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        centerContent.add(welcomeLabel);
        centerContent.add(Box.createRigidArea(new Dimension(0, 40)));

        JButton btnStart = crearBotonIniciarModerno(e -> dlg.dispose());
        btnStart.setAlignmentX(Component.CENTER_ALIGNMENT);
        centerContent.add(btnStart);
        
        centerContent.add(Box.createVerticalGlue());
        
        JPanel footer = new JPanel(new FlowLayout(FlowLayout.CENTER));
        footer.setOpaque(false);
        footer.setBorder(new EmptyBorder(0, 0, 25, 0));
        
        JLabel subtitle = new JLabel("Tu dashboard inteligente de scraping");
        subtitle.setFont(new Font("Segoe UI", Font.ITALIC, 14));
        subtitle.setForeground(MUTED);
        footer.add(subtitle);
        
        // Ensamblar
        mainPanel.add(topBar, BorderLayout.NORTH);
        mainPanel.add(centerContent, BorderLayout.CENTER);
        mainPanel.add(footer, BorderLayout.SOUTH);
        
        dlg.setContentPane(mainPanel);
        dlg.setVisible(true);
    }
    
    private JLabel crearLogoCircular() {
        try {
            File logoFile = new File("../resources/logo.png");
            if (logoFile.exists()) {
                Image img = new ImageIcon(logoFile.getAbsolutePath()).getImage();
                Image scaled = img.getScaledInstance(100, 100, Image.SCALE_SMOOTH);
                return new JLabel(new ImageIcon(scaled));
            }
        } catch (Exception ignored) {}
        
        // Fallback: solo texto si no hay imagen
        JLabel fallback = new JLabel("📦");
        fallback.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 60));
        fallback.setPreferredSize(new Dimension(110, 110));
        fallback.setHorizontalAlignment(SwingConstants.CENTER);
        return fallback;
    }

    private JButton crearBotonIniciarModerno(ActionListener action) {
        JButton btn = new JButton() {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                
                GradientPaint gradient = new GradientPaint(
                    0, 0, new Color(0, 130, 220),
                    0, getHeight(), new Color(0, 100, 200)
                );
                g2.setPaint(gradient);
                g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), 20, 20));

                if (getModel().isRollover()) {
                    g2.setColor(new Color(255, 255, 255, 30));
                    g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), 20, 20));
                }
                
                if (getModel().isPressed()) {
                    g2.setColor(new Color(0, 0, 0, 20));
                    g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), 20, 20));
                }
                
                g2.dispose();
                super.paintComponent(g);
            }
        };
        
        // Usar GridBagLayout para centrar verticalmente
        btn.setLayout(new GridBagLayout());
        btn.setOpaque(false);
        btn.setContentAreaFilled(false);
        btn.setBorderPainted(false);
        btn.setFocusPainted(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setPreferredSize(new Dimension(280, 55));
        
        // Panel interno para el contenido
        JPanel contenido = new JPanel(new FlowLayout(FlowLayout.CENTER, 10, 0));
        contenido.setOpaque(false);
        
        // Icono de lupa
        JLabel iconLabel = new JLabel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setColor(Color.WHITE);
                g2.setStroke(new BasicStroke(2.5f));
                
                // Lupa centrada
                g2.drawOval(2, 2, 14, 14);
                g2.drawLine(14, 14, 20, 20);
                
                g2.dispose();
            }
            
            @Override
            public Dimension getPreferredSize() {
                return new Dimension(24, 24);
            }
        };
        
        JLabel textLabel = new JLabel("Iniciar Búsqueda de Productos");
        textLabel.setFont(new Font("Segoe UI", Font.BOLD, 14));
        textLabel.setForeground(Color.WHITE);
        
        contenido.add(iconLabel);
        contenido.add(textLabel);
        
        btn.add(contenido);
        btn.addActionListener(action);
        
        return btn;
    }
    

    private JButton crearBotonMuteModerno() {
        JButton btn = new JButton();
        
        // Cargar icono de volumen desde archivo
        try {
            File iconFile = new File("../resources/iconos/volumen-reducido.png");
            if (iconFile.exists()) {
                Image img = new ImageIcon(iconFile.getAbsolutePath()).getImage();
                Image scaled = img.getScaledInstance(24, 24, Image.SCALE_SMOOTH);
                btn.setIcon(new ImageIcon(scaled));
            } else {
                btn.setText("🔊");
                btn.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 20));
            }
        } catch (Exception e) {
            btn.setText("🔊");
            btn.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 20));
        }
        
        btn.setPreferredSize(new Dimension(40, 40));
        btn.setOpaque(false);
        btn.setContentAreaFilled(false);
        btn.setBorderPainted(false);
        btn.setFocusPainted(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setToolTipText("Silenciar");
        
        return btn;
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

    private JLabel crearLabel(String t) {
        JLabel lbl = new JLabel(t);
        lbl.setFont(FONT_LABEL);
        return lbl;
    }
    
    private JLabel crearLabelEstilizado(String t) {
        JLabel lbl = new JLabel(t);
        lbl.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        lbl.setForeground(MUTED);
        return lbl;
    }
    
    // =============================================
    // MÉTODOS DE ESTILIZADO MODERNO
    // =============================================
    
    private void estilizarInputModerno(JTextField tf) {
        tf.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        tf.setBackground(Color.WHITE);
        tf.setForeground(TEXT);
        tf.setOpaque(true);
        tf.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(BORDER, 1),
            new EmptyBorder(8, 12, 8, 12)
        ));
        tf.setCaretColor(TEXT);
        
        tf.addFocusListener(new FocusAdapter() {
            @Override
            public void focusGained(FocusEvent e) {
                tf.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(PRIMARY, 2),
                    new EmptyBorder(7, 11, 7, 11)
                ));
            }
            @Override
            public void focusLost(FocusEvent e) {
                tf.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(BORDER, 1),
                    new EmptyBorder(8, 12, 8, 12)
                ));
            }
        });
    }
    
    private void estilizarComboBox(JComboBox<String> cb) {
        cb.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        cb.setBackground(Color.WHITE);
        cb.setForeground(TEXT);
        cb.setOpaque(true);
        cb.setBorder(BorderFactory.createLineBorder(BORDER, 1));
        cb.setFocusable(true);
        cb.setCursor(new Cursor(Cursor.HAND_CURSOR));
        cb.setPreferredSize(new Dimension(450, 38));
        
        // Usar UI por defecto para mejor compatibilidad
        cb.setUI(new javax.swing.plaf.basic.BasicComboBoxUI() {
            @Override
            protected JButton createArrowButton() {
                JButton button = new JButton();
                button.setText("▼");
                button.setFont(new Font("Segoe UI", Font.PLAIN, 10));
                button.setBorder(BorderFactory.createEmptyBorder(0, 5, 0, 10));
                button.setBackground(Color.WHITE);
                button.setForeground(MUTED);
                button.setFocusPainted(false);
                button.setContentAreaFilled(false);
                return button;
            }
        });
        
        // Estilizar el renderer para mejor visualización
        cb.setRenderer(new DefaultListCellRenderer() {
            @Override
            public Component getListCellRendererComponent(JList<?> list, Object value, 
                    int index, boolean isSelected, boolean cellHasFocus) {
                super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
                setBorder(new EmptyBorder(10, 12, 10, 12));
                setFont(new Font("Segoe UI", Font.PLAIN, 14));
                setForeground(TEXT);
                if (isSelected) {
                    setBackground(PRIMARY_LIGHT);
                } else {
                    setBackground(Color.WHITE);
                }
                return this;
            }
        });
    }
    
    private void estilizarSpinner(JSpinner sp) {
        sp.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        sp.setBorder(BorderFactory.createLineBorder(BORDER, 1));
        sp.setBackground(INPUT_BG);
        
        JComponent editor = sp.getEditor();
        if (editor instanceof JSpinner.DefaultEditor) {
            JTextField tf = ((JSpinner.DefaultEditor) editor).getTextField();
            tf.setBackground(INPUT_BG);
            tf.setHorizontalAlignment(JTextField.CENTER);
            tf.setBorder(new EmptyBorder(8, 10, 8, 10));
        }
        
        // Estilizar botones del spinner
        for (Component c : sp.getComponents()) {
            if (c instanceof JButton) {
                ((JButton) c).setBackground(INPUT_BG);
                ((JButton) c).setBorder(BorderFactory.createLineBorder(BORDER, 1));
            }
        }
    }
    
    private void estilizarTablaModerna(JTable tabla) {
        tabla.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        tabla.setRowHeight(40);
        tabla.setBackground(Color.WHITE);
        tabla.setShowGrid(false);
        tabla.setIntercellSpacing(new Dimension(0, 0));
        tabla.setSelectionBackground(PRIMARY_LIGHT);
        tabla.setSelectionForeground(TEXT);
        
        JTableHeader header = tabla.getTableHeader();
        header.setFont(new Font("Segoe UI", Font.BOLD, 13));
        header.setBackground(new Color(250, 251, 252));
        header.setForeground(TEXT);
        header.setBorder(BorderFactory.createMatteBorder(0, 0, 1, 0, BORDER));
        header.setPreferredSize(new Dimension(header.getPreferredSize().width, 45));
        
        tabla.setDefaultRenderer(Object.class, new DefaultTableCellRenderer() {
            @Override
            public Component getTableCellRendererComponent(JTable table, Object value,
                    boolean isSelected, boolean hasFocus, int row, int column) {
                Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
                if (!isSelected) {
                    c.setBackground(row % 2 == 0 ? Color.WHITE : new Color(250, 251, 252));
                }
                setBorder(new EmptyBorder(0, 15, 0, 15));
                return c;
            }
        });
    }
    
    private JButton crearBotonPrincipal(String texto) {
        JButton btn = new JButton(texto) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                
                Color bgColor;
                if (getModel().isPressed()) {
                    bgColor = PRIMARY.darker();
                } else if (getModel().isRollover()) {
                    bgColor = new Color(0, 100, 190);
                } else {
                    bgColor = PRIMARY;
                }
                
                g2.setColor(bgColor);
                g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), 12, 12));
                
                g2.setColor(Color.WHITE);
                g2.setFont(getFont());
                FontMetrics fm = g2.getFontMetrics();
                int x = (getWidth() - fm.stringWidth(getText())) / 2;
                int y = (getHeight() + fm.getAscent() - fm.getDescent()) / 2;
                g2.drawString(getText(), x, y);
                
                g2.dispose();
            }
        };
        
        btn.setFont(new Font("Segoe UI", Font.BOLD, 14));
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.setBorderPainted(false);
        btn.setContentAreaFilled(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setPreferredSize(new Dimension(180, 45));
        
        return btn;
    }
    
    private JButton crearBotonSecundario(String texto) {
        JButton btn = new JButton(texto) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                
                Color bgColor;
                if (getModel().isPressed()) {
                    bgColor = BORDER;
                } else if (getModel().isRollover()) {
                    bgColor = PRIMARY_LIGHT;
                } else {
                    bgColor = Color.WHITE;
                }
                
                g2.setColor(bgColor);
                g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), 12, 12));
                
                g2.setColor(BORDER);
                g2.draw(new RoundRectangle2D.Float(0, 0, getWidth()-1, getHeight()-1, 12, 12));
                
                g2.setColor(TEXT);
                g2.setFont(getFont());
                FontMetrics fm = g2.getFontMetrics();
                int x = (getWidth() - fm.stringWidth(getText())) / 2;
                int y = (getHeight() + fm.getAscent() - fm.getDescent()) / 2;
                g2.drawString(getText(), x, y);
                
                g2.dispose();
            }
        };
        
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        btn.setForeground(TEXT);
        btn.setFocusPainted(false);
        btn.setBorderPainted(false);
        btn.setContentAreaFilled(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setPreferredSize(new Dimension(150, 45));
        
        return btn;
    }

    private void aumentarScrollbars(JScrollPane sp) {
        sp.getVerticalScrollBar().setPreferredSize(new Dimension(18, 0));
        sp.getHorizontalScrollBar().setPreferredSize(new Dimension(0, 18));
    }

    private void estilizarScroll(JScrollPane sp) {
        sp.setBorder(BorderFactory.createEmptyBorder());
        sp.getVerticalScrollBar().setPreferredSize(new Dimension(10, 0));
        sp.getHorizontalScrollBar().setPreferredSize(new Dimension(0, 10));
        sp.getViewport().setBackground(Color.WHITE);
    }
    
    private void estilizarTextField(JTextField tf) {
        tf.setBorder(BorderFactory.createCompoundBorder(
            new RoundedBorder(8, BORDER),
            new EmptyBorder(8, 12, 8, 12)
        ));
        tf.setBackground(Color.WHITE);
    }
    
    private void estilizarTabla(JTable tabla) {
        JTableHeader header = tabla.getTableHeader();
        header.setBackground(PRIMARY);
        header.setForeground(Color.WHITE);
        header.setFont(FONT_TABLE_HEADER);
        header.setBorder(BorderFactory.createEmptyBorder());
        header.setPreferredSize(new Dimension(header.getPreferredSize().width, 40));
        
        // Renderizador para filas alternadas
        tabla.setDefaultRenderer(Object.class, new DefaultTableCellRenderer() {
            @Override
            public Component getTableCellRendererComponent(JTable table, Object value,
                    boolean isSelected, boolean hasFocus, int row, int column) {
                Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
                if (!isSelected) {
                    c.setBackground(row % 2 == 0 ? Color.WHITE : PRIMARY_LIGHT);
                }
                setBorder(new EmptyBorder(5, 10, 5, 10));
                return c;
            }
        });
    }

    private JPanel crearCardPanel() {
        JPanel card = new JPanel(new BorderLayout());
        card.setBackground(PANEL);
        card.setBorder(BorderFactory.createCompoundBorder(
                new RoundedBorder(12, BORDER),
                new EmptyBorder(15, 15, 15, 15)
        ));
        return card;
    }

    private void appendLog(String msg) {
        txtLog.append(msg + "\n");
        txtLog.setCaretPosition(txtLog.getDocument().getLength());
    }

    private JButton crearBotonRedondeado(String texto, boolean esPrimario) {
        return crearBotonRedondeado(texto, esPrimario, null);
    }
    
    private JButton crearBotonRedondeado(String texto, boolean esPrimario, ActionListener action) {
        JButton btn = new JButton(texto) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                
                if (getModel().isPressed()) {
                    g2.setColor(esPrimario ? PRIMARY.darker() : BORDER);
                } else if (getModel().isRollover()) {
                    g2.setColor(esPrimario ? PRIMARY.brighter() : PRIMARY_LIGHT);
                } else {
                    g2.setColor(esPrimario ? PRIMARY : PANEL);
                }
                
                g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), 20, 20));
                
                if (!esPrimario) {
                    g2.setColor(BORDER);
                    g2.draw(new RoundRectangle2D.Float(0, 0, getWidth()-1, getHeight()-1, 20, 20));
                }
                
                g2.setColor(esPrimario ? Color.WHITE : TEXT);
                g2.setFont(getFont());
                FontMetrics fm = g2.getFontMetrics();
                int x = (getWidth() - fm.stringWidth(getText())) / 2;
                int y = (getHeight() + fm.getAscent() - fm.getDescent()) / 2;
                g2.drawString(getText(), x, y);
                
                g2.dispose();
            }
            
            @Override
            protected void paintBorder(Graphics g) {
                // No pintar borde por defecto
            }
            
            @Override
            public boolean isContentAreaFilled() {
                return false;
            }
        };
        
        btn.setFont(FONT_BUTTON);
        btn.setFocusPainted(false);
        btn.setBorderPainted(false);
        btn.setContentAreaFilled(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.setPreferredSize(new Dimension(180, 45));
        
        if (action != null) {
            btn.addActionListener(action);
        }
        
        return btn;
    }
    
    private Icon crearIconoArbol() {
        return new Icon() {
            @Override
            public void paintIcon(Component c, Graphics g, int x, int y) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setColor(PRIMARY);
                // Dibujar un árbol simple
                g2.fillOval(x + 8, y + 2, 8, 8);
                g2.fillOval(x + 3, y + 8, 7, 7);
                g2.fillOval(x + 14, y + 8, 7, 7);
                g2.fillRect(x + 10, y + 14, 4, 6);
                g2.dispose();
            }
            @Override public int getIconWidth() { return 24; }
            @Override public int getIconHeight() { return 24; }
        };
    }
    
    private Icon crearIconoHeap() {
        return new Icon() {
            @Override
            public void paintIcon(Component c, Graphics g, int x, int y) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setColor(PRIMARY);
                // Triángulo invertido (heap)
                int[] xPoints = {x + 12, x + 2, x + 22};
                int[] yPoints = {y + 18, y + 4, y + 4};
                g2.fillPolygon(xPoints, yPoints, 3);
                g2.dispose();
            }
            @Override public int getIconWidth() { return 24; }
            @Override public int getIconHeight() { return 24; }
        };
    }
    
    private Icon crearIconoBST() {
        return new Icon() {
            @Override
            public void paintIcon(Component c, Graphics g, int x, int y) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setColor(PRIMARY);
                g2.setStroke(new BasicStroke(2));
                // Líneas del BST
                g2.drawLine(x + 12, y + 4, x + 6, y + 12);
                g2.drawLine(x + 12, y + 4, x + 18, y + 12);
                g2.fillOval(x + 9, y + 1, 6, 6);
                g2.fillOval(x + 3, y + 10, 6, 6);
                g2.fillOval(x + 15, y + 10, 6, 6);
                g2.dispose();
            }
            @Override public int getIconWidth() { return 24; }
            @Override public int getIconHeight() { return 24; }
        };
    }

    static class RoundedBorder extends AbstractBorder {
        private int radius;
        private Color color;
        
        public RoundedBorder(int radius, Color color) {
            this.radius = radius;
            this.color = color;
        }
        
        @Override
        public void paintBorder(Component c, Graphics g, int x, int y, int width, int height) {
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2.setColor(color);
            g2.draw(new RoundRectangle2D.Float(x, y, width - 1, height - 1, radius, radius));
            g2.dispose();
        }
        
        @Override
        public Insets getBorderInsets(Component c) {
            return new Insets(4, 8, 4, 8);
        }
        
        @Override
        public Insets getBorderInsets(Component c, Insets insets) {
            insets.left = insets.right = 8;
            insets.top = insets.bottom = 4;
            return insets;
        }
    }

    private void stylePrimary(JButton btn) {
        btn.setBackground(PRIMARY);
        btn.setForeground(Color.WHITE);
        btn.setFocusPainted(false);
        btn.setBorder(BorderFactory.createEmptyBorder(10, 18, 10, 18));
    }

    private void styleSecondary(JButton btn) {
        btn.setBackground(PANEL);
        btn.setForeground(TEXT);
        btn.setFocusPainted(false);
        btn.setBorder(BorderFactory.createLineBorder(BORDER));
    }

    private Image cargarLogo() {
        try {
            File f = new File("../resources/logo.png");
            if (!f.exists()) return null;
            ImageIcon icon = new ImageIcon(f.getAbsolutePath());
            return icon.getImage();
        } catch (Exception e) {
            return null;
        }
    }

    private static String normalizarTexto(String t) {
        if (t == null) return "";
        return Normalizer.normalize(t, Normalizer.Form.NFD)
                .replaceAll("[^\\p{ASCII}]", "")
                .toLowerCase();
    }

    private static void aplicarTemaAzulClaro() {
        Color primary = new Color(0, 120, 212);
        Color primaryLight = new Color(232, 241, 251);
        Color bg = new Color(247, 249, 252);
        Color border = new Color(227, 231, 239);
        Font base = new Font("Segoe UI", Font.PLAIN, 16);

        UIManager.put("Panel.background", bg);
        UIManager.put("OptionPane.background", bg);
        UIManager.put("OptionPane.messageFont", base);
        UIManager.put("OptionPane.buttonFont", base.deriveFont(Font.BOLD));

        UIManager.put("Button.background", primary);
        UIManager.put("Button.foreground", Color.WHITE);
        UIManager.put("Button.font", base.deriveFont(Font.BOLD));
        UIManager.put("Button.border", BorderFactory.createEmptyBorder(10, 16, 10, 16));

        UIManager.put("TabbedPane.background", bg);
        UIManager.put("TabbedPane.selected", primaryLight);
        UIManager.put("TabbedPane.borderHightlightColor", primary);

        UIManager.put("ComboBox.background", Color.WHITE);
        UIManager.put("ComboBox.foreground", Color.DARK_GRAY);
        UIManager.put("ComboBox.border", BorderFactory.createLineBorder(border));

        UIManager.put("Table.background", Color.WHITE);
        UIManager.put("Table.alternateRowColor", primaryLight);
        UIManager.put("TableHeader.background", primary);
        UIManager.put("TableHeader.foreground", Color.WHITE);
        UIManager.put("TableHeader.font", base.deriveFont(Font.BOLD));
        UIManager.put("Table.gridColor", border);

        UIManager.put("ScrollBar.thumb", primary);
        UIManager.put("ScrollBar.track", primaryLight);

        UIManager.put("TextField.border", BorderFactory.createLineBorder(border));
        UIManager.put("TextField.font", base);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new MainWindowDashboard().setVisible(true));
    }
}