# V1 Benchmark

This directory defines the fixed benchmark used to evaluate the V1 lyric-to-audio alignment system.

The benchmark should remain stable so future versions can be compared against the same reference.

## Benchmark Identity

```text
Version: V1
Purpose: lyric-to-audio timestamp alignment
Machine-readable definition: benchmark/v1/benchmark.json
Authoritative reference: experiments/v1/data/ground_truth.lrc
```

This README documents the benchmark rules. `benchmark.json` remains machine-readable metadata.

## Dataset

```text
experiments/v1/data/
├── ground_truth.lrc
├── lyrics.txt
├── original_lyrics.txt
├── song.flac
└── song.wav
```

Audio metadata:

```text
Duration:     254.133 seconds
Sample rate:  44,100 Hz
```

Lyric/reference structure:

```text
Original lyric lines:        50
Non-empty lyric events:      54
Timestamp-only sync events:  11
Total reference events:      65
```

## Ground Truth

`ground_truth.lrc` is the authoritative reference.

It contains:

1. non-empty lyric events, which are the V1 timestamp-alignment targets
2. timestamp-only synchronization events, which are preserved reference metadata

V1 does not generate the empty synchronization events. They are therefore not counted as lyric-alignment failures.

## Evaluation Population

Timestamp accuracy is evaluated over:

```text
54 non-empty lyric events
```

The 11 timestamp-only events are excluded from lyric timestamp error calculations.

## Metrics

### Mean Absolute Error

```text
MAE = mean(abs(predicted_timestamp - reference_timestamp))
```

### Median Absolute Error

Median absolute timestamp error.

### Maximum Absolute Error

Largest absolute timestamp error.

### Mean Signed Error

```text
predicted_timestamp - reference_timestamp
```

Positive values indicate later predictions; negative values indicate earlier predictions.

### Accuracy Windows

Report the percentage of events within:

```text
±0.25s
±0.50s
±1.00s
±2.00s
```

### Candidate Coverage

Candidate coverage measures the distance between each reference timestamp and its nearest detected candidate.

It is a diagnostic of candidate generation, not final alignment quality.

## Candidate Coverage vs Final Alignment

Candidate coverage asks:

```text
reference timestamp
        ↓
nearest candidate
```

Final alignment asks:

```text
lyrics
  ↓
matcher
  ↓
selected candidate
```

These are different measurements.

V1 demonstrated that candidate coverage can be substantially better than the final matcher.

## Standardized V1 Result

The standardized V1 evaluation recorded:

```text
MAE:              5.699s
Median error:     5.722s
Maximum error:   11.150s
Within ±0.25s:     0.0%
Within ±0.50s:     0.0%
Within ±1.00s:     5.6%
Within ±2.00s:     5.6%
```

These values are the historical V1 baseline for future comparisons.

## Candidate Coverage Result

The nearest-candidate diagnostic recorded:

```text
Reference lyric events: 54
Detected candidates:    256

Mean absolute error:    0.373s
Median absolute error:  0.288s
Maximum absolute error: 2.044s

Within ±0.25s: 21/54 = 38.9%
Within ±0.50s: 43/54 = 79.6%
Within ±1.00s: 52/54 = 96.3%
Within ±2.00s: 53/54 = 98.1%
```

Largest candidate miss:

```text
Reference:        175.590s
Nearest candidate: 173.546s
Error:             -2.044s
```

## Integrity Rules

1. Never modify `ground_truth.lrc` to improve scores.
2. Never remove the 11 timestamp-only synchronization events from the reference.
3. Do not count those events as V1 lyric-alignment failures.
4. Keep the 54-event evaluation population stable unless the benchmark is deliberately versioned.
5. Preserve historical results.
6. Record algorithm and configuration changes.
7. Use the same benchmark for future versions wherever possible.
8. If the benchmark definition changes, create/version a new benchmark rather than silently changing historical data.

## Known Consistency Issue

There is an unresolved lyric-region endpoint discrepancy.

Benchmark metadata records:

```text
233.16s
```

The V1 runner currently uses:

```text
233.47s
```

Do not silently reconcile these values. Determine the authoritative value deliberately and document the decision in the research history.

The ground-truth event timestamps themselves remain unchanged.

## Reproducing the Benchmark

From `backend/`:

```bash
uv sync
```

Run V1:

```bash
uv run python experiments/v1/run.py   experiments/v1/data/song.flac   experiments/v1/data/lyrics.txt
```

Evaluate:

```bash
uv run python experiments/v1/evaluate.py   experiments/v1/data/ground_truth.lrc   experiments/v1/results/predicted.lrc
```

Candidate diagnostics:

```bash
uv run python experiments/v1/candidate_diagnostics.py   experiments/v1/data/ground_truth.lrc   experiments/v1/results/predicted.json
```

## Version Comparison

Future versions should report at least:

```text
Version
Git commit
Algorithm/configuration
MAE
Median error
Maximum error
Mean signed error
±0.25s
±0.50s
±1.00s
±2.00s
Candidate coverage
Known limitations
```

The benchmark exists to measure engineering progress, not to replace the research interpretation.

## Related Documentation

Full research narrative:

```text
docs/v1/RESEARCH.md
```

Experiment reproduction manual:

```text
experiments/v1/README.md
```
