\# SongTimeStamps — V1 Research

\## 1. Purpose

V1 is the first research and engineering phase of the SongTimeStamps lyric-to-audio alignment system.

The objective of V1 was not to achieve perfect timestamp alignment.

The objective was to build the smallest useful, deterministic, understandable, and testable alignment system and use it to discover where the real problem lies.

The intended workflow is:

\`\`\`text

Audio + Lyrics

      ↓

Audio analysis

      ↓

Acoustic features

      ↓

Candidate timestamps

      ↓

Lyric-to-audio matching

      ↓

Alignment objects

      ↓

LRC

\`\`\`

V1 therefore serves two purposes:

1\. Establish a functioning alignment architecture.

2\. Produce reliable experimental knowledge for future versions.

V1 is not disposable. Its implementation, benchmark, experiments, failures, and decisions are part of the project's accumulated knowledge.

\---

\# 2. Core V1 Philosophy

\## Lightweight first

V1 intentionally avoids large AI models, external AI APIs, cloud services, vector databases, and unnecessary infrastructure.

The first question is always:

\> Can a smaller deterministic method solve the problem?

A heavier method should only be introduced when experimental evidence shows that the current approach has reached a meaningful limitation.

\## Local-first

The long-term system should be capable of processing audio locally.

The audio itself should not need to be uploaded to an external service merely to generate timestamps.

\## AI only when necessary

AI is not considered the default solution.

Classical signal processing, deterministic algorithms, and domain-specific methods should be explored first.

\## Prototype before optimization

V1 exists to answer:

\> Can we build the complete pipeline and understand where it fails?

It does not exist to produce a production-quality result immediately.

\## Preserve knowledge

A failed experiment is still useful if it tells us what assumption was wrong.

Future versions should inherit:

\* working components

\* benchmarks

\* experiments

\* failures

\* observations

\* architectural decisions

\* limitations

V2 should therefore compare itself against V1 instead of simply replacing it.

\---

\# 3. Versioning Strategy

The project uses Git to preserve the evolution of the system.

The intended hierarchy is:

\`\`\`text

V1

 ├── V1.0

 ├── V1.x

 │

 ↓

V2

 ├── V2.0

 ├── V2.x

 │

 ↓

V3

\`\`\`

A minor version represents an improvement that remains within the same fundamental architecture.

A major version represents a meaningful architectural change.

The project should preserve completed versions through Git branches and tags so that historical versions remain reproducible.

The latest stable release remains on \`main\`.

Experimental work may use feature branches when the work is substantial enough to warrant one.

\---

\# 4. V1 Architecture

The V1 system is divided into several conceptual layers.

\`\`\`text

                    AUDIO

                      │

                      ▼

              Audio preprocessing

                      │

                      ▼

              Feature extraction

                      │

                      ▼

               Feature timeline

                      │

                      ▼

              Boundary strength

                      │

                      ▼

             Candidate detection

                      │

                      ▼

              Lyric matching

                      │

                      ▼

               Alignments

                      │

                      ▼

                    LRC

\`\`\`

The important architectural decision is that these stages remain separate.

The system should not collapse audio processing, matching, and LRC generation into one opaque function.

This allows each stage to be tested independently and makes failures easier to diagnose.

\---

\# 5. Domain Layer

The domain layer was established before the alignment experiments.

It contains models representing the concepts used by the alignment system.

\## LyricLine

Represents one lyric line.

It contains:

\* UUID

\* line index

\* lyric text

The original text is preserved exactly.

Normalization or matching representations should be handled separately from the original lyric text.

\## LyricDocument

Represents a lyric document.

It contains:

\* UUID

\* language

\* role

\* collection of lyric lines

Supported roles are:

\* \`original\`

\* \`romanized\`

\* \`translation\`

The model is intentionally capable of representing multiple lyric layers.

For example:

\`\`\`text

Japanese original

Romanized Japanese

English translation

\`\`\`

These documents do not have to contain identical line counts.

\## LyricReference

Connects an alignment to a specific lyric line and document.

This allows alignment objects to refer back to the original lyric structure without duplicating lyric text.

\## Alignment

Represents the relationship between an audio interval and one or more lyric references.

It contains:

\* UUID

\* audio start

\* audio end

\* lyric references

\* confidence

\* method

An important architectural principle is:

\> Timestamp information belongs to the alignment, not to the lyric line itself.

This allows future versions to support more complex relationships between audio and lyrics.

\---

\# 6. Evidence Model

V1 also established an evidence model.

The system should eventually be able to answer:

\> Why did the system place this lyric here?

The evidence architecture contains:

\## EvidenceItem

Represents an individual piece of evidence.

It contains:

\* name

\* score

\* source

\* additional details

\## LocalAlignmentEvidence

Stores evidence associated with a specific alignment.

\## GlobalAlignmentEvidence

Stores evidence concerning the alignment as a whole.

\## AlignmentResult

Combines:

\* alignment IDs

\* local evidence

\* global evidence

This structure is intentionally retained for future versions.

Confidence should not be treated as proof of correctness.

Confidence is an algorithmic estimate.

Ground-truth evaluation remains a separate measurement.

\---

\# 7. Audio Representation

V1 uses a lightweight audio representation.

Audio is loaded as floating-point samples.

The representation contains:

\* sample rate

\* samples

\* channel count

\* duration

Audio is loaded into a consistent 2D representation so that mono and multi-channel input can be handled consistently.

Audio loading was implemented using \`soundfile\`.

\---

\# 8. Audio Preprocessing

The audio-processing pipeline begins with preprocessing.

The main steps are:

\`\`\`text

Audio

 ↓

Channel handling

 ↓

Mono representation

 ↓

Framing

 ↓

Feature extraction

\`\`\`

Stereo and multi-channel audio are converted to mono before feature extraction.

This keeps the feature pipeline simple and deterministic.

The preprocessing stage was tested independently.

\---

\# 9. Audio Framing

The audio is divided into overlapping frames.

The framing stage provides the temporal resolution needed by subsequent feature extraction.

The frame size and hop size are configurable.

The resulting representation associates extracted features with positions in time.

\---

\# 10. Feature Timeline

A structured feature timeline was introduced rather than passing unrelated arrays throughout the system.

Each feature frame is associated with a timestamp.

The V1 timeline contains:

\* timestamp

\* RMS

\* spectral flux

\* onset strength

Conceptually:

\`\`\`text

time      RMS      flux      onset

\------------------------------------

0.00      ...       ...       ...

0.02      ...       ...       ...

0.04      ...       ...       ...

...

\`\`\`

This became an important architectural decision.

Future versions can add additional features without abandoning the temporal representation.

\---

\# 11. RMS Energy

RMS energy provides a lightweight measurement of signal energy within each frame.

It gives the system information about changes in audio intensity.

RMS alone is insufficient for lyric alignment, but it provides useful supporting evidence.

\---

\# 12. Spectral Flux

Spectral flux measures changes in the frequency distribution between consecutive frames.

It provides another indication of transitions and acoustic events.

Spectral flux was tested independently using synthetic changes in spectral content.

\---

\# 13. Onset Strength

Onset strength provides an additional indication of musical events.

The intention is to detect moments where the audio changes strongly enough to represent potentially useful boundaries.

Onset strength became the strongest component of the initial boundary-strength signal.

\---

\# 14. Boundary Strength

V1 combines the extracted features into one boundary-strength signal.

The current weights are:

\`\`\`text

RMS             0.2

Spectral flux   0.3

Onset strength  0.5

\`\`\`

The resulting conceptual model is:

\`\`\`text

Boundary strength =

    0.2 × RMS

  \+ 0.3 × spectral flux

  \+ 0.5 × onset

\`\`\`

The features are normalized before combination.

This is a deterministic heuristic, not a learned model.

\---

\# 15. Candidate Detection

Candidate detection identifies timestamps that appear acoustically significant.

The detector searches for local peaks above a configurable threshold while enforcing a minimum spacing between candidates.

Current V1 settings used:

\`\`\`text

Threshold:       0.5

Minimum spacing: 0.5 seconds

\`\`\`

The intermediate representation is:

\`\`\`text

Audio

  ↓

Acoustic features

  ↓

Boundary strength

  ↓

Candidate timestamps

\`\`\`

This separation turned out to be extremely important during later experiments.

\---

\# 16. V1 Real-Song Benchmark

A real-song benchmark was created to evaluate the system against known timestamps.

The benchmark contains:

\`\`\`text

Audio duration:      254.133 seconds

Sample rate:         44,100 Hz

Original lyric lines: 50

Reference lyric events: 54

\`\`\`

The reference LRC contains:

\* 54 non-empty lyric events

\* 11 timestamp-only synchronization events

The timestamp-only events are treated as synchronization metadata rather than lyric-alignment targets for V1.

They are therefore not counted as V1 lyric-alignment failures.

The non-empty lyric events form the primary alignment benchmark.

The benchmark is intended to remain reusable across future versions.

\---

\# 17. Benchmark Data

The benchmark includes:

\`\`\`text

experiments/v1/data/

├── ground\_truth.lrc

├── lyrics.txt

├── original\_lyrics.txt

├── song.flac

└── song.wav

\`\`\`

The ground-truth LRC remains the authoritative reference artifact for the experiment.

It should not be modified simply to make an algorithm appear more successful.

\---

\# 18. Benchmark Consistency Note

There is currently a small metadata discrepancy that must remain explicitly documented until resolved.

The benchmark metadata records the lyric region ending at:

\`\`\`text

233.16s

\`\`\`

while the later V1 experiment runner uses:

\`\`\`text

233.47s

\`\`\`

This difference has not been silently reconciled.

Future benchmark cleanup should determine which value is authoritative and update the relevant metadata consistently.

Until that is resolved, comparisons involving the lyric-region endpoint should identify which artifact/configuration was used.

The ground-truth timestamp events themselves should remain unchanged.

\---

\# 19. Experiment 001 — Deterministic V1 Baseline

\## Question

Can a deterministic acoustic-feature pipeline produce useful lyric timestamps without AI models or external services?

\## Hypothesis

RMS energy, spectral flux, onset strength, and lyric-order matching should be sufficient to establish a useful first alignment baseline.

\## Method

The pipeline performs:

1\. Audio loading

2\. Mono conversion

3\. Audio framing

4\. RMS extraction

5\. Spectral flux extraction

6\. Onset-strength extraction

7\. Boundary-strength calculation

8\. Candidate detection

9\. Lyric-order matching

10\. Alignment construction

11\. LRC serialization

\## Result

The first real-song baseline produced 54 reference-length lyric events but selected incorrect timestamps.

The later standardized evaluation recorded:

\`\`\`text

MAE:              5.699s

Median error:     5.720s

Maximum error:   11.150s

Within ±0.25s:     0.0%

Within ±0.50s:     0.0%

Within ±1.00s:     5.6%

Within ±2.00s:     5.6%

\`\`\`

\## Observation

The system successfully performed the complete computational workflow, but the timestamps were not practically useful.

The initial failure demonstrated that:

\> A structurally correct alignment pipeline is not necessarily a temporally correct alignment pipeline.

\## Decision

Keep the deterministic architecture.

Do not introduce AI yet.

Investigate the candidate and matching stages independently.

\---

\# 20. Experiment 002 — Candidate Coverage

\## Question

Are correct lyric boundaries actually present among the acoustic candidates?

This experiment separates candidate detection from candidate selection.

If candidates are already near the ground-truth timestamps, then improving feature detection is not the primary solution.

\## Method

For every non-empty ground-truth lyric event, find the nearest detected acoustic candidate.

The experiment does not ask the matcher to select the candidate.

It only asks:

\> How close is the nearest candidate?

\## Result

\`\`\`text

Reference lyric events: 54

Detected candidates:    256

Mean absolute error:    0.373s

Median absolute error:  0.288s

Maximum absolute error: 2.044s

\`\`\`

Coverage:

\`\`\`text

Within ±0.25s: 21/54  = 38.9%

Within ±0.50s: 43/54  = 79.6%

Within ±1.00s: 52/54  = 96.3%

Within ±2.00s: 53/54  = 98.1%

\`\`\`

The significant poorly covered case was:

\`\`\`text

Ground truth: 175.590s

Nearest candidate: 173.546s

Error: -2.044s

\`\`\`

\## What We Learned

This was one of the most important V1 discoveries.

The candidate detector is not perfect.

However, many correct lyric boundaries already have reasonably close candidates.

Therefore:

\> Candidate generation is not the primary bottleneck.

The much larger problem is deciding **\*\*which candidate belongs to which lyric\*\***.

\## Decision

Retain candidate detection as a useful intermediate stage.

Do not spend the next version endlessly tuning candidate detection before investigating lyric-to-candidate correspondence.

\---

\# 21. Experiment 003 — Current Sequence Matcher

\## Question

Can lyric ordering and estimated lyric duration select the correct candidate sequence?

\## Hypothesis

Lyrics occur in order, and longer lyric lines should generally occupy more temporal space.

Therefore a dynamic-programming sequence matcher can select candidates using:

\* lyric order

\* lyric length

\* expected positions

\* expected gaps

\## Method

The matcher assigns weights to lyric lines based on normalized character length.

It then estimates expected lyric positions across the selected lyric region and performs ordered candidate selection using dynamic programming.

\## Result

The standardized experiment recorded:

\`\`\`text

MAE:              5.699s

Median error:     5.722s

Maximum error:   11.150s

Within ±0.25s:     0.0%

Within ±0.50s:     0.0%

Within ±1.00s:     5.6%

Within ±2.00s:     5.6%

\`\`\`

Matcher diagnostics also showed that the matcher frequently selected candidates much worse than the nearest available candidate.

In one diagnostic:

\`\`\`text

Nearest-candidate MAE: 0.373s

Matcher-selected MAE: 3.997s

\`\`\`

The exact matcher diagnostic output depends on the prediction artifact used, so this value should be treated as an experiment-specific diagnostic rather than the final standardized V1 benchmark score.

\## What We Learned

The candidates themselves contain useful temporal information, but the global sequence model does not know which candidate corresponds to which lyric.

The matcher can make a locally plausible choice that causes a sequence-level drift.

Once that drift begins, later lyric timestamps can move increasingly far from the correct positions.

\## Decision

Do not treat the current global DP formulation as the V2 foundation.

Investigate why the correspondence problem exists instead of merely increasing or decreasing its weights.

\---

\# 22. Experiment 004 — Uniform Gap Matching

\## Question

Is lyric-character weighting itself causing the systematic drift?

The previous matcher assumes that character count is related to sung duration.

That assumption may be weak.

For example:

\`\`\`text

Long text ≠ necessarily long sung duration

Short text ≠ necessarily short sung duration

\`\`\`

\## Hypothesis

Removing character-based duration weighting and using a simpler temporal assumption may reduce systematic bias.

\## Result

\`\`\`text

MAE:              4.985s

Median error:     4.459s

Maximum error:   13.232s

Within ±0.25s:     3.7%

Within ±0.50s:     7.4%

Within ±1.00s:    11.1%

Within ±2.00s:    24.1%

\`\`\`

Compared with the current sequence matcher, this was an improvement.

However, it remained dramatically worse than the nearest-candidate baseline.

\## What We Learned

Character-length weighting contributes to the error.

But removing it does not solve the underlying correspondence problem.

The fundamental problem is therefore not simply:

\`\`\`text

"Which lyric-length formula should we use?"

\`\`\`

It is:

\`\`\`text

"How do we determine which acoustic event corresponds to this lyric?"

\`\`\`

\## Decision

Stop treating lyric-length weighting as the primary solution.

\---

\# 23. Experiment 005 — Acoustic Candidate Scoring

\## Question

Can acoustic boundary strength identify the correct timestamp once we know approximately where a lyric begins?

\## Method

For each ground-truth timestamp, candidates were examined within controlled windows.

The strongest acoustic candidate was selected.

Important:

\> These experiments use the ground-truth timestamp to center the search window.

Therefore they are **\*\*diagnostic experiments\*\***, not valid end-to-end alignment algorithms.

\## Results

\### ±0.25 second window

\`\`\`text

MAE:              0.116s

Median:           0.104s

Within ±0.50s:   100.0%

Within ±1.00s:   100.0%

\`\`\`

\### ±0.50 second window

\`\`\`text

MAE:              0.299s

Median:           0.371s

Within ±0.50s:   100.0%

Within ±1.00s:   100.0%

\`\`\`

\### ±1.00 second window

\`\`\`text

MAE:              0.519s

Median:           0.483s

Within ±0.50s:    51.9%

Within ±1.00s:   100.0%

\`\`\`

\### ±1.50 second window

\`\`\`text

MAE:              0.823s

Median:           0.751s

Within ±0.50s:    28.3%

Within ±1.00s:    64.2%

\`\`\`

\### ±2.00 second window

\`\`\`text

MAE:              1.123s

Median:           1.252s

Within ±0.50s:    18.9%

Within ±1.00s:    45.3%

\`\`\`

\## What We Learned

This experiment revealed a valuable property of the acoustic representation.

When the search region is already reasonably close to the true lyric boundary, acoustic information can refine the timestamp substantially.

Therefore:

\`\`\`text

Acoustic features

        ↓

Poor at establishing correspondence globally

        ↓

Potentially useful for local timestamp refinement

\`\`\`

This is an important distinction.

\## Decision

Retain acoustic boundary strength as a **\*\*local refinement signal\*\***.

Do not use it as the sole global lyric-to-audio correspondence mechanism.

\---

\# 24. Experiment 006 — Adaptive Acoustic Sequence Matching

\## Question

Can strong acoustic candidates plus ordered dynamic programming solve the correspondence problem without ground-truth-centered windows?

\## Method

The same candidate set was used.

The matcher was given:

\* weak timing information

\* candidate ordering

\* acoustic boundary strength

\* sequence constraints

No ground-truth-centered local window was used.

\## Result

\`\`\`text

MAE:              4.221s

Median error:     2.534s

Maximum error:   16.362s

Mean signed error: -2.851s

Within ±0.25s:     7.4%

Within ±0.50s:    13.0%

Within ±1.00s:    22.2%

Within ±2.00s:    42.6%

\`\`\`

The per-line diagnostics showed major sequence drift.

Examples included:

\`\`\`text

Line 002

GT:       23.230s

Selected: 29.907s

Error:    +6.677s

Line 007

GT:       46.870s

Selected: 52.222s

Error:    +5.352s

Line 034

GT:      162.960s

Selected: 153.472s

Error:    -9.488s

Line 038

GT:      181.530s

Selected: 165.849s

Error:   -15.681s

Line 039

GT:      184.660s

Selected: 168.298s

Error:   -16.362s

\`\`\`

\## What We Learned

Adding acoustic evidence to the global DP does not solve the problem.

The matcher still lacks a sufficiently strong representation of the relationship between:

\`\`\`text

actual sung audio

        ↕

specific lyric

\`\`\`

The acoustic signal can identify musical events, but it cannot reliably identify which lyric is being sung at those events.

\## Decision

Do not continue endlessly tuning the same global DP formulation.

The next architecture must introduce a stronger representation of audio content and lyric content.

\---

\# 25. V1 Candidate-Matching Conclusion

The experiments allow the V1 candidate problem to be separated into two distinct questions.

\## Question A — Can we detect useful acoustic boundaries?

To a useful degree, yes.

The nearest-candidate baseline achieved:

\`\`\`text

MAE: 0.373s

Median: 0.288s

±0.50s: 79.6%

±1.00s: 96.3%

\`\`\`

This is not perfect candidate coverage, but it demonstrates that the audio pipeline is producing useful temporal information.

\## Question B — Can we determine which candidate corresponds to which lyric?

The current approaches did not solve this.

Global sequence matching produced errors several seconds larger than the nearest-candidate baseline.

Therefore:

\> **\*\*Candidate generation is sufficiently useful to retain, while candidate-to-lyric selection requires a fundamentally stronger signal.\*\***

This is the central V1 research conclusion.

\---

\# 26. What V1 Actually Discovered

The most important discovery is that the alignment problem contains at least three different tasks.

\`\`\`text

1\. Detect interesting audio events

              ↓

2\. Determine which event corresponds to which lyric

              ↓

3\. Refine the exact timestamp

\`\`\`

V1 has partial evidence for all three.

\### Task 1 — Detection

Reasonably promising.

\### Task 2 — Correspondence

Currently unsolved.

\### Task 3 — Refinement

Promising when a sufficiently accurate local region is already known.

This means the future architecture should not force one algorithm to solve all three problems simultaneously.

\---

\# 27. The Fundamental V1 Failure

The current pipeline effectively asks:

\`\`\`text

Audio

 ↓

musical boundaries

 ↓

guess which lyric belongs to each boundary

\`\`\`

The missing information is the actual relationship between audio content and lyric content.

Acoustic energy and onset information can tell us:

\> Something happened here.

They cannot reliably tell us:

\> This is the beginning of "Kimi da yo kimi nanda yo."

That requires richer information about the audio itself.

\---

\# 28. What We Should NOT Do

\## Do not add arbitrary offsets

For example:

\`\`\`text

timestamp + 17 seconds

\`\`\`

is not a solution.

\## Do not use magic scaling factors

For example:

\`\`\`text

timestamp × constant

\`\`\`

is not a general alignment method.

\## Do not endlessly tune DP weights

Changing:

\`\`\`text

0.2

0.3

0.5

\`\`\`

does not solve missing information.

\## Do not declare success from ground-truth-centered experiments

A local refinement experiment centered around the true timestamp is useful diagnostically, but it is not an end-to-end algorithm.

\## Do not throw away the V1 pipeline

The acoustic representation and candidate detector remain useful components.

\---

\# 29. V1 Components to Preserve

The following should be inherited by future versions.

\`\`\`text

Domain models

        ↓

Audio loading

        ↓

Preprocessing

        ↓

Feature extraction

        ↓

Feature timeline

        ↓

Boundary strength

        ↓

Candidate detection

        ↓

Alignment structures

        ↓

Evidence model

        ↓

Evaluation framework

        ↓

Tests

\`\`\`

The current candidate-selection strategy is the component that should be reconsidered.

\---

\# 30. V1 Components That Need Improvement

The primary weak point is:

\`\`\`text

candidate timestamps

        ↓

candidate-to-lyric correspondence

\`\`\`

The current matcher relies too heavily on:

\* lyric order

\* estimated lyric duration

\* temporal spacing

\* acoustic boundary strength

These signals are insufficient by themselves.

\---

\# 31. V1 Local Refinement Insight

The local acoustic experiments suggest a potentially useful future architecture:

\`\`\`text

Approximate lyric region

        ↓

candidate search

        ↓

acoustic scoring

        ↓

timestamp refinement

\`\`\`

This is more promising than asking acoustic features to solve the entire song globally.

Therefore future versions should consider a coarse-to-fine alignment architecture.

\---

\# 32. Proposed V2 Research Direction

V2 should investigate a fundamentally different question:

\> Can we build a representation that captures information about the actual sung audio and compare it with the supplied lyrics?

The conceptual architecture becomes:

\`\`\`text

                         AUDIO

                           │

                           ▼

                  Audio representation

                           │

                           │

                           ▼

                    ┌─────────────┐

                    │   MATCHER   │

                    └─────────────┘

                           ▲

                           │

                           │

                  Lyric representation

                           ▲

                           │

                         LYRICS

\`\`\`

The important change is that the matcher should compare:

\`\`\`text

audio content

      ↕

lyric content

\`\`\`

rather than:

\`\`\`text

candidate position

      ↕

estimated lyric position

\`\`\`

\---

\# 33. V2 Principle — Build Our Own Matcher First

V2 should remain local-first.

No external AI API is required.

No cloud processing is required.

No large pretrained model should be introduced merely because it exists.

The first goal is to investigate whether a specialized alignment system can be constructed from smaller components.

The project is not trying to build a general-purpose speech recognizer.

The actual problem is narrower:

\> Given known lyrics and audio, determine where those lyrics occur in the song.

This distinction is central to the project's architecture.

\---

\# 34. V2 Research Should Be Incremental

V2 should not immediately become a giant machine-learning project.

The intended progression is:

\`\`\`text

V2.0

Audio representation

        ↓

V2.1

Lyric representation

        ↓

V2.2

Similarity / correspondence

        ↓

V2.3

Sequence alignment

        ↓

V2.4

Local refinement

        ↓

V2.x

Learned components if necessary

\`\`\`

Each stage should be independently evaluated.

If a simpler method works, there is no reason to replace it with a larger one.

\---

\# 35. Potential V2 Audio Representation

The existing representation can be expanded gradually.

Current:

\`\`\`text

RMS

Spectral flux

Onset strength

\`\`\`

Potential future signals include:

\`\`\`text

Spectral centroid

Spectral bandwidth

Spectral contrast

Zero-crossing rate

Mel-frequency representation

Harmonic information

Vocal activity

Other temporal acoustic features

\`\`\`

These should not all be added at once.

Each additional signal should answer a specific research question.

\---

\# 36. Potential V2 Lyric Representation

The original lyric text must remain untouched.

A separate representation can eventually capture properties useful for matching.

Potential representations include:

\`\`\`text

Normalized text

Phonetic representation

Syllable structure

Vowel sequence

Consonant structure

Language-specific pronunciation

\`\`\`

The representation should support multilingual lyrics.

The system should not assume that:

\`\`\`text

one lyric line = one audio event

\`\`\`

Future alignment must be capable of representing:

\`\`\`text

1 → 1

1 → N

N → 1

N → N

\`\`\`

between lyric structures and audio segments.

\---

\# 37. Learning Should Come Later

A learned model may eventually be useful.

However, it should only be introduced after the deterministic representation has been understood.

A future learning formulation could look conceptually like:

\`\`\`text

Correct audio/lyric pair

        ↓

       positive

Incorrect audio/lyric pair

        ↓

       negative

              ↓

       Alignment model

              ↓

       similarity score

\`\`\`

The goal would not be to train a general lyric-generation system.

The goal would be to train a specialized model that learns:

\> What does a correctly aligned audio/lyric pair look like?

This keeps the learning problem focused.

\---

\# 38. V1 Evaluation Principles

Future versions should use the same benchmark wherever possible.

Useful metrics include:

\* Mean absolute timestamp error

\* Median absolute error

\* Maximum error

\* Mean signed error

\* Percentage within ±0.25s

\* Percentage within ±0.50s

\* Percentage within ±1.00s

\* Percentage within ±2.00s

\* Candidate coverage

\* Alignment coverage

\* Sequence correctness

\* Confidence calibration

A model's confidence should not be treated as ground truth.

Evaluation must remain separate.

\---

\# 39. Failure Severity

Future experiments should distinguish between minor and major failures.

A useful conceptual scale is:

\`\`\`text

Level 0 — negligible

Level 1 — minor

Level 2 — noticeable

Level 3 — significant

Level 4 — major

Level 5 — catastrophic

\`\`\`

The purpose is not to create bureaucracy.

The purpose is to make it obvious which failures actually require architectural changes.

\---

\# 40. Reproducibility

An experiment should preserve enough information to reproduce its result.

Important evidence includes:

\`\`\`text

Experiment ID

Version

Git commit

Audio identity/fingerprint

Audio metadata

Lyric identity/hash

Algorithm version

Configuration

Feature configuration

Candidate configuration

Predicted output

Evaluation metrics

Failure observations

Conclusion

Decision

\`\`\`

The project should preserve raw experimental evidence where practical.

Copyrighted audio should not be distributed in the repository unless the project has permission to do so.

Local benchmark audio can remain excluded from public distribution when necessary.

\---

\# 41. Current V1 Project State

At the end of the V1 research phase:

\`\`\`text

Domain layer                 COMPLETE

Audio loading                FUNCTIONAL

Preprocessing                FUNCTIONAL

Feature extraction           FUNCTIONAL

Feature timeline             FUNCTIONAL

Candidate detection          FUNCTIONAL

Alignment construction       FUNCTIONAL

Evidence model               FUNCTIONAL

Testing                      PASSING

Linting                      PASSING

Formatting                   PASSING

End-to-end pipeline          FUNCTIONAL

Practical alignment quality  INSUFFICIENT

Candidate generation         PROMISING

Global candidate matching    INSUFFICIENT

Local acoustic refinement    PROMISING

\`\`\`

\---

\# 42. V1 Final Assessment

V1 is considered a **\*\*successful experimental foundation\*\*** but an **\*\*unsuccessful practical alignment method\*\***.

This distinction is intentional.

V1 successfully established:

\* a modular alignment architecture

\* a deterministic audio pipeline

\* structured domain models

\* temporal feature representation

\* acoustic candidate generation

\* alignment construction

\* evidence structures

\* reproducible evaluation

\* a real-song benchmark

\* objective measurements

\* a collection of controlled experiments

V1 did not establish:

\* reliable lyric-to-audio correspondence

\* production-quality timestamps

\* robust alignment across arbitrary songs

\* multilingual robustness

\* reliable handling of instrumental sections

\* general high-accuracy alignment

\---

\# 43. The Most Important V1 Lesson

The central lesson is:

\> **\*\*A structurally correct alignment pipeline is not necessarily a temporally correct alignment pipeline.\*\***

A second, more specific lesson is:

\> **\*\*Detecting musical boundaries is not the same as identifying which lyric is being sung at those boundaries.\*\***

And a third:

\> **\*\*Acoustic features appear more useful for local refinement than for establishing global lyric-to-audio correspondence.\*\***

These three observations define the starting point for V2.

\---

\# 44. V1 → V2 Decision

V1 should now be considered experimentally closed.

The project should retain:

\`\`\`text

Audio representation

Feature extraction

Feature timeline

Candidate detection

Benchmark

Evaluation framework

Alignment domain

Evidence model

Tests

\`\`\`

The current global candidate-selection strategy should not be treated as the final matcher.

V2 should investigate a stronger audio-content ↔ lyric-content representation.

The project should remain local-first while this research is performed.

No external AI service is required for the initial V2 experiments.

\---

\# 45. V2 Research Question

The first V2 question is:

\> **\*\*Can a locally computed representation of the actual sung audio provide enough information to match supplied lyrics to their correct regions of the song?\*\***

The answer to this question determines the next architectural step.

If the representation is useful:

\`\`\`text

representation

      ↓

matcher

      ↓

sequence alignment

      ↓

local refinement

\`\`\`

If it is insufficient:

\`\`\`text

record failure

      ↓

identify missing information

      ↓

design next experiment

\`\`\`

The project should not introduce complexity without evidence.

\---

\# 46. V1 → V2 Architecture

The evolution is therefore:

\`\`\`text

V1

Audio

 ↓

Acoustic features

 ↓

Candidates

 ↓

Temporal/sequence guess

 ↓

Timestamp

\`\`\`

to:

\`\`\`text

V2

Audio

 ↓

Audio representation

 ↓

Candidate / region generation

 ↓

Audio ↔ Lyric correspondence

 ↓

Sequence alignment

 ↓

Local acoustic refinement

 ↓

Timestamp

\`\`\`

The V1 candidate detector remains useful.

The major change is the **\*\*correspondence layer\*\***.

\---

\# 47. Final V1 Statement

V1 built the machine.

It proved that the system can:

\`\`\`text

load audio

    ↓

understand its temporal structure

    ↓

extract acoustic information

    ↓

generate candidate boundaries

    ↓

accept lyrics

    ↓

construct alignment objects

    ↓

produce LRC data

\`\`\`

It also demonstrated where the machine currently fails.

The machine does not yet understand which musical event corresponds to which lyric.

That is the problem V2 is now responsible for investigating.

V1 is therefore preserved as the experimental baseline and source of knowledge for every future alignment version.

**\*\*V1 is closed as a research phase.\*\***

**\*\*V2 begins with the construction of a stronger lyric-to-audio correspondence mechanism.\*\***
