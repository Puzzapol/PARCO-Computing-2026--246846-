import pandas as pd
import matplotlib.pyplot as plt
import os

# ========== PATH RELATIVO ==========
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

# Carico tutti i file *_parallel.csv
files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_parallel.csv")]

dfs = []
for f in files:
    df = pd.read_csv(os.path.join(RESULTS_DIR, f))
    matrix_name = f.replace("_parallel.csv", "")
    df["matrix"] = matrix_name
    dfs.append(df)

all_par = pd.concat(dfs, ignore_index=True)

# ========== CALCOLO 90° PERCENTILE ==========
percentile_df = (
    all_par.groupby(["matrix", "threads", "schedule"])["bw_gbs"]
    .quantile(0.90)
    .reset_index()
)

# ========== LISTA SCHEDULING ==========
sched_types = ["static", "dynamic", "guided"]

# ========== GENERO UN PLOT PER OGNI SCHEDULING ==========
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "..", "plots")

for sched in sched_types:

    sub_df = percentile_df[percentile_df["schedule"] == sched]

    plt.figure(figsize=(10, 6))

    for mat, sub in sub_df.groupby("matrix"):
        plt.plot(
            sub["threads"],
            sub["bw_gbs"],
            marker='o',
            linewidth=2,
            label=f"{mat}"
        )

    plt.xlabel("Threads")
    plt.ylabel("Bandwidth 90° percentile (GB/s)")
    plt.title(f"90th Percentile Bandwidth vs Threads — {sched.capitalize()} Scheduling")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    # Salvataggio automatico del plot
    out_path = os.path.join(PLOTS_DIR, f"bandwidth_90pct_{sched}.png")
    plt.savefig(out_path, dpi=200)

    print(f"Plot salvato in: {out_path}")
