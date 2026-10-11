POPULATION_SIZE = 30
# POPULATION_SIZE = 70
# POPULATION_SIZE = 100
# POPULATION_SIZE = 120
# POPULATION_SIZE = 150

HOLD, REST = 0, 1
LOW_DEGREE = -2
HIGH_DEGREE = 9
N_PITCHES = HIGH_DEGREE - LOW_DEGREE + 1
GENE_MAX = 2 + N_PITCHES - 1
TOURNAMENT_K = 3
ELITISM = 2
SEED = 0
STAGNATION_LIMIT = 40

MAX_GENERATIONS = 300

TONIC = 60
MAJOR = [0, 2, 4, 5, 7, 9, 11]
# --- Forma e grade rítmica ---
N_BARS = 8
STEPS_PER_BAR = 8  # colccheias em 4/4
GENOME_LEN = N_BARS * STEPS_PER_BAR  # 64 genes
TEMPO = 100

# --- Progressão (um acorde por compasso) ---
# Acordes como conjuntos de graus (0 = Dó, ..., 6 = Si), comparados com d % 7
CHORDS = {
    "I": {0, 2, 4},   # C  E G
    "vi": {5, 0, 2},  # A  C E
    "IV": {3, 5, 0},  # F  A C
    "V": {4, 6, 1},   # G  B D
}
PROGRESSION = ["I", "vi", "IV", "V", "I", "vi", "V", "I"]


P_CROSSOVER = 0.8          # prob. de cruzar um par (senão, filhos = cópias dos pais)
P_MUT_GENE = 0.02          # por gene (mutações pontuais)
P_MUT_STRUCT = 0.15        # por indivíduo (mutações estruturais)
CROSSOVER_MODE = "mixed"   # "one", "two" ou "mixed"
SWITCH_GEN = 100           # geração em que o "mixed" troca de 2 pontos para 1 ponto

W = {"chord": 0.35, "smooth": 0.25, "variety": 0.15, "resolution": 0.10, "rhythm": 0.15}  # soma = 1
STRONG_STEPS = (0, 4)   # tempos fortes dentro do compasso (colcheias em 4/4)

def degree_to_midi(degree):
    return TONIC + 12 * ( degree // 7 ) + MAJOR[degree % 7]

def gene_to_degree(gene):
    return gene  - 2 + LOW_DEGREE  # gene 2 = degree 0 (C), gene 3 = degree 1 (D), etc.