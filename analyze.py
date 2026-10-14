import os
import csv
import numpy as np
import matplotlib.pyplot as plt

raw_csv_path = os.path.join("data", "raw_results.csv")
mem_csv_path = os.path.join("data", "memory_results.csv")
summary_csv_path = os.path.join("data", "summary_results.csv")

os.makedirs("figures", exist_ok=True)

def get_median(values):
    s = sorted(values)
    n = len(s)
    if n == 0: return 0.0
    mid = n // 2
    return s[mid] if n % 2 == 1 else (s[mid-1] + s[mid]) / 2.0

def get_iqr(values):
    s = sorted(values)
    n = len(s)
    if n < 2: return 0.0
    q1 = s[int(0.25 * (n - 1))]
    q3 = s[int(0.75 * (n - 1))]
    return q3 - q1

data_time = {}
with open(raw_csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r["Phase"] == "measured" and r["Status"] == "ok":
            lang = r["Language"]
            n = int(r["Size"])
            sec = float(r["Time_sec"])
            key = (lang, n)
            if key not in data_time: data_time[key] = []
            data_time[key].append(sec)

data_mem = {}
with open(mem_csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r["Status"] == "ok":
            data_mem[(r["Language"], int(r["Size"]))] = float(r["Peak_Working_Set_MiB"])

summary_rows = []
sorted_keys = sorted(data_time.keys(), key=lambda x: (x[1], x[0]))

print("=========================================================================================")
print("                          RESULTADOS EXPERIMENTALES REALES")
print("=========================================================================================")
print(f"{'Language':<8} | {'Size (n)':<8} | {'Median (ms)':<12} | {'IQR (ms)':<10} | {'Peak RAM (MiB)':<14}")
print("-" * 80)

for lang, n in sorted_keys:
    times_ms = [t * 1000.0 for t in data_time[(lang, n)]]
    med = get_median(times_ms)
    iqr_val = get_iqr(times_ms)
    mem_mib = data_mem.get((lang, n), 0.0)

    summary_rows.append({
        "Language": lang,
        "Size": n,
        "Median_ms": f"{med:.3f}",
        "IQR_ms": f"{iqr_val:.3f}",
        "Peak_RAM_MiB": f"{mem_mib:.2f}"
    })

    print(f"{lang:<8} | {n:<8} | {med:<12.3f} | {iqr_val:<10.3f} | {mem_mib:<14.2f}")

with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Language", "Size", "Median_ms", "IQR_ms", "Peak_RAM_MiB"])
    writer.writeheader()
    writer.writerows(summary_rows)

print(f"\n[OK] Resumen procesado guardado en: {summary_csv_path}")

# GENERACIÓN DE GRÁFICAS
plt.figure(figsize=(8, 5))
for lang in ["C", "Java", "Python"]:
    ns = [k[1] for k in sorted_keys if k[0] == lang]
    meds = [get_median([t * 1000.0 for t in data_time[(lang, n)]]) for n in ns]
    if meds:
        plt.loglog(ns, meds, 'o-', linewidth=2, label=f"{lang}")

plt.xlabel("Matrix Size (n)", fontsize=11)
plt.ylabel("Execution Time (ms) - Log Scale", fontsize=11)
plt.title("Matrix Multiplication Scaling Behavior O(n³)", fontsize=12, fontweight='bold')
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig("figures/fig1_time.png", dpi=300)
print("[OK] Gráfica de tiempos guardada en 'figures/fig1_time.png'")

plt.figure(figsize=(8, 5))
for lang in ["C", "Java", "Python"]:
    ns = [k[1] for k in sorted_keys if k[0] == lang]
    mems = [data_mem.get((lang, n), 0.0) for n in ns]
    if mems:
        plt.plot(ns, mems, 's--', linewidth=2, label=f"{lang}")

plt.xlabel("Matrix Size (n)", fontsize=11)
plt.ylabel("Peak Working Set (MiB)", fontsize=11)
plt.title("Peak Memory Footprint Across Matrix Sizes", fontsize=12, fontweight='bold')
plt.legend()
plt.grid(True, ls="--", alpha=0.5)
plt.tight_layout()
plt.savefig("figures/fig2_memory.png", dpi=300)
print("[OK] Gráfica de memoria guardada en 'figures/fig2_memory.png'")