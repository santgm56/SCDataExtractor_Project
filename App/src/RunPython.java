import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

public class RunPython {

    // Referencia al proceso actual para poder cancelarlo desde la UI
    private static Process currentProcess;

    // Método para ejecutar scraping con parámetros dinámicos
    public static List<String> ejecutarScraping(int tienda, String producto, int cantidadItems, int cantidadPaginas, boolean generarReporte) throws InterruptedException {
        List<String> lineasSalida = new ArrayList<>();

        try {
            // Rutas relativas - venv y main.py están en la raíz del proyecto (un nivel arriba)
            String pythonPath = "..\\.venv\\Scripts\\python.exe";
            String scriptPath = "..\\main.py";

            // Mapear tienda
            String tiendaStr = (tienda == 2) ? "alkosto" : "mercadolibre";

            ProcessBuilder pb = new ProcessBuilder(
                    pythonPath,
                    "-X", "utf8",
                    scriptPath,
                    "--java-bridge",
                    "--tienda", tiendaStr,
                    "--producto", producto,
                    "--items", String.valueOf(cantidadItems),
                    "--paginas", String.valueOf(cantidadPaginas)
            );

            if (generarReporte) {
                pb.command().add("--export");
            }

            pb.redirectErrorStream(true);
            pb.environment().put("PYTHONIOENCODING", "utf-8");

            Process process = pb.start();
            setCurrentProcess(process);

            // Capturar salida del proceso con UTF-8
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), "UTF-8"))) {

                String line;
                while ((line = reader.readLine()) != null) {
                    // Si el hilo fue interrumpido, matar el proceso y cortar
                    if (Thread.currentThread().isInterrupted()) {
                        process.destroy();
                        throw new InterruptedException("Scraping cancelado por usuario");
                    }

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

        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            clearCurrentProcess();
        }

        return lineasSalida;
    }

    // Cancela el scraping activo desde la UI
    public static void cancelarScraping() {
        Process process = getCurrentProcess();
        if (process != null && process.isAlive()) {
            process.destroy();
            try {
                if (!process.waitFor(2, TimeUnit.SECONDS)) {
                    process.destroyForcibly();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                clearCurrentProcess();
            }
        }
    }

    private static synchronized void setCurrentProcess(Process process) {
        currentProcess = process;
    }

    private static synchronized Process getCurrentProcess() {
        return currentProcess;
    }

    private static synchronized void clearCurrentProcess() {
        currentProcess = null;
    }
}