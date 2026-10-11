import csv, random
from config import ELITISM, MAX_GENERATIONS, POPULATION_SIZE, STAGNATION_LIMIT, SWITCH_GEN
from fitness import fitness
from genome import random_genome
from operators import tournament_select, crossover, mutate

def run_ga(seed, pop_size=POPULATION_SIZE, max_gen=MAX_GENERATIONS, crossover_mode="mixed", weights=None, log_path=None):
    random.seed(seed)
    pop = [random_genome() for _ in range(pop_size)]
    historico = []

    best_genome = None
    best_fit = float("-inf")
    gens_sem_melhora = 0

    # quantas geracoes já passamos desde o início (para checar SWITCH_GEN)
    gen = 0

    while gen < max_gen:
        # avaliar UMA vez por geracao -----------------------------------
        if weights is None:
            fits = [fitness(g) for g in pop]
        else:
            fits = [fitness(g, weights) for g in pop]

        # estatísticas da geracao ---------------------------------------
        fit_max = max(fits)
        fit_min = min(fits)
        fit_mean = sum(fits) / len(fits)
        historico.append((gen, fit_max, fit_mean, fit_min))

        #atualiza o melhor global
        idx_best = max(range(len(pop)), key=lambda i: fits[i])
        if fits[idx_best] > best_fit:
            best_fit = fits[idx_best]
            best_genome = pop[idx_best]
            gens_sem_melhora = 0
        else:
            gens_sem_melhora += 1

        # critério de parada por estagnação 
        #    em mixed, não podemos parar antes da troca de SWITCH_GEN,
        #    senão mixed degenera para two (não chega a explorar o
        #    segundo modo de crossover).
        if gens_sem_melhora >= STAGNATION_LIMIT:
            if crossover_mode == "mixed" and gen < SWITCH_GEN:
                # não houve a troca: ignora a estagnação por ora
                pass
            else:
                break

        # se já atingimos max_gen, não precisamos gerar a próxima população
        if gen + 1 >= max_gen:
            break

        # 4. elitismo 
        order = sorted(range(len(pop)), key=lambda i: fits[i], reverse=True)
        elite_idx = order[:ELITISM]
        nova = [pop[i] for i in elite_idx]

        # 5. reproducao
        while len(nova) < pop_size:
            i1 = tournament_select(pop, fits)
            i2 = tournament_select(pop, fits)
            pai1, pai2 = pop[i1], pop[i2]

            f1, f2 = crossover(pai1, pai2, gen, crossover_mode)

            nova.append(mutate(f1, gen))
            if len(nova) < pop_size:  # evita ultrapassar em pop_size ímpar
                nova.append(mutate(f2, gen))

        #substituicao ---------------------------------------------------
        pop = nova[:pop_size]
        gen += 1

    # --- log CSV -----------------------------------------------------------
    if log_path:
        with open(log_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["gen", "max", "mean", "min"])
            for row in historico:
                w.writerow(row)

    return best_genome, historico