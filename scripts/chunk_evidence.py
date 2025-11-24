#!/usr/bin/env python3
# Plot: Tempo vs Chunk per TUTTI i threads disponibili nei file

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def main():
    results_dir = Path("../results")
    plots_dir = Path("../plots")
    plots_dir.mkdir(exist_ok=True)

    parallel_files = list(results_dir.glob("*_parallel.csv"))
    matrices = {}
    for pfile in parallel_files:
        name = pfile.stem.replace("_parallel", "")
        sfile = results_dir / f"{name}_sequential.csv"
        if sfile.exists():
            matrices[name] = (pfile, sfile)

    if not matrices:
        print("Nessun file trovato")
        return

    all_rows = []

    # Carica dati
    for name, (pfile, sfile) in matrices.items():
        df_p = pd.read_csv(pfile)

        if not {"schedule","threads","chunk","time_ms"}.issubset(df_p.columns):
            raise ValueError(f"Colonne mancanti in {pfile}")

        df_group = df_p.groupby(
            ["schedule", "chunk", "threads"], 
            as_index=False
        ).agg(time_ms_90=("time_ms", lambda x: x.quantile(0.9)))

        df_group["matrix"] = name
        all_rows.append(df_group)

    df_all = pd.concat(all_rows, ignore_index=True)

    # 🔍 trova TUTTI i threads presenti nei file
    all_threads = sorted(df_all["threads"].unique())
    print("Threads trovati nei file:", all_threads)

    # ============================================================
    # 🔥 PLOT: tempo vs chunk per TUTTI i thread trovati nei file
    # ============================================================
    for sched in df_all["schedule"].unique():
        df_sched = df_all[df_all["schedule"] == sched]

        # FIGURA PIÙ GRANDE 👍
        plt.figure(figsize=(14, 6))

        for thr in all_threads:
            df_thr = df_sched[df_sched["threads"] == thr].copy()
            if df_thr.empty:
                continue

            df_thr = df_thr.groupby("chunk", as_index=False).agg(
                mean_time=("time_ms_90", "mean")
            )
            df_thr = df_thr.sort_values("chunk")

            plt.plot(
                df_thr["chunk"], 
                df_thr["mean_time"],
                marker="o",
                linewidth=2,
                markersize=8,
                label=f"threads={thr}"
            )

        # 🔥 Tick dell’asse X: chiari, in grassetto e corrispondenti ai chunk
        # 🔥 Tick dell’asse X: chiari e corrispondenti ai chunk
        x_chunks = sorted(df_sched["chunk"].unique())
        plt.xticks(
            x_chunks,
            [str(c) for c in x_chunks],
            fontsize=12    # ← NOTA: rimosso il grassetto
        )


        plt.xlabel("Chunk size", fontsize=14)
        plt.ylabel("Tempo (ms)", fontsize=14)
        plt.title(f"Tempo vs Chunk - schedule={sched}", fontsize=16, fontweight="bold")
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=12)

        outname = f"time_vs_chunk_{sched}.png"
        plt.tight_layout()
        plt.savefig(plots_dir / outname)
        plt.close()

        print(f"Salvato: {outname}")


if __name__ == "__main__":
    main()
