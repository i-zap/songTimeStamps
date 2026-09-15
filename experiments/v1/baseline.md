# V1.0 Baseline Experiment

## Experiment

**Version:** V1.0
**Purpose:** Establish the first deterministic lyric-to-audio timestamp alignment baseline.

## Hypothesis

A deterministic audio-feature pipeline using RMS energy, spectral flux, onset strength, and lyric-order matching can produce useful lyric timestamps without AI models or external services.

## Input

* Audio: `song.wav`
* Audio duration: 254.133 seconds
* Sample rate: 44,100 Hz
* Lyric segments: 54
* Ground-truth segments: 54
* Lyric region: 17.15s → 233.47s

## Method

The V1.0 pipeline performs:

1. Audio loading
2. Mono conversion
3. Audio framing
4. RMS energy extraction
5. Spectral flux extraction
6. Onset-strength extraction
7. Weighted boundary-strength calculation
8. Acoustic candidate detection
9. Candidate-to-lyric matching using lyric order and estimated lyric duration
10. Alignment generation
11. LRC serialization

### Boundary-strength weights

* RMS: 0.2
* Spectral flux: 0.3
* Onset strength: 0.5

### Candidate detection

* Threshold: 0.5
* Minimum candidate spacing: 0.5 seconds

## Results

| Metric                 |  Result |
| ---------------------- | ------: |
| Predicted segments     |      54 |
| Ground-truth segments  |      54 |
| Mean absolute error    |  5.699s |
| Median absolute error  |  5.720s |
| Maximum absolute error | 11.150s |
| Within ±0.25s          |    0.0% |
| Within ±0.50s          |    0.0% |
| Within ±1.00s          |    5.6% |
| Within ±2.00s          |    5.6% |

## Observations

The acoustic candidate detector produces a large number of plausible temporal boundaries. Several detected candidates closely correspond to ground-truth lyric boundaries.

However, the current candidate-selection and lyric-order matching strategy does not reliably select the correct boundary for each lyric segment.

The results indicate that the primary limitation is not simply the absence of detected acoustic events. The mapping between lyric segments and acoustic candidates is currently too weak.

## Conclusion

The V1.0 baseline does not provide sufficiently accurate timestamp alignment for practical use.

The baseline is nevertheless considered successful as a scientific reference because it establishes:

* A deterministic alignment pipeline
* A reproducible benchmark
* A prediction artifact
* A machine-readable prediction representation
* Objective evaluation metrics
* A measurable failure baseline

## Decision

Retain V1.0 unchanged as the baseline.

Do not introduce AI or external services yet.

The next experiment should investigate stronger deterministic sequence-based matching and temporal constraints before considering substantially heavier alignment methods.

## Baseline Status

**V1.0: FAILED AS A PRACTICAL ALIGNMENT METHOD, RETAINED AS A VALID EXPERIMENTAL BASELINE.**
