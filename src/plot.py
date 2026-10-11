import argparse
import csv
from pathlib import Path
 
import matplotlib
 
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
 
from config import SWITCH_GEN
 
ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "results" / "exp"
FIG = ROOT / "results" / "figures"
TERMS = ["chord", "smooth", "variety", "resolution", "rhythm"]
 
plt.rcParams.update({"font.size": 7, "axes.labelsize": 7, "legend.fontsize": 6,
                     "xtick.labelsize": 6, "ytick.labelsize": 6, "axes.grid": True,
                     "grid.alpha": 0.25, "figure.dpi": 150})
COL = 3.3  # largura de uma coluna do template ISMIR, em polegadas
 
 
def load_curves(name):
    """Retorna dict col -> array (n_seeds, L), com padding pelo ultimo valor."""
    files = sorted((EXP / name).glob("seed*.csv"), key=lambda p: int(p.stem[4:]))
    if not files:
        return None
    runs = []
    for f in files:
        with open(f) as fh:
            rd = csv.DictReader(fh)
            runs.append({k: [] for k in ("max", "mean", "min")})
            for row in rd:
                for k in runs[-1]:
                    runs[-1][k].append(float(row[k]))
    L = max(len(r["max"]) for r in runs)
    out = {}
    for k in ("max", "mean", "min"):
        out[k] = np.array([r[k] + [r[k][-1]] * (L - len(r[k])) for r in runs])
    return out
 
 
def load_summary():
    with open(EXP / "summary.csv") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            if k not in ("config", "crossover"):
                r[k] = float(v)
    return rows
 
 
def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=300)
    plt.close(fig)
    print("salvo:", FIG / f"{name}.pdf")
 
 
def fig_evolution(base):
    c = load_curves(base)
    if c is None:
        print(f"sem dados para {base}; pulei fig_evolution")
        return
    x = np.arange(c["max"].shape[1])
    fig, ax = plt.subplots(figsize=(COL, 2.3))
    for k, style, lab in (("max", "-", "melhor"), ("mean", "--", "média"), ("min", ":", "pior")):
        m, s = c[k].mean(0), c[k].std(0)
        ax.plot(x, m, style, label=lab, linewidth=1.2)
        ax.fill_between(x, m - s, m + s, alpha=0.15)
    ax.set_xlabel("geração")
    ax.set_ylabel("fitness")
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", title=f"n = {c['max'].shape[0]} sementes", title_fontsize=6)
    save(fig, "fig_evolution")
 
 
def fig_crossover():
    names = [n for n in ("one", "two", "mixed") if (EXP / n).exists()]
    if len(names) < 2:
        print("menos de 2 configs de cruzamento; pulei fig_crossover")
        return
    fig, ax = plt.subplots(figsize=(COL, 2.3))
    for n in names:
        c = load_curves(n)
        m, s = c["max"].mean(0), c["max"].std(0)
        x = np.arange(len(m))
        ax.plot(x, m, label=n, linewidth=1.2)
        ax.fill_between(x, m - s, m + s, alpha=0.15)
    ax.axvline(SWITCH_GEN, color="gray", linestyle=":", linewidth=0.8)
    ax.text(SWITCH_GEN + 2, 0.02, "troca (mixed)", fontsize=5, color="gray",
            transform=ax.get_xaxis_transform())
    ax.set_xlabel("geração")
    ax.set_ylabel("melhor fitness")
    ax.legend(loc="lower right")
    save(fig, "fig_crossover")
 
 
def fig_weights(rows):
    names = [n for n in ("mixed", "conservative", "adventurous", "no_variety")
             if any(r["config"] == n for r in rows)]
    if len(names) < 2:
        print("menos de 2 configs de pesos; pulei fig_weights")
        return
    fig, ax = plt.subplots(figsize=(COL, 2.3))
    w = 0.8 / len(names)
    x = np.arange(len(TERMS))
    for i, n in enumerate(names):
        vals = [np.mean([r[t] for r in rows if r["config"] == n]) for t in TERMS]
        errs = [np.std([r[t] for r in rows if r["config"] == n]) for t in TERMS]
        ax.bar(x + i * w - 0.4 + w / 2, vals, w, yerr=errs, capsize=1.5, label=n)
    ax.set_xticks(x)
    ax.set_xticklabels(TERMS)
    ax.set_ylabel("pontuação do termo")
    ax.set_ylim(0, 1.15)
    ax.legend(ncol=2, loc="upper center")
    save(fig, "fig_weights")
 
 
def table(rows):
    order = [n for n in ("one", "two", "mixed", "conservative", "adventurous", "no_variety")
             if any(r["config"] == n for r in rows)]
    ms = lambda rs, k: (np.mean([r[k] for r in rs]), np.std([r[k] for r in rs]))
    lines_md = ["| config | gen. 0 (melhor) | final (pesos da config) | final (pesos base) | gerações até 0,95 |",
                "|---|---|---|---|---|"]
    lines_tex = [r"\begin{tabular}{lcccc}", r"\hline",
                 r"Config. & Ger.\ 0 & Final & Final (base) & Ger.\ p/ 0,95 \\", r"\hline"]
    for n in order:
        rs = [r for r in rows if r["config"] == n]
        g0, fin, fb, gens = ms(rs, "gen0_max"), ms(rs, "final_fit"), ms(rs, "fit_base"), ms(rs, "gen95")
        lines_md.append(f"| {n} | {g0[0]:.3f} ± {g0[1]:.3f} | {fin[0]:.3f} ± {fin[1]:.3f} | "
                        f"{fb[0]:.3f} ± {fb[1]:.3f} | {gens[0]:.0f} |")
        tex_name = n.replace("_", "\\_")
        lines_tex.append(f"{tex_name} & {g0[0]:.3f}$\\pm${g0[1]:.3f} & {fin[0]:.3f}$\\pm${fin[1]:.3f} & "
                         f"{fb[0]:.3f}$\\pm${fb[1]:.3f} & {gens[0]:.0f} \\\\")
    lines_tex += [r"\hline", r"\end{tabular}"]
    FIG.mkdir(parents=True, exist_ok=True)
    (FIG / "table.md").write_text("\n".join(lines_md) + "\n")
    (FIG / "table.tex").write_text("\n".join(lines_tex) + "\n")
    print("\n".join(lines_md))
 
 
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", default="mixed", help="config usada no grafico de evolucao")
    a = p.parse_args()
    if not (EXP / "summary.csv").exists():
        raise SystemExit("rode primeiro: python src/experiments.py")
    rows = load_summary()
    fig_evolution(a.base)
    fig_crossover()
    fig_weights(rows)
    table(rows)
 
 
if __name__ == "__main__":
    main()