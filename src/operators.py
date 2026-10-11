import random
from config import (GENE_MAX, HOLD, N_BARS, P_CROSSOVER, P_MUT_GENE,
                    P_MUT_STRUCT, REST, STEPS_PER_BAR, TOURNAMENT_K, SWITCH_GEN)


def tournament_select(population, fitnesses, k=TOURNAMENT_K):
    # select k random individuals and return the index of the one with the highest fitness.
    selected_indices = random.sample(range(len(population)), k)
    best_index = max(selected_indices, key=lambda i: fitnesses[i])
    return best_index


def _one_bar_cut_point():
    bar_index = random.randint(1, N_BARS - 1)
    return bar_index * STEPS_PER_BAR


def _two_bar_cut_points():
    c1 = random.randint(1, N_BARS - 2)
    c2 = random.randint(c1 + 1, N_BARS - 1)
    return c1 * STEPS_PER_BAR, c2 * STEPS_PER_BAR


def crossover_one_point(a, b):
    point = _one_bar_cut_point()
    child1 = a[:point] + b[point:]
    child2 = b[:point] + a[point:]
    return child1, child2


def crossover_two_point(a, b):
    point1, point2 = _two_bar_cut_points()
    child1 = a[:point1] + b[point1:point2] + a[point2:]
    child2 = b[:point1] + a[point1:point2] + b[point2:]
    return child1, child2


def crossover(a, b, gen=0, mode="mixed"):
    if mode == "mixed":
        mode = "two" if gen < SWITCH_GEN else "one"
    elif mode == "mixed_random":
        mode = random.choice(("one", "two"))
    elif mode not in {"one", "two"}:
        raise ValueError(f"Unsupported crossover mode: {mode!r}")

    if random.random() >= P_CROSSOVER:
        return list(a), list(b)

    if mode == "one":
        return crossover_one_point(a, b)
    if mode == "two":
        return crossover_two_point(a, b)
    raise ValueError(f"Unsupported crossover mode: {mode!r}")

def mutate_point(g, rate=P_MUT_GENE):
    if random.random() < rate:
        choices = [HOLD, REST] + list(range(2, GENE_MAX + 1))
        return random.choice(choices)
    return g

def mutate_transpose_segment(g):
    if not g:
        return []

    start = random.randint(0, len(g) - 1)
    end = random.randint(start, len(g) - 1)
    transpose_amount = random.randint(-2, 2)
    if transpose_amount == 0:
        return list(g)

    new_g = list(g)
    for idx in range(start, end + 1):
        if new_g[idx] >= 2:
            new_g[idx] = max(2, min(GENE_MAX, new_g[idx] + transpose_amount))
    return new_g

def mutate_copy_bar(g):
    bar_length = STEPS_PER_BAR
    num_bars = N_BARS
    source_bar = random.randint(0, num_bars - 1)
    target_bar = random.randint(0, num_bars - 1)
    if source_bar == target_bar:
        return g  # No change if source and target are the same

    start_source = source_bar * bar_length
    start_target = target_bar * bar_length

    for i in range(bar_length):
        g[start_target + i] = g[start_source + i]
    return g

def mutate_reverse_bar(g):
    bar_length = STEPS_PER_BAR
    num_bars = N_BARS
    bar_index = random.randint(0, num_bars - 1)

    start = bar_index * bar_length
    end = start + bar_length

    g[start:end] = g[start:end][::-1]
    return g

def mutate(g, gen):
    g = [mutate_point(gene) for gene in g]

    # structural mutations are always available and controlled by P_MUT_STRUCT
    if random.random() < P_MUT_STRUCT:
        g = mutate_transpose_segment(g)
    if random.random() < P_MUT_STRUCT:
        g = mutate_copy_bar(g)
    if random.random() < P_MUT_STRUCT:
        g = mutate_reverse_bar(g)
    return g