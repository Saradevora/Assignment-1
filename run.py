import os
import time
import subprocess
import psutil
import numpy as np

SIZES = [10, 50, 100, 200, 300, 400, 500, 600, 800, 1000]
REPETITIONS = 5
WARMUP_JAVA = 2
WARMUP_OTHER = 0
TIMEOUT_SEC = 600

os.makedirs("data", exist_ok=True)
raw_csv_path = os.path.join("data", "raw_results.csv")
mem_csv_path = os.path.join("data", "memory_results.csv")

def compile_programs():
    print("--- COMPILACIÓN ---")
    gcc_path = r"C:\w64devkit\bin\gcc.exe"
    compiler = gcc_path if os.path.exists(gcc_path) else "gcc"
    
    subprocess.run([compiler, "-O2", "matrix_mult.c", "-o", "matrix_mult_c.exe"], check=True)
    print("  [OK] C compilado con -O2")
    
    subprocess.run(["javac", "MatrixMult.java"], check=True)
    print("  [OK] Java compilado")

def run_with_monitoring(cmd_list, timeout):
    # Ejecución directa pasando el entorno de variables del sistema
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    
    p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    
    peak_wset = 0
    t0 = time.time()
    timed_out = False

    while p.poll() is None:
        try:
            ps = psutil.Process(p.pid)
            # Medimos también los procesos hijos generados por la JVM o intérpretes
            children = ps.children(recursive=True)
            current_mem = ps.memory_info().peak_wset
            for child in children:
                current_mem += child.memory_info().peak_wset
            peak_wset = max(peak_wset, current_mem)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        if time.time() - t0 > timeout:
            p.kill()
            timed_out = True
            break
        time.sleep(0.01)

    stdout, stderr = p.communicate()
    return stdout, peak_wset, timed_out, stderr

def main():
    compile_programs()

    targets = [
        ("C", [".\\matrix_mult_c.exe"], WARMUP_OTHER),
        ("Java", ["java", "-Duser.language=en", "-Duser.country=US", "MatrixMult"], WARMUP_JAVA),
        ("Python", ["python", "matrix_mult.py"], WARMUP_OTHER)
    ]

    with open(raw_csv_path, "w", encoding="utf-8") as f_raw, \
         open(mem_csv_path, "w", encoding="utf-8") as f_mem:

        f_raw.write("Language,Size,Phase,Repetition,Time_sec,Checksum,Checksum_Rel_Err,Status\n")
        f_mem.write("Language,Size,Peak_Working_Set_MiB,Status\n")

        for lang, base_cmd, warmup in targets:
            print(f"\n================ MIDE {lang} ================")
            
            for n in SIZES:
                path_A = f"inputs/A_{n}.bin"
                path_B = f"inputs/B_{n}.bin"

                if not os.path.exists(path_A) or not os.path.exists(path_B):
                    print(f"Archivos de entrada faltantes para n={n}. Ejecuta gen_inputs.py primero.")
                    continue

                A = np.fromfile(path_A, dtype="<f8").reshape((n, n))
                B = np.fromfile(path_B, dtype="<f8").reshape((n, n))
                ref_checksum = (A @ B).sum()

                cmd = base_cmd + [str(n), str(REPETITIONS), str(warmup), path_A, path_B]
                print(f"Ejecutando {lang} para n={n}...", end="", flush=True)

                stdout, peak_bytes, timed_out, stderr = run_with_monitoring(cmd, TIMEOUT_SEC)

                if timed_out:
                    print(" [TIMEOUT!]")
                    f_raw.write(f"{lang},{n},measured,0,NaN,NaN,NaN,timeout\n")
                    f_mem.write(f"{lang},{n},{peak_bytes / (1024*1024):.3f},timeout\n")
                    print(f"  --> Cancelando tamaños mayores para {lang} debido al timeout.")
                    break

                peak_mib = peak_bytes / (1024 * 1024)
                f_mem.write(f"{lang},{n},{peak_mib:.3f},ok\n")

                lines = stdout.strip().split("\n")
                valid_count = 0

                for line in lines:
                    parts = line.strip().split(",")
                    if len(parts) == 4:
                        phase, rep, sec_str, chk_str = parts
                        try:
                            sec = float(sec_str)
                            chk = float(chk_str)
                            rel_err = abs(chk - ref_checksum) / abs(ref_checksum)
                            f_raw.write(f"{lang},{n},{phase},{rep},{sec:.9f},{chk:.9e},{rel_err:.3e},ok\n")
                            if phase == "measured":
                                valid_count += 1
                        except ValueError:
                            continue

                if valid_count == 0 and stderr:
                    print(f" [ERROR Java/Runtime]: {stderr.strip()}")
                else:
                    print(f" [OK] {valid_count} repeticiones registradas. Peak RAM: {peak_mib:.2f} MiB")

    print(f"\n¡Mediciones completadas! Datos guardados en:\n - {raw_csv_path}\n - {mem_csv_path}")

if __name__ == "__main__":
    main()