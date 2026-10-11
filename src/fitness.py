from config import (CHORDS, MAJOR, PROGRESSION, N_BARS, STEPS_PER_BAR,
                    STRONG_STEPS, TONIC, W, GENOME_LEN)
from genome import decode


def _as_event_dict(ev):
    if isinstance(ev, dict):
        return ev
    if isinstance(ev, (tuple, list)) and len(ev) >= 3:
        start, dur, pitch = ev[:3]
        return {"start": start, "dur": dur, "pitch": pitch, "type": "NOTE"}
    return {"start": 0, "dur": 0, "pitch": None, "type": "REST"}


def chord_pitch_classes(bar):
   #classes de altura (0-11) do acorde do compasso 'bar'
   return {MAJOR[d] for d in CHORDS[PROGRESSION[bar]]}


def sounding_pitch_at(events, step):
    #pitch MIDI da nota soando em 'step' (start <= step < start+dur) ou None
    for ev in events:
        ev_dict = _as_event_dict(ev)
        if ev_dict.get("type") == "REST":
            continue
        start = ev_dict["start"]
        dur = ev_dict["dur"]
        if start <= step < start + dur:
            return ev_dict["pitch"]
    return None

def strong_beats(events):
    return [bar * STEPS_PER_BAR + step for bar in range(N_BARS) for step in STRONG_STEPS]


def chord_score(events):
    strong = strong_beats(events)
    hits, total = 0, 0
    for b in strong:
        total += 1
        bar = b // STEPS_PER_BAR
        pc_set = chord_pitch_classes(bar)
        p = sounding_pitch_at(events, b)
        if p is None:
            continue  # silêncio: fora do denominador
        if (p - TONIC) % 12 in pc_set:
            hits += 1
    return hits / total if total else 0.0

def jump_points(d):
   #pontuação por salto d em semitons
    if d <= 2:
        return 1.0
    if d <= 4:
        return 0.6
    if d <= 7:
        return 0.3
    return 0.0

def smooth_score(events):
    #media, sobre pares de eventos consecutivos, de uma pontuação por salto
    pitches = [
        _as_event_dict(ev)["pitch"]
        for ev in events
        if _as_event_dict(ev).get("type") != "REST"
    ]
    if len(pitches) < 2:
        return 0.0
    scores = [jump_points(abs(b - a)) for a, b in zip(pitches, pitches[1:])]
    return sum(scores) / len(scores)

def variety_score(events):
    #evita a 'nota repetida para sempre'
    pitches = [
        _as_event_dict(ev)["pitch"]
        for ev in events
        if _as_event_dict(ev).get("type") != "REST"
    ]
    if not pitches:
        return 0.0

    n_distinct = len(set(pitches))
    distinct_term = min(n_distinct, 6) / 6.0

    if len(pitches) < 2:
        repeat_term = 1.0
    else:
        repeats = sum(1 for a, b in zip(pitches, pitches[1:]) if a == b)
        repeat_term = 1.0 - repeats / (len(pitches) - 1)

    return 0.5 * (distinct_term + repeat_term)


def resolution_score(events):
    # Última nota: tônica, desde que termine no fim do genoma
    notes = [
        _as_event_dict(ev)
        for ev in events
        if _as_event_dict(ev).get("type") != "REST"
    ]

    if not notes:
        return 0.0

    last = max(notes, key=lambda ev: ev["start"] + ev["dur"])

    if last["start"] + last["dur"] != GENOME_LEN:
        return 0.0

    pc = (last["pitch"] - TONIC) % 12

    if pc == 0:
        return 1.0

    if pc in (4, 7):
        return 0.5

    return 0.0

def rhythm_score(events, genome):
    #densidade de notas razoável.
    n = len(events)
    if n == 0:
        return 0.0

    lo, hi = 16, 40
    if lo <= n <= hi:
        density = 1.0
    elif n < lo:
        density = n / lo
    else:
        # cai de 1 em hi até 0 em hi*2 (80)
        density = max(0.0, 1.0 - (n - hi) / hi)

    rest_ratio = genome.count(1) / len(genome) if genome else 0.0
    if rest_ratio <= 0.15:
        rest_penalty = 1.0
    else:
        # 0.15 -> 1 ; 0.30 -> 0
        rest_penalty = max(0.0, 1.0 - (rest_ratio - 0.15) / 0.15)

    return density * rest_penalty

    
def terms(genome):
    events = decode(genome)
    return {
        "chord":      chord_score(events),
        "smooth":     smooth_score(events),
        "variety":    variety_score(events),
        "resolution": resolution_score(events),
        "rhythm":     rhythm_score(events, genome),
    }

def fitness(genome, weights=W):
    t = terms(genome)
    return sum(weights[k] * t[k] for k in t)