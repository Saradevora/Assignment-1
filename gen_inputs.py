import os
import numpy as np

SEED = 42
SIZES = [10, 50, 100, 200, 300, 400, 500, 600, 800, 1000]

os.makedirs("inputs", exist_ok=True)
rng = np.random.default_rng(SEED)

print("Generando matrices aleatorias binarias en 'inputs/'...")
for n in SIZES:
    A = rng.random((n, n), dtype=np.float64)
    B = rng.random((n, n), dtype=np.float64)
    
    A.astype("<f8").tofile(f"inputs/A_{n}.bin")
    B.astype("<f8").tofile(f"inputs/B_{n}.bin")
    print(f"  [OK] Creadas A_{n}.bin y B_{n}.bin ({A.nbytes / (1024*1024):.2f} MB cada una)")

print("Generación completada.")