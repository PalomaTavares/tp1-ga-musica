import random

from config import GENOME_LEN, HOLD, GENE_MAX, REST, degree_to_midi, gene_to_degree


def decode(genome):
    # Convert a genome into events: (start_step, duration_steps, midi_pitch).
    if not genome:
        return []

    events = []
    active_note = None  # (start_step, pitch)

    for i, g in enumerate(genome):
        if g == HOLD:
            continue

        if active_note is not None:
            start, pitch = active_note
            events.append((start, i - start, pitch))
            active_note = None

        if g != REST:
            pitch = degree_to_midi(gene_to_degree(g))
            active_note = (i, pitch)

    if active_note is not None:
        start, pitch = active_note
        events.append((start, len(genome) - start, pitch))

    return events


def random_genome(length=GENOME_LEN):
    genome = []
    for _ in range(length):
        roll = random.random()
        if roll < 0.6:
            genome.append(random.randint(2, GENE_MAX))
        elif roll < 0.8:
            genome.append(HOLD)
        else:
            genome.append(REST)
    return genome


if __name__ == "__main__":
    random.seed(0)
    genome = random_genome()
    print(genome)
    print(decode(genome))
