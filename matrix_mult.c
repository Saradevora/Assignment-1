#include <stdio.h>
#include <stdlib.h>
#include <time.h>

double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

double* load_matrix(const char *path, int n) {
    double *m = (double *)malloc(n * n * sizeof(double));
    if (!m) return NULL;
    FILE *f = fopen(path, "rb");
    if (!f) { free(m); return NULL; }
    size_t r = fread(m, sizeof(double), n * n, f);
    fclose(f);
    if (r != (size_t)(n * n)) { free(m); return NULL; }
    return m;
}

void multiply_kernel(double *A, double *B, double *C, int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += A[i * n + k] * B[k * n + j];
            }
            C[i * n + j] = sum;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 6) return 1;
    int n = atoi(argv[1]);
    int reps = atoi(argv[2]);
    int warmup = atoi(argv[3]);
    const char *path_A = argv[4];
    const char *path_B = argv[5];
    const char *path_out = (argc >= 7) ? argv[6] : NULL;

    double *A = load_matrix(path_A, n);
    double *B = load_matrix(path_B, n);
    double *C = (double *)calloc(n * n, sizeof(double));
    if (!A || !B || !C) return 2;

    int total_runs = warmup + reps;
    for (int r = 0; r < total_runs; r++) {
        for (int i = 0; i < n * n; i++) C[i] = 0.0;

        double t0 = get_time_sec();
        multiply_kernel(A, B, C, n);
        double t1 = get_time_sec();

        double checksum = 0.0;
        for (int i = 0; i < n * n; i++) checksum += C[i];

        const char *phase = (r < warmup) ? "warmup" : "measured";
        int rep_num = (r < warmup) ? (r + 1) : (r - warmup + 1);
        printf("%s,%d,%.9f,%.9e\n", phase, rep_num, t1 - t0, checksum);
        fflush(stdout);
    }

    if (path_out && path_out[0] != '\0') {
        FILE *fout = fopen(path_out, "wb");
        if (fout) {
            fwrite(C, sizeof(double), n * n, fout);
            fclose(fout);
        }
    }

    free(A); free(B); free(C);
    return 0;
}