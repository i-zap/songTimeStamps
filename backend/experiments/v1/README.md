# Alignment V1

V1 is the first working version of the lyric-audio alignment pipeline.

It takes an audio file and a plain-text lyric file and produces timestamped lyric alignments.

## Requirements

From the `backend/` directory, install the project dependencies:

```bash
uv sync
```

The project uses `uv` to manage the Python environment and dependencies.

## Input Files

V1 expects the input files to be inside:

```text
experiments/v1/data/
```

Example:

```text
experiments/v1/
├── data/
│   ├── song.wav
│   └── lyrics.txt
└── run.py
```

The lyrics file must contain one lyric line per line.

Example:

```text
Ameagari no niji mo
Rin to saita hana mo
Irodzuki afuredasu
Akaneiro no sora aogu kimi ni
```

## Running V1

From the `backend/` directory:

```bash
uv run python experiments/v1/run.py experiments/v1/data/song.wav experiments/v1/data/lyrics.txt
```

The program prints:

* Audio duration
* Audio sample rate
* Number of lyric lines
* Number of generated alignments
* Start and end timestamp for each lyric line

Example:

```text
Audio duration: 254.133s
Audio sample rate: 44100
Lyric lines: 50
Alignments: 50

   3.471s →    3.843s | 000 | Ameagari no niji mo
   3.843s →    4.040s | 001 | Rin to saita hana mo
   ...
```

## What V1 Does

The V1 pipeline currently performs:

1. Audio loading
2. Stereo-to-mono conversion
3. Audio framing
4. RMS calculation
5. Spectral-flux calculation
6. Onset-strength calculation
7. Boundary-strength calculation
8. Candidate timestamp detection
9. Candidate-to-lyric matching
10. Alignment result generation

## Validation

Before considering V1 complete, run:

```bash
uv run pytest
```

Then:

```bash
uv run ruff check .
```

Then:

```bash
uv run ruff format --check .
```

All three checks should pass.

## V1 Status

V1 is the first end-to-end working alignment model.

The implementation is intentionally simple. Its purpose is to establish a clean and testable alignment pipeline before introducing more advanced alignment techniques.

## Important

The V1 runner only accepts input files located inside:

```text
experiments/v1/data/
```

This keeps the experiment inputs contained and prevents arbitrary filesystem paths from being used by the runner.
