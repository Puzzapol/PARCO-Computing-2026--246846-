import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RESULTS = BASE / "results"
PLOTS = BASE / "plots"

def load_perf_parallel(name):
    perf = pd.read_csv(RESULTS / f"{name}_parallel_perf.csv")
    return perf


def main():
    PLOTS.mkdir(exist_ok=True)

    # Trova tutte le matrici presenti
    matrices = sorted({p.name.split("_")[0] for p in RESULTS.glob("*_parallel_perf.csv")})
    print("Trovate matrici:", matrices)

    all_data = {}

    for m in matrices:
        df = load_perf_parallel(m)
        df["miss_rate"] = df["cache_miss"] / df["cache_ref"]
        all_data[m] = df

    schedules = ["static", "dynamic", "guided"]

    # ============================
    #   1) Grafico per ogni scheduling
    # ============================
    for sched in schedules:
        plt.figure(figsize=(10,6))

        for m in matrices:
            df = all_data[m]
            sub = df[df["schedule"] == sched].copy()
            sub = sub.groupby("threads").mean(numeric_only=True).reset_index()

            plt.plot(sub["threads"], sub["miss_rate"],
                     marker="o", label=m)

        plt.xscale("log", base=2)
        plt.xticks([2,4,8,16,32], [2,4,8,16,32])
        plt.xlabel("Threads")
        plt.ylabel("Cache miss rate (miss/ref)")
        plt.title(f"Cache MISS-RATE – scheduling = {sched}")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(PLOTS / f"cache_missrate_schedule_{sched}.png")
        plt.close()

    


if __name__ == "__main__":
    main()
