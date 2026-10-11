import argparse
import csv
import random
import shutil
import statistics as st
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
 
from export import events_to_midi
from fitness import fitness, terms
from ga import run_ga
from genome import decode, random_genome
 
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "exp"
 
# nome -> (modo de cruzamento, pesos do fitness ou None = pesos base de config.W)
CONFIGS = {
    "one":   ("one", None),
    "two":   ("two", None),
    "mixed": ("mixed", None),  # configuracao base
    "conservative": ("mixed", {"chord": 0.50, "smooth": 0.30, "variety": 0.05,
                               "resolution": 0.10, "rhythm": 0.05}),
    "adventurous":  ("mixed", {"chord": 0.20, "smooth": 0.10, "variety": 0.35,
                               "resolution": 0.10, "rhythm": 0.25}),
    "no_variety":   ("mixed", {"chord": 0.41, "smooth": 0.29, "variety": 0.0,
                               "resolution": 0.12, "rhythm": 0.18}),
}
TERM_NAMES = ["chord", "smooth", "variety", "resolution", "rhythm"]
 
 
def _run_one(job):
    """Uma rodada do GA. Funcao de topo para funcionar com ProcessPoolExecutor."""
    name, mode, weights, seed, pop, gen = job
    cfg_dir = OUT_DIR / name
    cfg_dir.mkdir(parents=True, exist_ok=True)
 
    best, hist = run_ga(seed, pop, gen, mode, weights, log_path=str(cfg_dir / f"seed{seed}.csv"))
    events = decode(best)
    events_to_midi(events, str(cfg_dir / f"seed{seed}.mid"))
 
    t = terms(best)
    row = {
        "config": name,
        "crossover": mode,
        "seed": seed,
        "gens": len(hist),
        "gen0_max": hist[0][1],
        "gen0_mean": hist[0][2],
        "final_fit": max(h[1] for h in hist),   # sob os pesos da propria config
        "fit_base": fitness(best),              # sob os pesos base: comparavel entre configs
        "n_notes": len(events),
        # velocidade de convergencia: 1a geracao com melhor fitness >= 0.95 (len(hist) se nunca)
        "gen95": next((h[0] for h in hist if h[1] >= 0.95), len(hist)),
    }
    row.update({k: t[k] for k in TERM_NAMES})
    return row
 
 
def _render_audio(rows, soundfont):
    """Renderiza 1 .wav por config escolhida (melhor seed sob os pesos base) com FluidSynth."""
    if not shutil.which("fluidsynth"):
        print("fluidsynth nao encontrado no PATH: pulei a renderizacao de audio.")
        return
    audio_dir = ROOT / "results" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    chosen = [c for c in ("mixed", "conservative", "adventurous") if any(r["config"] == c for r in rows)]
    chosen.append("baseline_random")
    for c in chosen:
        if c == "baseline_random":
            mid = OUT_DIR / "baseline_random.mid"
        else:
            best = max((r for r in rows if r["config"] == c), key=lambda r: r["fit_base"])
            mid = OUT_DIR / c / f"seed{best['seed']}.mid"
        wav = audio_dir / f"{c}.wav"
        subprocess.run(["fluidsynth", "-ni", soundfont, str(mid), "-F", str(wav), "-r", "44100"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("audio:", wav)
 
 
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seeds", type=int, default=10, help="numero de sementes por config (1..N)")
    p.add_argument("--pop", type=int, default=100)
    p.add_argument("--gen", type=int, default=300)
    p.add_argument("--configs", nargs="+", default=list(CONFIGS), choices=list(CONFIGS))
    p.add_argument("--jobs", type=int, default=1, help="processos em paralelo")
    p.add_argument("--soundfont", default=None, help="arquivo .sf2 para renderizar .wav")
    a = p.parse_args()
 
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [(n, CONFIGS[n][0], CONFIGS[n][1], s, a.pop, a.gen)
            for n in a.configs for s in range(1, a.seeds + 1)]
 
    t0 = time.time()
    if a.jobs > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            rows = list(ex.map(_run_one, jobs))
    else:
        rows = []
        for i, j in enumerate(jobs, 1):
            rows.append(_run_one(j))
            print(f"[{i}/{len(jobs)}] {j[0]} seed={j[3]} -> {rows[-1]['final_fit']:.3f}", flush=True)
 
    # baseline aleatorio (geracao 0) para audicao
    random.seed(0)
    events_to_midi(decode(random_genome()), str(OUT_DIR / "baseline_random.mid"))
 
    fields = ["config", "crossover", "seed", "gens", "gen0_max", "gen0_mean", "final_fit",
              "fit_base", "n_notes", "gen95"] + TERM_NAMES
    with open(OUT_DIR / "summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
 
    print(f"\n{len(jobs)} rodadas em {time.time() - t0:.0f}s -> {OUT_DIR / 'summary.csv'}")
    print(f"{'config':14s} {'gen0(max)':>11s} {'final':>13s} {'fit_base':>13s} {'gens':>6s} {'gen95':>6s}")
    for n in a.configs:
        r = [x for x in rows if x["config"] == n]
        ms = lambda k: (st.mean(x[k] for x in r), st.pstdev(x[k] for x in r))
        print(f"{n:14s} {ms('gen0_max')[0]:11.3f} {ms('final_fit')[0]:7.3f}±{ms('final_fit')[1]:.3f} "
              f"{ms('fit_base')[0]:7.3f}±{ms('fit_base')[1]:.3f} {ms('gens')[0]:6.0f} {ms('gen95')[0]:6.0f}")
 
    if a.soundfont:
        _render_audio(rows, a.soundfont)
 
 
if __name__ == "__main__":
    main()