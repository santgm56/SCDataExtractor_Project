import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

public class RunPython {
    public static void start(){
        try {
            // Rutas relativas dentro del proyecto
            String pythonPath = "venv\\Scripts\\python.exe";
            String scriptPath = "main.py";

            ProcessBuilder pb = new ProcessBuilder(
                pythonPath,
                scriptPath
            );

            pb.redirectErrorStream(true);

            Process process = pb.start();

            // Enviar opción de e-commerce (NO CAMBIAR)
            try ( // Para enviar inputs al script:
                    BufferedWriter writer = new BufferedWriter(
                            new OutputStreamWriter(process.getOutputStream())
                    )) {
                // Enviar opción de e-commerce (NO CAMBIAR)
                writer.write("2");
                writer.newLine();   // ESTO ES EL ENTER
                writer.flush();
                
                // 1: Mercado Libre, 2: Alkosto (Cambiar para selección por parte del usuario)
                writer.write("2");
                writer.newLine();
                writer.flush();
                
                // Item (Cambiar para selección por parte del usuario)
                writer.write("Computador");
                writer.newLine();
                writer.flush();
                
                // Cantidad de items (Cambiar para selección por parte del usuario)
                writer.write("10");
                writer.newLine();
                writer.flush();
                
                // Cantidad de páginas visitadas (Cambiar para selección por parte del usuario)
                writer.write("1");
                writer.newLine();
                writer.flush();
                
                // Generar reporte (idk si cambiarlo o no)
                writer.write("n");
                writer.newLine();
                writer.flush();
                
                // Enter para continuar (NO CAMBIAR)
                writer.newLine();
                
                // Cerrar programa (NO CAMBIAR)
                writer.write("4");
                writer.newLine();
            }

            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
            )) {
                String line;
                while (process.isAlive() && (line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }

            int exitCode = process.waitFor();
            System.out.println("Python terminó con código: " + exitCode);
            process.getOutputStream().close();
            process.getInputStream().close();
            process.getErrorStream().close();

            process.destroy();

        } catch (IOException | InterruptedException e) {
        }
    }
}
