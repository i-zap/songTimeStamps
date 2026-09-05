# SongTimeStamps

## V1 Alignment Engine — Phase Completion Report

**Project:** SongTimeStamps
**Version:** V1
**Phase:** Core Alignment Engine / Domain + Feature Pipeline
**Status:** Development phase complete
**Current branch:** `feat/core-domain`

---

# 1. V1 Objective

The objective of V1 was to establish the first working foundation of the SongTimeStamps alignment system.

The intended V1 workflow is:

**User provides:**

* Audio
* Lyrics

**System produces:**

* Aligned lyric timestamps
* Structured alignment data
* Eventually an LRC file

The primary objective was **not perfect alignment**.

The priority was to build a small, understandable, testable prototype that could expose the actual problems in the alignment process.

V1 is therefore intended to become the foundation for future versions rather than a disposable prototype.

---

# 2. Core V1 Philosophy

The project follows these principles:

### Lightweight first

Avoid unnecessarily large models, heavy dependencies, and expensive infrastructure.

### Local-first

The system should eventually be capable of running locally rather than depending on cloud AI services.

### AI only when necessary

AI/model-based approaches are not the default solution.

Classical signal-processing and algorithmic approaches should be used wherever they are sufficient.

### Prototype before optimization

V1 exists to answer:

> "Can we build the complete pipeline and understand where it fails?"

Rather than:

> "Can we achieve perfect alignment immediately?"

### Preserve knowledge between versions

Future versions must build on V1 rather than restarting from scratch.

Failures, benchmarks, design decisions, and limitations discovered in V1 are considered project knowledge.

---

# 3. Versioning Strategy

The project uses a Git-based version history.

The important distinction is:

* `main` = latest stable release
* Version branches = preserved historical versions
* Feature branches = active development

A completed V1 should remain recoverable independently so that it can be inspected or cloned years later.

Future development should build upon the accumulated knowledge of previous versions.

For example:

**V1 → V1.x → V2 → V2.x → V3**

A major architectural change may justify a new major version.

A smaller improvement or correction should remain within the existing version where practical.

---

# 4. Domain Layer Completed

The initial domain foundation was created before implementing the alignment algorithms.

## LyricLine

Represents one individual lyric line.

Current information includes:

* UUID
* line index
* lyric text

## LyricDocument

Represents a lyric document.

Current information includes:

* UUID
* language
* role
* collection of lyric lines

Supported lyric roles:

* `original`
* `romanized`
* `translation`

## LyricReference

Connects an alignment back to a specific lyric line and document.

It contains:

* document ID
* lyric line ID

This allows alignment data to reference the original lyric structure instead of duplicating lyric text.

---

# 5. Audio Domain

An audio representation was created using `AudioSamples`.

The V1 representation contains:

* sample rate
* audio samples
* channel count
* duration

Audio loading was implemented using `soundfile`.

Audio is loaded as floating-point samples and forced into a 2D representation so that mono and stereo input can be handled consistently.

---

# 6. Alignment Domain

The `Alignment` model represents the relationship between audio time and lyric content.

Each alignment contains:

* UUID
* audio start
* audio end
* lyric references
* confidence
* method

This establishes the central object that the eventual LRC-generation layer can consume.

---

# 7. Evidence Model

V1 also established an evidence structure rather than treating every alignment as an unexplained timestamp.

## EvidenceItem

Contains:

* name
* score
* source
* additional details

## LocalAlignmentEvidence

Stores evidence associated with an individual alignment.

## GlobalAlignmentEvidence

Stores evidence concerning the alignment as a whole.

## AlignmentResult

Combines:

* alignment IDs
* local evidence
* global evidence

This is important for future development because an alignment should eventually be explainable.

For example:

> Why did the system place this lyric line here?

The architecture already provides a place to store that reasoning.

---

# 8. Audio Processing Pipeline

The V1 signal-processing pipeline was built incrementally.

The current conceptual flow is:

**Audio**

↓

**Mono conversion**

↓

**Audio framing**

↓

**RMS**

↓

**Spectral flux**

↓

**Onset strength**

↓

**Boundary strength**

↓

**Candidate timestamps**

↓

**Lyric alignment**

↓

**Alignment objects**

---

# 9. Mono Conversion

Stereo and multi-channel audio is converted to mono before feature extraction.

This keeps the rest of the V1 signal-processing pipeline simple.

The conversion was tested for:

* stereo → mono
* mono → mono

---

# 10. Audio Framing

The audio is divided into overlapping frames.

V1 uses configurable:

* frame size
* hop size

The current pipeline uses a default frame size and hop size while allowing them to be overridden.

This provides the temporal resolution needed by the feature-extraction stage.

---

# 11. RMS Feature

RMS was implemented as a basic measurement of frame energy.

It provides information about how strong the audio signal is within each frame.

This gives the system a lightweight indication of changes in audio intensity.

---

# 12. Spectral Flux

Spectral flux was implemented to detect changes in the frequency distribution of consecutive frames.

This gives V1 another signal for identifying possible musical transitions or boundaries.

The implementation was tested with synthetic spectral changes.

---

# 13. Onset Strength

Onset strength was added as another lightweight indication of musical events.

The goal is to capture moments where the audio changes strongly enough that they may correspond to useful candidate positions.

---

# 14. Boundary Strength

The individual audio features are combined into a boundary-strength signal.

V1 therefore does not depend on one feature alone.

The current approach combines:

* RMS
* spectral flux
* onset strength

into a single signal used for candidate detection.

This represents the first version of the hybrid signal-processing strategy.

---

# 15. Feature Timeline

A feature timeline was introduced so that extracted audio information remains associated with time.

Each feature frame contains:

* timestamp
* RMS
* spectral flux
* onset strength

This became an important architectural decision.

Instead of passing disconnected arrays throughout the entire application, the system has a structured temporal representation of the audio.

---

# 16. Candidate Detection

Candidate timestamps are generated from the calculated boundary-strength signal.

The candidate detector identifies positions that appear sufficiently significant according to a configurable threshold.

This creates the intermediate representation:

**Audio → Candidate timestamps**

rather than attempting to directly produce lyric timestamps from raw audio.

---

# 17. Result Builder

The result-building stage converts candidate timestamps into actual lyric alignments.

It associates lyric lines with candidate timestamps and creates audio ranges.

The builder also connects every generated alignment to the appropriate `LyricLine` through `LyricReference`.

This means the alignment layer remains connected to the domain model.

---

# 18. Pipeline Integration

The individual components were integrated into a single pipeline.

The pipeline now performs the complete V1 sequence:

1. Receive audio.
2. Convert audio to mono.
3. Frame the audio.
4. Calculate RMS.
5. Calculate spectral flux.
6. Calculate onset strength.
7. Calculate boundary strength.
8. Generate candidate timestamps.
9. Build lyric alignments.
10. Return structured alignment data.

This represents the first complete end-to-end alignment path.

---

# 19. Testing

The V1 implementation was developed with tests alongside the individual components.

The final validation reached:

**22 tests → 30 tests → final pipeline validation**

The latest complete validation showed:

```text
30 passed
All checks passed!
42 files already formatted
```

The test suite covers the major components created during this phase, including:

* audio handling
* candidate detection
* feature timeline
* feature extraction
* onset detection
* preprocessing
* alignment result
* alignment result builder
* RMS
* signal processing
* spectral processing
* matching
* complete pipeline
* application health

The important result is that the implemented components are currently structurally passing their tests.

---

# 20. Code Quality Validation

The project also uses Ruff for code quality and formatting.

The final checks passed:

```text
uv run ruff check .
All checks passed!
```

and:

```text
uv run ruff format --check .
42 files already formatted
```

Therefore the current implementation is both test-passing and formatter/linter clean.

---

# 21. Important V1 Validation Result

A real-song test was performed using a 4:14 audio file.

The audio duration was:

**254.133 seconds**

The lyric input contained:

**50 lyric lines**

The V1 system successfully produced:

**50 alignments**

However, the resulting timestamps were incorrect.

The system produced timestamps concentrated approximately between:

**3.471 s and 43.410 s**

while the actual lyric section begins around:

**17.15 s**

and continues much farther into the song.

The final alignment was:

```text
43.410 → 254.133
```

for the final lyric line.

This is clearly not an acceptable final alignment.

---

# 22. V1 Failure — What We Learned

This failure is valuable because it identifies the next engineering problem.

The system is capable of:

* loading the audio
* processing the audio
* extracting features
* generating candidates
* accepting lyrics
* creating lyric references
* producing a complete alignment structure

But the temporal candidates are not yet representing the real lyric timing correctly.

Therefore the primary problem is currently **alignment accuracy**, not application structure.

The failure should not be patched using arbitrary offsets or song-specific constants.

For example, we should not solve one song with:

```text
timestamp + 17 seconds
```

or:

```text
timestamp × some constant
```

Such fixes would hide the underlying problem and make the system less general.

---

# 23. Secondary V1 Failure

The result builder currently has a weakness when candidate timestamps are insufficient.

If the final candidate is treated as the beginning of the final lyric, the remaining duration can be assigned to that lyric.

This produced:

```text
43.410 → 254.133
```

for the final lyric.

This behavior is mathematically valid but musically unreliable.

Future versions should therefore handle insufficient or unreliable candidate timestamps explicitly rather than automatically assigning the remaining entire audio duration to the final lyric.

---

# 24. What V1 Has Successfully Proven

V1 has demonstrated that a lightweight classical approach can form a complete processing architecture without requiring a large AI model.

The project now has:

* domain models
* audio loading
* preprocessing
* feature extraction
* temporal feature representation
* candidate detection
* matching
* alignment construction
* evidence structures
* tests
* linting
* formatting
* an integrated pipeline

The system is therefore no longer just a collection of experiments.

It is now a functioning prototype architecture.

---

# 25. What V1 Has NOT Proven

V1 has **not** yet proven that the current candidate-generation strategy can reliably align arbitrary songs.

It has also not yet proven:

* robust lyric-to-audio synchronization
* accurate handling of instrumental sections
* reliable handling of different musical structures
* accurate final LRC generation
* robustness across different genres
* robustness across different languages
* high first-attempt alignment accuracy

These are future validation targets.

---

# 26. V1 Knowledge to Carry Forward

The following information must be preserved when moving to future versions.

### Decision 1 — Lightweight approach

Do not introduce a large model unless the classical approach demonstrates that it cannot reasonably solve the problem.

### Decision 2 — Structured intermediate data

Keep the feature timeline and alignment structures rather than collapsing everything into one opaque function.

### Decision 3 — Evidence matters

Future alignment methods should be capable of explaining or recording why an alignment was selected.

### Decision 4 — No arbitrary timestamp hacks

Offsets and magic scaling factors should not be used to hide algorithmic problems.

### Decision 5 — Tests remain mandatory

Every major improvement should extend the existing test suite rather than replacing it.

### Decision 6 — Preserve previous knowledge

V2 must compare itself against V1 rather than simply replacing V1.

---

# 27. Recommended V1.x Direction

The next work should not immediately be a redesign.

The first V1.x objective should be:

> **Understand exactly why candidate timestamps are being generated incorrectly.**

The investigation should follow the existing pipeline:

```text
Audio
 ↓
Frames
 ↓
Feature timestamps
 ↓
RMS
 ↓
Spectral flux
 ↓
Onset
 ↓
Boundary strength
 ↓
Candidate timestamps
 ↓
Matching
 ↓
Alignment construction
```

Each stage should be inspected independently.

The goal is to identify the first stage where the timeline diverges from reality.

Only after that should the algorithm be modified.

---

# 28. Current Project State

At the end of this phase:

**Domain layer:** complete for V1 foundation

**Audio layer:** functional

**Feature extraction:** functional

**Candidate detection:** functional

**Alignment construction:** functional

**Testing:** passing

**Linting:** passing

**Formatting:** passing

**End-to-end prototype:** functional

**Real-world alignment accuracy:** insufficient

**Next focus:** diagnose and improve temporal candidate generation/alignment

---

# 29. V1 Status

## 🟢 Engineering foundation

Complete.

## 🟢 Automated tests

Passing.

## 🟢 Code quality

Passing.

## 🟢 End-to-end pipeline

Working.

## 🟡 Real-world alignment quality

Needs improvement.

## 🔴 Production-ready alignment

Not yet.

---

# 30. Final V1 Conclusion

V1 has accomplished its primary purpose.

It has established a lightweight, modular and testable alignment foundation while exposing the central weakness of the current approach.

The project should **not restart from scratch**.

The next version should inherit:

* the domain layer
* the audio representation
* feature processing
* candidate generation
* alignment structures
* evidence structures
* tests
* engineering decisions
* known failures

The next stage should therefore be treated as an **incremental improvement of V1**, not a replacement of V1.

The most important lesson from this phase is:

> **A structurally correct alignment pipeline is not necessarily a temporally correct alignment pipeline.**

V1 has successfully built the machine.

The next phase is about teaching that machine to understand where the music actually is.
