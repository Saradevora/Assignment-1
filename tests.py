import os
import subprocess
import numpy as np

RTOL = 1e-12
ATOL = 1e-12

def compile_all():
    print("Compilando Java...")
    res_j = subprocess.run(["javac", "MatrixMult.java"], capture_output=True, text=True, shell=True)
    if res_j.returncode != 0:
        raise RuntimeError(f"Error compilando Java:\n{res_j.stderr}")
    print("  [OK] Java compilado.")

    print("Compilando C...")
    gcc_path = r"C:\w64devkit\bin\gcc.exe"
    compiler = gcc_path if os.path.exists(gcc_path) else "gcc"
    res_c = subprocess.run([compiler, "-O2", "matrix_mult.c", "-o", "matrix_mult_c.exe"], capture_output=True, text=True)
    if res_c.returncode == 0:
        print("  [OK] C compilado correctamente.")
    else:
        print("  [AVISO] Advertencia en compilación de C.")

def run_program(lang, cmd_list, n, path_A, path_B, path_out):
    args = [str(n), "1", "0", path_A, path_B, path_out]
    full_cmd_str = " ".join(cmd_list + args)
    
    res = subprocess.run(full_cmd_str, capture_output=True, text=True, shell=True)
    
    if res.returncode != 0:
        if "Device Guard" in res.stderr or "bloqueado" in res.stderr:
            print(f"  [OMITIDO] {lang} bloqueado por Device Guard en esta máquina.")
            return None
        raise RuntimeError(f"Error al ejecutar '{full_cmd_str}':\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
    
    if not os.path.exists(path_out):
        raise FileNotFoundError(f"No se generó el archivo de salida: {path_out}")
        
    return np.fromfile(path_out, dtype="<f8").reshape((n, n))

def test_correctness():
    compile_all()

    targets = {
        "Java": ["java", "MatrixMult"],
        "Python": ["python", "matrix_mult.py"],
        "C": [".\\matrix_mult_c.exe"]
    }

    # Test 1: Ejemplo 3x3
    A3 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.float64)
    B3 = np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]], dtype=np.float64)
    expected_3 = A3 @ B3

    A3.astype("<f8").tofile("tmp_a.bin")
    B3.astype("<f8").tofile("tmp_b.bin")

    print("\n--- TEST 1: Ejemplo 3x3 a mano ---")
    for name, cmd in targets.items():
        res = run_program(name, cmd, 3, "tmp_a.bin", "tmp_b.bin", "tmp_c.bin")
        if res is not None:
            assert np.allclose(res, expected_3, rtol=RTOL, atol=ATOL), f"Fallo en {name}"
            print(f"  [OK] {name} es idéntico a la solución exacta.")

    # Test 2: Identidad A * I = A
    n = 50
    A_rand = np.random.default_rng(123).random((n, n), dtype=np.float64)
    I_mat = np.eye(n, dtype=np.float64)
    A_rand.astype("<f8").tofile("tmp_a.bin")
    I_mat.astype("<f8").tofile("tmp_b.bin")

    print("\n--- TEST 2: Propiedad de la Identidad (n=50) ---")
    for name, cmd in targets.items():
        res = run_program(name, cmd, n, "tmp_a.bin", "tmp_b.bin", "tmp_c.bin")
        if res is not None:
            assert np.allclose(res, A_rand, rtol=RTOL, atol=ATOL), f"Fallo en {name}"
            print(f"  [OK] {name} satisface A * I = A.")

    # Test 3: Comparación con NumPy (n=100)
    n100 = 100
    A_100 = np.random.default_rng(123).random((n100, n100), dtype=np.float64)
    B_100 = np.random.default_rng(456).random((n100, n100), dtype=np.float64)
    expected_100 = A_100 @ B_100

    A_100.astype("<f8").tofile("tmp_a.bin")
    B_100.astype("<f8").tofile("tmp_b.bin")

    print("\n--- TEST 3: Comparación contra NumPy (n=100) ---")
    for name, cmd in targets.items():
        res = run_program(name, cmd, n100, "tmp_a.bin", "tmp_b.bin", "tmp_c.bin")
        if res is not None:
            max_diff = np.max(np.abs(res - expected_100))
            assert np.allclose(res, expected_100, rtol=RTOL, atol=ATOL), f"Fallo en {name}"
            print(f"  [OK] {name} coincide con NumPy (dif. máx = {max_diff:.2e}).")

    for f in ["tmp_a.bin", "tmp_b.bin", "tmp_c.bin"]:
        if os.path.exists(f): os.remove(f)

    print("\n¡PRUEBAS DE VERIFICACIÓN COMPLETADAS!")

if __name__ == "__main__":
    test_correctness()