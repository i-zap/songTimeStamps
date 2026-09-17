import json
import sys
from pathlib import Path

import numpy as np
from app.alignment.pipeline import build_feature_timeline
from app.alignment.signal import calculate_boundary_strength


def parse_lrc(path: Path) -> list[tuple[float, str]]:
    events = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line.startswith("[") or "]" not in line:
            continue

        timestamp_text, lyric_text = line.split("]", 1)
        timestamp_text = timestamp_text[1:]

        try:
            minutes, seconds = timestamp_text.split(":", 1)
            timestamp = float(minutes) * 60.0 + float(seconds)
        except ValueError:
            continue

        events.append((timestamp, lyric_text))

    return events


def load_prediction(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def calculate_candidate_strengths(
    audio_path: Path,
) -> tuple[np.ndarray, np.ndarray]:
    from app.alignment.audio import load_audio

    audio = load_audio(audio_path)

    timeline = build_feature_timeline(audio)

    rms = np.asarray(
        [frame.rms for frame in timeline.frames],
        dtype=np.float32,
    )

    spectral_flux = np.asarray(
        [frame.spectral_flux for frame in timeline.frames],
        dtype=np.float32,
    )

    onset_strength = np.asarray(
        [frame.onset_strength for frame in timeline.frames],
        dtype=np.float32,
    )

    boundary_strength = calculate_boundary_strength(
        rms,
        spectral_flux,
        onset_strength,
    )

    timestamps = np.asarray(
        [frame.timestamp for frame in timeline.frames],
        dtype=np.float32,
    )

    return timestamps, boundary_strength


def interpolate_strength(
    timestamp: float,
    timestamps: np.ndarray,
    strengths: np.ndarray,
) -> float:
    if len(timestamps) == 0:
        raise ValueError("Timestamp array cannot be empty.")

    if len(timestamps) != len(strengths):
        raise ValueError("Timestamps and strengths must have the same length.")

    if timestamp <= timestamps[0]:
        return float(strengths[0])

    if timestamp >= timestamps[-1]:
        return float(strengths[-1])

    index = int(
        np.searchsorted(
            timestamps,
            timestamp,
            side="left",
        )
    )

    if index == 0:
        return float(strengths[0])

    if index >= len(timestamps):
        return float(strengths[-1])

    left = index - 1
    right = index

    left_time = float(timestamps[left])
    right_time = float(timestamps[right])

    left_strength = float(strengths[left])
    right_strength = float(strengths[right])

    if right_time == left_time:
        return left_strength

    ratio = (timestamp - left_time) / (right_time - left_time)

    return left_strength + ratio * (right_strength - left_strength)


def score_candidates(
    candidates: np.ndarray,
    timestamps: np.ndarray,
    strengths: np.ndarray,
) -> np.ndarray:
    return np.asarray(
        [
            interpolate_strength(
                float(candidate),
                timestamps,
                strengths,
            )
            for candidate in candidates
        ],
        dtype=np.float64,
    )


def nearest_candidate(
    reference: float,
    candidates: np.ndarray,
) -> tuple[float, float]:
    distances = np.abs(candidates - reference)

    index = int(np.argmin(distances))

    candidate = float(candidates[index])

    return candidate, candidate - reference


def strongest_candidate_in_window(
    reference: float,
    candidates: np.ndarray,
    strengths: np.ndarray,
    window: float,
) -> tuple[float, float, float]:
    mask = np.abs(candidates - reference) <= window

    indices = np.flatnonzero(mask)

    if len(indices) == 0:
        return (
            float("nan"),
            float("nan"),
            float("nan"),
        )

    local_strengths = strengths[indices]

    best_position = int(np.argmax(local_strengths))

    best_index = int(indices[best_position])

    candidate = float(candidates[best_index])

    strength = float(strengths[best_index])

    error = candidate - reference

    return candidate, error, strength


def calculate_metrics(
    reference: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    valid = np.isfinite(predicted)

    reference = reference[valid]
    predicted = predicted[valid]

    errors = predicted - reference
    absolute_errors = np.abs(errors)

    return {
        "count": float(len(errors)),
        "mae": float(np.mean(absolute_errors)),
        "median": float(np.median(absolute_errors)),
        "maximum": float(np.max(absolute_errors)),
        "signed_mean": float(np.mean(errors)),
        "within_025": float(np.mean(absolute_errors <= 0.25)),
        "within_050": float(np.mean(absolute_errors <= 0.50)),
        "within_100": float(np.mean(absolute_errors <= 1.00)),
        "within_200": float(np.mean(absolute_errors <= 2.00)),
    }


def print_metrics(
    name: str,
    metrics: dict[str, float],
) -> None:
    print(name)
    print("-" * 80)

    print(f"Events evaluated:     {int(metrics['count'])}")

    print(f"Mean absolute error:   {metrics['mae']:.3f}s")

    print(f"Median absolute error: {metrics['median']:.3f}s")

    print(f"Maximum absolute error: {metrics['maximum']:.3f}s")

    print(f"Mean signed error:     {metrics['signed_mean']:+.3f}s")

    print(f"Within ±0.25s: {metrics['within_025'] * 100:.1f}%")

    print(f"Within ±0.50s: {metrics['within_050'] * 100:.1f}%")

    print(f"Within ±1.00s: {metrics['within_100'] * 100:.1f}%")

    print(f"Within ±2.00s: {metrics['within_200'] * 100:.1f}%")

    print()


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: uv run python "
            "experiments/v1/candidate_scoring_diagnostics.py "
            "<audio> <ground_truth.lrc>"
        )
        raise SystemExit(1)

    audio_path = Path(sys.argv[1])
    ground_truth_path = Path(sys.argv[2])

    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}")
        raise SystemExit(1)

    if not ground_truth_path.exists():
        print(f"Ground truth file not found: {ground_truth_path}")
        raise SystemExit(1)

    # --------------------------------------------------------------
    # Ground truth
    # --------------------------------------------------------------

    events = parse_lrc(ground_truth_path)

    lyric_events = [(timestamp, text) for timestamp, text in events if text.strip()]

    reference = np.asarray(
        [timestamp for timestamp, _ in lyric_events],
        dtype=np.float64,
    )

    # --------------------------------------------------------------
    # Audio features
    # --------------------------------------------------------------

    frame_timestamps, frame_strengths = calculate_candidate_strengths(audio_path)

    # --------------------------------------------------------------
    # Candidate timestamps
    #
    # IMPORTANT:
    # We load the exact candidates produced by
    # the existing V1 experiment.
    # --------------------------------------------------------------

    results_path = Path("experiments/v1/results/predicted.json")

    if not results_path.exists():
        print(f"Prediction file not found: {results_path}")
        print("Run experiments/v1/run.py first.")
        raise SystemExit(1)

    prediction = load_prediction(results_path)

    candidates = np.asarray(
        prediction["candidates"],
        dtype=np.float64,
    )

    lyric_start = float(prediction["lyric_region"]["start"])

    lyric_end = float(prediction["lyric_region"]["end"])

    mask = (candidates >= lyric_start) & (candidates <= lyric_end)

    candidates = candidates[mask]

    candidate_strengths = score_candidates(
        candidates,
        frame_timestamps,
        frame_strengths,
    )

    # --------------------------------------------------------------
    # Baseline:
    # nearest candidate.
    # --------------------------------------------------------------

    nearest_predictions = np.asarray(
        [
            nearest_candidate(
                float(timestamp),
                candidates,
            )[0]
            for timestamp in reference
        ],
        dtype=np.float64,
    )

    nearest_metrics = calculate_metrics(
        reference,
        nearest_predictions,
    )

    # --------------------------------------------------------------
    # Local strongest candidate experiments.
    #
    # We intentionally test several windows rather than
    # choosing one arbitrary value.
    # --------------------------------------------------------------

    windows = (
        0.25,
        0.50,
        1.00,
        1.50,
        2.00,
    )

    window_results = {}

    for window in windows:
        predictions = []

        for timestamp in reference:
            candidate, _, _ = strongest_candidate_in_window(
                float(timestamp),
                candidates,
                candidate_strengths,
                window,
            )

            predictions.append(candidate)

        predictions_array = np.asarray(
            predictions,
            dtype=np.float64,
        )

        window_results[window] = (
            predictions_array,
            calculate_metrics(
                reference,
                predictions_array,
            ),
        )

    # --------------------------------------------------------------
    # Output
    # --------------------------------------------------------------

    print("=" * 80)
    print("CANDIDATE ACOUSTIC SCORING DIAGNOSTICS")
    print("=" * 80)
    print()

    print(f"Reference lyric events: {len(reference)}")

    print(f"Candidates evaluated:   {len(candidates)}")

    print()

    print_metrics(
        "NEAREST-CANDIDATE BASELINE",
        nearest_metrics,
    )

    print("STRONGEST ACOUSTIC CANDIDATE")
    print("-" * 80)

    for window in windows:
        _, metrics = window_results[window]

        print(
            f"Window ±{window:.2f}s | "
            f"MAE {metrics['mae']:.3f}s | "
            f"Median {metrics['median']:.3f}s | "
            f"±0.50s "
            f"{metrics['within_050'] * 100:.1f}% | "
            f"±1.00s "
            f"{metrics['within_100'] * 100:.1f}%"
        )

    print()

    # --------------------------------------------------------------
    # Detailed comparison using the 1-second window.
    # --------------------------------------------------------------

    _, _ = window_results[1.00]

    one_second_predictions = window_results[1.00][0]

    print("PER-LINE: NEAREST vs STRONGEST WITHIN ±1.00s")
    print("-" * 80)

    print("IDX | GT | NEAREST | STRONGEST | NEAREST ERR | STRONGEST ERR | STRENGTH")

    print("-" * 80)

    for index, reference_timestamp in enumerate(reference):
        nearest_timestamp, nearest_error = nearest_candidate(
            float(reference_timestamp),
            candidates,
        )

        strongest_timestamp = float(one_second_predictions[index])

        strongest_error = strongest_timestamp - reference_timestamp

        strength = interpolate_strength(
            strongest_timestamp,
            frame_timestamps,
            frame_strengths,
        )

        print(
            f"{index:03d} | "
            f"{reference_timestamp:7.3f} | "
            f"{nearest_timestamp:8.3f} | "
            f"{strongest_timestamp:9.3f} | "
            f"{nearest_error:+11.3f} | "
            f"{strongest_error:+13.3f} | "
            f"{strength:.3f}"
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
