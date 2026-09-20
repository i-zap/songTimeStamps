# V1 Experiments

This directory contains the reproducible laboratory work used to investigate the V1 lyric-to-audio alignment system.

The canonical research narrative is `docs/v1/RESEARCH.md`. This README is the reproduction manual.

## Structure

```text
experiments/v1/
├── README.md
├── run.py
├── evaluate.py
├── candidate_diagnostics.py
├── matcher_diagnostics.py
├── uniform_matcher_diagnostics.py
├── candidate_scoring_diagnostics.py
├── candidate_sequence_diagnostics.py
├── data/
│   ├── song.flac
│   ├── song.wav
│   ├── lyrics.txt
│   ├── original_lyrics.txt
│   └── ground_truth.lrc
└── results/
    ├── predicted.lrc
    └── predicted.json
```

## Requirements

From `backend/`:

```bash
uv sync
```

Run the commands below from `backend/`.

## Dataset

The real-song benchmark uses the files in:

```text
experiments/v1/data/
```

Audio:

```text
Duration: 254.133s
Sample rate: 44,100 Hz
```

The benchmark contains 50 original lyric lines, 54 non-empty lyric events, and 11 timestamp-only synchronization events.

The reference LRC remains authoritative and must not be changed to improve results.

## Baseline Run

```bash
uv run python experiments/v1/run.py   experiments/v1/data/song.flac   experiments/v1/data/lyrics.txt
```

Outputs:

```text
experiments/v1/results/predicted.lrc
experiments/v1/results/predicted.json
```

## Evaluation

```bash
uv run python experiments/v1/evaluate.py   experiments/v1/data/ground_truth.lrc   experiments/v1/results/predicted.lrc
```

The evaluator measures:

- mean absolute error
- median absolute error
- maximum absolute error
- mean signed error
- percentage within ±0.25s
- percentage within ±0.50s
- percentage within ±1.00s
- percentage within ±2.00s
- per-line error

Timestamp-only synchronization events are excluded from lyric-alignment error metrics.

## Experiment 002 — Candidate Coverage

```bash
uv run python experiments/v1/candidate_diagnostics.py   experiments/v1/data/ground_truth.lrc   experiments/v1/results/predicted.json
```

Question: are useful acoustic candidates already near the reference timestamps?

Key result:

```text
Nearest-candidate MAE: 0.373s
```

This experiment is diagnostic; it does not ask the matcher to choose candidates.

## Experiment 003 — Sequence Matcher

```bash
uv run python experiments/v1/matcher_diagnostics.py   experiments/v1/data/ground_truth.lrc   experiments/v1/results/predicted.json
```

Question: can lyric order and estimated lyric duration select the correct candidate sequence?

This experiment exposed systematic sequence drift.

## Experiment 004 — Uniform Gap Matching

```bash
uv run python experiments/v1/uniform_matcher_diagnostics.py   experiments/v1/data/ground_truth.lrc   experiments/v1/results/predicted.json
```

Question: is character-length weighting causing the drift?

Observed diagnostic result:

```text
MAE: 4.985s
```

Removing character weighting improved the result but did not solve correspondence.

## Experiment 005 — Acoustic Candidate Scoring

```bash
uv run python experiments/v1/candidate_scoring_diagnostics.py   experiments/v1/data/ground_truth.lrc   experiments/v1/results/predicted.json
```

Question: can acoustic evidence refine a timestamp when its approximate region is already known?

Important: these tests use ground-truth-centered windows, so they are diagnostic and are not valid end-to-end alignment results.

Best diagnostic result:

```text
±0.25s window
MAE: 0.116s
```

## Experiment 006 — Adaptive Acoustic Sequence

```bash
uv run python experiments/v1/candidate_sequence_diagnostics.py   experiments/v1/data/ground_truth.lrc   experiments/v1/results/predicted.json
```

Question: can acoustic strength plus ordered dynamic programming solve correspondence without ground-truth-centered windows?

Observed result:

```text
MAE: 4.221s
Median error: 2.534s
Maximum error: 16.362s
```

The experiment still showed major sequence drift.

## Experiment → Research Mapping

| Experiment | Question | Conclusion |
|---|---|---|
| 001 | Can the deterministic pipeline work? | Complete pipeline works; quality is insufficient |
| 002 | Are useful candidates present? | Candidate generation is promising |
| 003 | Can temporal sequence matching select them? | Global matching drifts |
| 004 | Is character weighting the cause? | It contributes, but is not the root problem |
| 005 | Can acoustics refine a known region? | Local refinement is promising |
| 006 | Can acoustic evidence fix global matching? | Stronger audio↔lyric correspondence is required |

See `docs/v1/RESEARCH.md` for the complete reasoning chain.

## Reproducibility

When adding an experiment, preserve:

- experiment ID
- version
- Git commit
- question
- hypothesis
- method
- input data
- algorithm/configuration
- result
- failure observations
- conclusion
- decision

Preserve raw experimental evidence where practical.

## Benchmark Integrity

Do not modify `ground_truth.lrc` to improve a result.

The reference contains 11 timestamp-only synchronization events. They remain in the reference but are not V1 lyric-alignment targets.

There is an unresolved lyric-region endpoint discrepancy:

```text
benchmark metadata: 233.16s
V1 runner:          233.47s
```

Do not silently reconcile these values while reproducing historical results. Resolve them deliberately in a future benchmark cleanup.

## Current Interpretation

V1 separates the problem into:

```text
1. Detect useful audio events
        ↓
2. Determine which event corresponds to which lyric
        ↓
3. Refine the timestamp
```

V1 provides promising evidence for detection and local refinement, but the correspondence layer remains the primary unresolved problem.
