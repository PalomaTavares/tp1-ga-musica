from midiutil import MIDIFile

from config import TEMPO
from genome import decode, random_genome

STEP_BEATS = 0.5


def events_to_midi(events, path, tempo=TEMPO):
    midi = MIDIFile(1)
    midi.addTempo(0, 0, tempo)

    for start, dur, pitch in events:
        midi.addNote(
            track=0,
            channel=0,
            pitch=pitch,
            time=start * STEP_BEATS,
            duration=dur * STEP_BEATS,
            volume=100,
        )

    with open(path, "wb") as f:
        midi.writeFile(f)


def export_random_midi(path="results/sample.mid"):
    genome = random_genome()
    events = decode(genome)
    events_to_midi(events, path)
    return genome, events


if __name__ == "__main__":
    genome, events = export_random_midi()
    print("Genome:", genome)
    print("Events:", events)
    print("Saved MIDI to results/sample.mid")