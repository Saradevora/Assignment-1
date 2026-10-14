import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Paths;

public class MatrixMult {

    private static double[][] loadMatrix(String path, int n) throws Exception {
        byte[] bytes = Files.readAllBytes(Paths.get(path));
        ByteBuffer bb = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
        double[][] m = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                m[i][j] = bb.getDouble();
            }
        }
        return m;
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 5) {
            System.err.println("Uso: java MatrixMult <n> <reps> <warmup> <A.bin> <B.bin> [out_C.bin]");
            return;
        }

        int n = Integer.parseInt(args[0]);
        int reps = Integer.parseInt(args[1]);
        int warmup = Integer.parseInt(args[2]);
        String pathA = args[3];
        String pathB = args[4];
        String pathOut = (args.length >= 6) ? args[5] : null;

        double[][] A = loadMatrix(pathA, n);
        double[][] B = loadMatrix(pathB, n);
        double[][] C = new double[n][n];

        int totalRuns = warmup + reps;

        for (int r = 0; r < totalRuns; r++) {
            // Reiniciar matriz C
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    C[i][j] = 0.0;
                }
            }

            long t0 = System.nanoTime();

            // Algoritmo estándar I-J-K
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    double sum = 0.0;
                    for (int k = 0; k < n; k++) {
                        sum += A[i][k] * B[k][j];
                    }
                    C[i][j] = sum;
                }
            }

            long t1 = System.nanoTime();
            double elapsedSec = (t1 - t0) / 1e9;

            // Consumir el resultado (checksum)
            double checksum = 0.0;
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    checksum += C[i][j];
                }
            }

            String phase = (r < warmup) ? "warmup" : "measured";
            int repNum = (r < warmup) ? (r + 1) : (r - warmup + 1);

            System.out.printf("%s,%d,%.9f,%.9e\n", phase, repNum, elapsedSec, checksum);
            System.out.flush();
        }

        // Exportar resultado en formato little-endian para los tests
        if (pathOut != null) {
            ByteBuffer outBB = ByteBuffer.allocate(n * n * 8).order(ByteOrder.LITTLE_ENDIAN);
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    outBB.putDouble(C[i][j]);
                }
            }
            try (FileOutputStream fos = new FileOutputStream(pathOut)) {
                fos.write(outBB.array());
            }
        }
    }
}