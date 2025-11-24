# Sparse Matrix-Vector Multiplication (SpMV) on HPC Cluster

## Overview

This project implements and evaluates Sparse Matrix–Vector Multiplication (SpMV) using a sequential and a parallel OpenMP version. Matrices are stored in Matrix Market (.mtx) format. The evaluation includes execution time, GFLOPS, memory bandwidth, arithmetic intensity (AI), speedup, efficiency, scheduling effects, chunk-size effects, and hardware performance counters collected using perf. All experiments are executed on an HPC cluster via PBS job scripts, while plots are generated locally using Python.

---

## Repository Structure

repo/
│-- src/
│   ├── main_sequential.cpp
│   └── main_parallel.cpp
│
│-- scripts/
│   ├── run_sequential.pbs
│   ├── run_parallel.pbs
│   ├── run_sequential_perf.pbs
│   └── run_parallel_perf.pbs
│
│-- matrix/
│-- results/
│-- plots/
│-- README.md

---

## HPC Environment

The PBS scripts load the following modules:

module load gcc91
module load perf

Parallel jobs request:

#PBS -l select=1:ncpus=32:mem=16gb
#PBS -l place=excl
#PBS -q short_cpuQ

Sequential jobs request:

#PBS -l select=1:ncpus=1:mem=4gb

---

## Build Instructions

Compilation is automatically handled inside the PBS scripts.

### Sequential build
g++ -std=c++11 src/main_sequential.cpp -o results/main_sequential

### Parallel build
g++ -std=c++11 -fopenmp src/main_parallel.cpp -o results/main_parallel

---

## Running Experiments on the Cluster

### 1. Parallel execution
qsub -v MATRIX=<matrix.mtx> scripts/run_parallel.pbs

This script:
- compiles the parallel code
- tests scheduling policies (static, dynamic, guided)
- tests chunk sizes (1, 8, 64, 256, 512)
- tests threads (2, 4, 8, 16, 32)
- writes results to results/<matrix>_parallel.csv

Parallel CSV format:
schedule,threads,chunk,time_ms,gflops,bw_gbs,ai

---

### 2. Sequential execution
qsub -v MATRIX=<matrix.mtx> scripts/run_sequential.pbs

Output:
results/<matrix>_sequential.csv

---

### 3. Hardware profiling (perf)

Parallel profiling:
qsub -v MATRIX=<matrix.mtx> scripts/run_parallel_perf.pbs

Sequential profiling:
qsub -v MATRIX=<matrix.mtx> scripts/run_sequential_perf.pbs

Perf CSV format:
schedule,threads,chunk,cycles,instructions,cache_ref,cache_miss

---

## Parameters

### Number of threads
export OMP_NUM_THREADS=<value>

### Scheduling policy
export OMP_SCHEDULE="<policy>,<chunk>"

policy ∈ {static, dynamic, guided}  
chunk ∈ {1, 8, 64, 256, 512}

### Selecting the matrix
qsub -v MATRIX=<file.mtx> scripts/<job>.pbs

---

## Plotting (executed locally)

The cluster environment does not support matplotlib.  
Plots must be generated locally.

### Install required Python packages:
pip install numpy pandas matplotlib

### Generate plots:
python3 scripts/bandwidth.py
python3 scripts/efficiency.py
python3 scripts/chunk_evidence.py
python3 scripts/parallel_cache_misses.py

All plots are saved in:
plots/

---

## Generated Plots

### Bandwidth (90th percentile)
plots/bandwidth_90pct_static.png  
plots/bandwidth_90pct_dynamic.png  
plots/bandwidth_90pct_guided.png  

### Cache miss rate
plots/cache_missrate_schedule_static.png  
plots/cache_missrate_schedule_dynamic.png  
plots/cache_missrate_schedule_guided.png  

### Efficiency
plots/efficiency_static.png  
plots/efficiency_dynamic.png  
plots/efficiency_guided.png  

### Speedup across all chunk sizes
plots/static_ALLCHUNKS_speedup.png  
plots/dynamic_ALLCHUNKS_speedup.png  
plots/guided_ALLCHUNKS_speedup.png  

### Time vs chunk size
plots/time_vs_chunk_static.png  
plots/time_vs_chunk_dynamic.png  
plots/time_vs_chunk_guided.png  

---

## Matrix Files (Download and Installation)

Several matrices are included directly in the repository:

bcsstm08.mtx  
cavity07.mtx  
ecology1.mtx  
G67.mtx  
hcircuit.mtx  
msc10848.mtx  

Two matrices exceed GitHub’s 100 MB file-size limit and are **not included**:

nlpkkt80.mtx  (~251 MB)  
x104.mtx      (~141 MB)

### Download the missing matrices

nlpkkt80.mtx:
https://sparse.tamu.edu/Kkt/nlpkkt80

x104.mtx:
https://sparse.tamu.edu/HB/x104

Download the Matrix Market (.mtx) file.

### Upload to the HPC cluster

From your local machine:
scp nlpkkt80.mtx USER@hpc-head-n1.unitn.it:/path/to/repo/matrix/
scp x104.mtx USER@hpc-head-n1.unitn.it:/path/to/repo/matrix/

### Required directory structure
repo/
 └── matrix/
      ├── nlpkkt80.mtx
      └── x104.mtx

The PBS scripts automatically detect and use the matrices if present.

---

## Reproducibility

This project is fully reproducible because:
- no absolute paths are used  
- all experiments are performed through PBS scripts  
- all performance results are exported to CSV  
- all plot scripts regenerate the exact figures  
- missing large matrices can be added manually

---

## Contact
paolo.sarcletti@studenti.unitn.it

Paolo Sarcletti
