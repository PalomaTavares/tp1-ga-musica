import argparse
from config import *
from ga import run_ga
from genome import decode
from export import events_to_midi

p = argparse.ArgumentParser()
p.add_argument("--seed", type=int, default=SEED)
p.add_argument("--pop", type=int, default=POPULATION_SIZE)
p.add_argument("--gen", type=int, default=MAX_GENERATIONS)
p.add_argument("--crossover", default="mixed", choices=["one", "two", "mixed"])
p.add_argument("--out", default="results/run")
a = p.parse_args()

best, hist = run_ga(a.seed, a.pop, a.gen, a.crossover, log_path=a.out + ".csv")
events_to_midi(decode(best), a.out + ".mid")
print(f"seed={a.seed} gens={len(hist)} best={max(h[1] for h in hist):.3f}")