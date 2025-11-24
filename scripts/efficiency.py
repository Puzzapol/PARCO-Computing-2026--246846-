import pandas as pd
import matplotlib.pyplot as plt
import os

# ===== PATH RELATIVO =====
BASE_DIR = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(BASE_DIR, "..", "results")
PLOTS_DIR = os.path.join(BASE_DIR, "..", "plots")

os.makedirs(PLOTS_DIR, exist_ok=True)

# ===== Trova file sequenziali e paralleli =====
parallel_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_parallel.csv")]
sequential_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_sequential.csv")]

# ===== Carica versioni SEQUENZIALI =====
seq_times = {}

for f in sequential_files:
    df = pd.read_csv(os.path.join(RESULTS_DIR, f))
    matrix = f.replace("_sequential.csv", "")
    seq_times[matrix] = df["time_ms"].mean()

# ===== Carica versioni PARALLELE =====
dfs = []

for f in parallel_files:
    df = pd.read_csv(os.path.join(RESULTS_DIR, f))
    matrix = f.replace("_parallel.csv", "")
    df["matrix"] = matrix

    if matrix not in seq_times:
        print(f"⚠️ Manca il file sequenziale per {matrix}")
        continue

    T_seq = seq_times[matrix]
    df["speedup"] = T_seq / df["time_ms"]
    df["efficiency"] = df["speedup"] / df["threads"]

    dfs.append(df)

all_par = pd.concat(dfs, ignore_index=True)

# ===== Ricava i vari scheduling presenti =====
schedules = all_par["schedule"].unique()
print("Schedulings trovati:", schedules)

# ===== Plot per ogni scheduling =====
for sched in schedules:
    sub = all_par[all_par["schedule"] == sched]

    plt.figure(figsize=(10, 6))

    for mat, mat_df in sub.groupby("matrix"):
        eff_df = (
            mat_df.groupby("threads")["efficiency"]
            .mean()
            .reset_index()
        )

        plt.plot(
            eff_df["threads"],
            eff_df["efficiency"],
            marker='o',
            linewidth=2,
            label=mat
        )

    plt.xlabel("Threads")
    plt.ylabel("Efficiency")
    plt.title(f"Parallel Efficiency vs Threads — schedule={sched}")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    out_file = os.path.join(PLOTS_DIR, f"efficiency_{sched}.png")
    plt.savefig(out_file, dpi=200)
    plt.close()

    print(f"Plot salvato: {out_file}")
