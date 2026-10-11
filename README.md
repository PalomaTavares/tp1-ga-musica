# tp1-ga-musica
Projeto desenvolvido para a disciplina de IA em Música da UFMG.

## Requisitos
- Python 3.10+
- Ambiente virtual recomendado

## Instalações:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Como rodar
No terminal, na raiz do projeto:
python -m venv .venv
source .venv/bin/activate

## Gerar uma melodia

```bash
python src/run.py --seed 1 --pop 100 --gen 300 --crossover mixed --out results/exemplo
```

Gera `results/exemplo.mid` (melodia) e `results/exemplo.csv` (fitness por geração).
Opções: `--seed`, `--pop`, `--gen`, `--crossover {one,two,mixed}`, `--out`.

## Reproduzir os resultados do resumo

```bash
python src/experiments.py --seeds 10 --pop 100 --gen 300 --jobs 4
python src/plot.py
python pick_midis.py
```

## Opções do script
- `--seed`: semente aleatória
- `--pop`: tamanho da população
- `--gen`: número de gerações
- `--crossover`: `one`, `two` ou `mixed`
- `--out`: prefixo dos arquivos de saída

- `experiments.py`: 6 configurações × 10 sementes → `results/exp/` (curvas, `.mid`, `summary.csv`).
- `plot.py`: gráficos e tabela → `results/figures/`.
- `pick_midis.py`: copia as melodias citadas no resumo → `results/midi/`.

As sementes são fixas, então os mesmos comandos reproduzem os mesmos resultados.

Os áudios do repositório estão em `results/audio/`. Para gerá-los a partir dos MIDI
(requer FluidSynth e um soundfont `.sf2`):

```bash
mkdir -p results/audio
for f in results/midi/*.mid; do
  fluidsynth -ni caminho/do/soundfont.sf2 "$f" -F "results/audio/$(basename "${f%.mid}").wav" -r 44100
done
```

## Uso de IA

Instalação de bibliotecas python: https://chatgpt.com/share/6ac563cb-891c-83e8-91ba-9765eaa1aa6b

Funções auxiliares de conversão: https://chatgpt.com/c/6ac6c9ad-25d8-83e8-a54c-15ef84d6ce4c

Dúvidas de código: https://chatgpt.com/share/6ac80827-7150-83e8-8efd-4181c4fb8f54

Diversos prompts foram usados para fazer correçõe no código pelo copilot, mas não consegui compartilhá-los