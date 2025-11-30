import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.List;

public class RunPython {
    
    // Método para ejecutar scraping con parámetros dinámicos
    public static List<String> ejecutarScraping(int tienda, String producto, int cantidadItems, int cantidadPaginas, boolean generarReporte) {
        List<String> lineasSalida = new ArrayList<>();
        
        try {
            // Rutas relativas - venv y main.py están en la raíz del proyecto (un nivel arriba)
            String pythonPath = "..\\venv\\Scripts\\python.exe";
            String scriptPath = "..\\main.py";

            ProcessBuilder pb = new ProcessBuilder(pythonPath, scriptPath);
            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Enviar parámetros al script de Python
            try (BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(process.getOutputStream()))) {
                
                // Opción de e-commerce
                writer.write("2");
                writer.newLine();
                writer.flush();
                
                // Tienda (1: MercadoLibre, 2: Alkosto)
                writer.write(String.valueOf(tienda));
                writer.newLine();
                writer.flush();
                
                // Producto a buscar
                writer.write(producto);
                writer.newLine();
                writer.flush();
                
                // Cantidad de items
                writer.write(String.valueOf(cantidadItems));
                writer.newLine();
                writer.flush();
                
                // Cantidad de páginas
                writer.write(String.valueOf(cantidadPaginas));
                writer.newLine();
                writer.flush();
                
                // Generar reporte
                writer.write(generarReporte ? "s" : "n");
                writer.newLine();
                writer.flush();
                
                // Enter para continuar
                writer.newLine();
                writer.flush();
                
                // Salir del programa
                writer.write("4");
                writer.newLine();
                writer.flush();
            }

            // Capturar salida del proceso
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                
                String line;
                while (process.isAlive() && (line = reader.readLine()) != null) {
                    System.out.println(line);
                    lineasSalida.add(line);
                }
            }

            int exitCode = process.waitFor();
            System.out.println("Python terminó con código: " + exitCode);
            
            // Cerrar recursos
            process.getOutputStream().close();
            process.getInputStream().close();
            process.getErrorStream().close();
            process.destroy();

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        
        return lineasSalida;
    }
}