# Sparse Matrix-Vector Multiplication (SpMV) on HPC Cluster

## Overview
This project implements and evaluates Sparse Matrix-Vector Multiplication (SpMV) on matrices
stored in Matrix Market (.mtx) format. Two implementations are provided:

- a sequential version  
- a parallel OpenMP version with configurable scheduling and chunk size  

The project includes:
- performance measurements (execution time, GFLOPS, memory bandwidth, arithmetic intensity)
- hardware performance counters using `perf`
- PBS job scripts for running experiments on an HPC cluster
- Python scripts (executed locally) for generating plots from the results

All experiments are automated through the provided PBS scripts.

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

### Required modules

```
module load gcc91
module load perf      # only for profiling
```

### Resources for parallel jobs

```
#PBS -l select=1:ncpus=32:mem=16gb
#PBS -l place=excl
#PBS -q short_cpuQ
```

### Resources for sequential jobs

```
#PBS -l select=1:ncpus=1:mem=4gb
```

---

## Build Instructions

Compilation is performed automatically inside the PBS scripts.

### Sequential build
```
g++ -std=c++11 src/main_sequential.cpp -o results/main_sequential
```

### Parallel build
```
g++ -std=c++11 -fopenmp src/main_parallel.cpp -o results/main_parallel
```

---

## Running Experiments on the Cluster

### 1. Parallel execution

```
qsub -v MATRIX=filename.mtx scripts/run_parallel.pbs
```

The script automatically:
- compiles the parallel code  
- evaluates scheduling policies: static, dynamic, guided  
- tests thread counts: 2, 4, 8, 16, 32  
- tests chunk sizes: 1, 8, 64, 256, 512  
- performs 12 measurements for each configuration  

Output file:

```
results/<matrixname>_parallel.csv
```

CSV format:

```
schedule,threads,chunk,time_ms,gflops,bw_gbs,ai
```

---

### 2. Sequential execution

```
qsub -v MATRIX=filename.mtx scripts/run_sequential.pbs
```

Output:

```
results/<matrixname>_sequential.csv
```

---

### 3. Hardware profiling (perf)

#### Parallel profiling
```
qsub -v MATRIX=filename.mtx scripts/run_parallel_perf.pbs
```

Output columns:
```
schedule,threads,chunk,cycles,instructions,cache_ref,cache_miss
```

#### Sequential profiling
```
qsub -v MATRIX=filename.mtx scripts/run_sequential_perf.pbs
```

---

## Parameters

### Number of threads
```
export OMP_NUM_THREADS=<value>
```

### Scheduling policy
```
export OMP_SCHEDULE="<static|dynamic|guided>,<chunk>"
```

### Selecting the input matrix
```
qsub -v MATRIX=myMatrix.mtx scripts/<job>.pbs
```

---

## Plotting (executed locally)

The cluster cannot run matplotlib, so plots are generated locally from the CSV files in `results/`.

### Install dependencies

```
pip install pandas matplotlib
```

### Run the plotting scripts

```
python3 scripts/bandwidth.py
python3 scripts/efficiency.py
python3 scripts/chunk_evidence.py
python3 scripts/parallel_cache_misses.py
```

Output plots stored in:

```
plots/
```

---

## Generated Plots

### 1. Bandwidth (90th Percentile)
- plots/bandwidth_90pct_static.png  
- plots/bandwidth_90pct_dynamic.png  
- plots/bandwidth_90pct_guided.png  

### 2. Cache Miss Rate
- plots/cache_missrate_schedule_static.png  
- plots/cache_missrate_schedule_dynamic.png  
- plots/cache_missrate_schedule_guided.png  

### 3. Efficiency
- plots/efficiency_static.png  
- plots/efficiency_dynamic.png  
- plots/efficiency_guided.png  

### 4. Speedup Across All Chunk Sizes
- plots/static_ALLCHUNKS_speedup.png  
- plots/dynamic_ALLCHUNKS_speedup.png  
- plots/guided_ALLCHUNKS_speedup.png  

### 5. Time vs Chunk Size
- plots/time_vs_chunk_static.png  
- plots/time_vs_chunk_dynamic.png  
- plots/time_vs_chunk_guided.png  

---

## Implemented Methods

### Sequential SpMV
- loads the .mtx file in COO format  
- sorts entries by row, col  
- builds a prefix array (CSR-like)  
- performs a standard SpMV  
- measures execution time via `std::chrono`  

### Parallel SpMV (OpenMP)
- same preprocessing  
- OpenMP loop:

```
#pragma omp parallel for schedule(runtime)
```

Scheduling fully controlled through environment variables.

---

## Collected Metrics

Each experiment reports:

- runtime in milliseconds  
- GFLOPS  
- bandwidth (GB/s)  
- arithmetic intensity  

Perf experiments additionally measure:

- CPU cycles  
- instructions retired  
- cache references  
- cache misses  

---

## Reproducibility Notes

- All experiments use PBS job scripts  
- No absolute paths are used  
- The MATRIX variable controls the matrix used in all runs  
- All CSV files are stored in `results/`  
- All plots can be regenerated from those CSVs  

Any other user with access to the same cluster environment can reproduce the results.

---


