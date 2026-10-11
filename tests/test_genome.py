import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import CHORDS, GENE_MAX, GENOME_LEN, HOLD, MAJOR, N_BARS, PROGRESSION, REST, STEPS_PER_BAR, STRONG_STEPS, TONIC
from fitness import chord_pitch_classes, chord_score, fitness, rhythm_score, strong_beats
from ga import run_ga
from genome import decode, random_genome
from operators import crossover, mutate_point, mutate_transpose_segment, tournament_select


def test_decode_example_sequence():
    genome = [4, 0, 0, 1, 0, 6, 4]
    assert decode(genome) == [(0, 3, 60), (5, 1, 64), (6, 1, 60)]


def test_crossover_keeps_bar_boundaries_and_returns_two_children():
    random.seed(0)
    for mode in ("one", "two", "mixed"):
        for gen in (0, 500):
            for _ in range(200):
                a = random_genome()
                b = random_genome()
                c1, c2 = crossover(a, b, gen, mode)
                assert len(c1) == len(c2) == GENOME_LEN
                for bar in range(N_BARS):
                    s = slice(bar * STEPS_PER_BAR, (bar + 1) * STEPS_PER_BAR)
                    assert c1[s] in (a[s], b[s])
                    assert c2[s] in (a[s], b[s])


def test_invalid_crossover_mode_raises_value_error():
    a = random_genome()
    b = random_genome()
    with pytest.raises(ValueError):
        crossover(a, b, 0, "tow")


def test_fitness_accepts_decoded_tuple_events():
    genome = [4, 0, 0, 1, 0, 6, 4]
    score = fitness(genome)
    assert score >= 0.0
    assert score <= 1.0


def test_tournament_select_returns_an_index():
    population = [[0, 0], [1, 1], [2, 2]]
    selected = tournament_select(population, [0.1, 0.9, 0.2])
    assert selected in (0, 1, 2)


def test_run_ga_same_seed_produces_same_result():
    params = {"seed": 1, "pop_size": 12, "max_gen": 5}
    best1, hist1 = run_ga(**params)
    best2, hist2 = run_ga(**params)

    assert best1 == best2
    assert hist1 == hist2


def test_strong_beats_cover_all_bars_and_chord_score_uses_bar_offsets():
    expected = [bar * STEPS_PER_BAR + step for bar in range(N_BARS) for step in STRONG_STEPS]
    assert strong_beats([]) == expected

    events = []
    for bar in range(N_BARS):
        note = TONIC + min(chord_pitch_classes(bar))
        for step in STRONG_STEPS:
            events.append((bar * STEPS_PER_BAR + step, 1, note))

    assert chord_score(events) == 1.0


def test_rhythm_score_penalizes_excess_rest_in_genome():
    genome = [2, 3, 4] + [REST] * 40 + [2, 3, 4]
    score = rhythm_score(decode(genome), genome)
    assert score < 1.0


def test_mutate_point_can_create_hold_or_rest():
    seen = {mutate_point(2) for _ in range(2000)}
    assert HOLD in seen
    assert REST in seen


def test_mutate_transpose_segment_only_transposes_note_genes():
    genome = [HOLD, REST, 2, 3, 4, REST, 5, HOLD, 6]
    transposed = mutate_transpose_segment(genome)
    assert transposed[0] == HOLD
    assert transposed[1] == REST
    assert transposed[2] >= 2 and transposed[2] <= GENE_MAX
    assert transposed[3] >= 2 and transposed[3] <= GENE_MAX
    assert transposed[4] >= 2 and transposed[4] <= GENE_MAX
    assert transposed[5] == REST
    assert transposed[7] == HOLD
