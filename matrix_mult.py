import sys
import time
from array import array

def load_matrix(path, n):
    a = array("d")
    with open(path, "rb") as f:
        a.fromfile(f, n * n)
    return [a[i * n : (i + 1) * n].tolist() for i in range(n)]

def main():
    if len(sys.argv) < 6:
        print("Uso: python matrix_mult.py <n> <reps> <warmup> <A.bin> <B.bin> [out_C.bin]", file=sys.stderr)
        return

    n = int(sys.argv[1])
    reps = int(sys.argv[2])
    warmup = int(sys.argv[3])
    path_A = sys.argv[4]
    path_B = sys.argv[5]
    path_out = sys.argv[6] if len(sys.argv) >= 7 else None

    A = load_matrix(path_A, n)
    B = load_matrix(path_B, n)

    total_runs = warmup + reps

    for r in range(total_runs):
        C = [[0.0] * n for _ in range(n)]

        t0 = time.perf_counter()

        for i in range(n):
            for j in range(n):
                total = 0.0
                for k in range(n):
                    total += A[i][k] * B[k][j]
                C[i][j] = total

        t1 = time.perf_counter()
        elapsed_sec = t1 - t0

        checksum = sum(sum(row) for row in C)

        phase = "warmup" if r < warmup else "measured"
        rep_num = (r + 1) if r < warmup else (r - warmup + 1)

        print(f"{phase},{rep_num},{elapsed_sec:.9f},{checksum:.9e}", flush=True)

    if path_out:
        out_arr = array("d", [elem for row in C for elem in row])
        with open(path_out, "wb") as f:
            out_arr.tofile(f)

if __name__ == "__main__":
    main()