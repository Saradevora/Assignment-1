# Assignment 1: Empirical Benchmark of O(n<sup>3</sup>) Matrix Multiplication in C, Java, and Python
This repository contains the complete benchmark code, unit tests, raw experimental results, analysis scripts, and final report for **Assignment 1** of Big Data (Degree in Data Science and Engineering, ULPGC).

## Overview

The primary objective of this project is to conduct a rigorous empirical comparison of basic O(n<sup>3</sup>) dense matrix multiplication (I-J-K loop order) using double-precision floating-point numbers across three programming environments: C (GCC -O2), Java (OpenJDK 21), and Python (CPython 3.13).

## Repository Structure

```text
├── matrix_mult.c      # C implementation (GCC -O2 flat array layout)
├── MatrixMult.java    # Java implementation (with in-process HotSpot warm-up)
├── matrix_mult.py     # Native Python implementation
├── gen_inputs.py      # Binary input generator (np.random.default_rng, seed=42)
├── tests.py           # Mathematical verification suite (3x3, Identity, NumPy validation)
├── run.py             # Automated benchmark runner & psutil Peak Working Set memory monitor
├── analyze.py         # Statistical analysis (Median, IQR) & chart generator
├── data/              # Raw CSV measurements and processed summary tables
├── figures/           # Generated high-resolution scaling plots (fig1_time.png, fig2_memory.png)
└── .gitignore         # Excludes executables (.exe), bytecode (.class), and binary inputs
```

## How to Reproduce the Benchmark
- Install Python dependencies:
```text
pip install numpy psutil matplotlib
```

- Generate deterministic binary inputs:
Generates Little-Endian double-precision binary input files for sizes n ∈ {10, 50, 100, 200, 300, 400, 500, 600, 800, 1000} using seed 42.
```text
python gen_inputs.py
```

- Run correctness and accuracy tests:
Validates matrix multiplication mathematical correctness against hand-calculated results, identity matrix properties, and NumPy reference solutions (ε = 10<sup>-12</sup>).
```text
python tests.py
```

- Execute timing and memory benchmarks:
Runs 5 repetitions per language and matrix dimension, measuring execution time and tracking peak memory footprint (Working Set in MiB) with psutil.
```text
python run.py
```

- Generate statistical summary and charts:
Calculates Medians, IQRs, log-log scaling fits, and saves visualization plots to figures/.
```text
python analyze.py
```

## Hardware & Runtime Environment
- Operating System: Windows 11 Home / Pro (x86_64)
- C Compiler: GCC 13.2.0 (w64devkit) with -O2 optimization flag
- Java Runtime: OpenJDK 21 (build 21.0.2)
- Python Interpreter: CPython 3.13.0

Repository URL: https://github.com/Saradevora/Assignment-1

## Author
> **Student:** Sara Dévora Ortega  
> **Degree:** Data Science and Engineering (ULPGC)  
> **Subject:** Big Data  
> **Academic Year:** 2026–2027
