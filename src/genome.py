import random

from config import GENOME_LEN, HOLD, MAJOR, REST, TONIC


def decode(genome):
    """Convert a genome into events: (start_step, duration_steps, midi_pitch)."""
    if not genome:
        return []

    events = []
    active_note = None  # (start_step, pitch)

    for step_index, step in enumerate(genome):
        is_hold = step == HOLD or str(step).upper() == "HOLD"
        is_rest = step == REST or str(step).upper() == "REST"
        is_pitch = not is_hold and not is_rest

        if is_pitch:
            if active_note is not None:
                start_step, current_pitch = active_note
                events.append((start_step, step_index - start_step, current_pitch))
            active_note = (step_index, step)
            continue

        if is_hold:
            if active_note is None:
                # edge case: HOLD with no open note -> acts like a rest
                continue
            continue

        if is_rest:
            if active_note is not None:
                start_step, current_pitch = active_note
                events.append((start_step, step_index - start_step, current_pitch))
                active_note = None

    if active_note is not None:
        start_step, current_pitch = active_note
        events.append((start_step, len(genome) - start_step, current_pitch))

    return events


def random_genome(length=GENOME_LEN):
    genome = []
    for _ in range(length):
        roll = random.random()
        if roll < 0.6:
            genome.append(random.choice(MAJOR) + TONIC)
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
