import json
import sys
from pathlib import Path

import numpy as np
from app.domain.lyrics import LyricLine


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


def uniform_gap_match(
    lyric_lines: list[LyricLine],
    candidate_timestamps: np.ndarray,
    lyric_start: float,
    lyric_end: float,
) -> list[tuple[LyricLine, float]]:
    if candidate_timestamps.ndim != 1:
        raise ValueError("Candidate timestamps must be a 1D array.")

    candidates = candidate_timestamps[
        (candidate_timestamps >= lyric_start) & (candidate_timestamps <= lyric_end)
    ]

    lyric_count = len(lyric_lines)
    candidate_count = len(candidates)

    if lyric_count == 0:
        return []

    if candidate_count < lyric_count:
        raise ValueError("Not enough candidates inside lyric region.")

    if lyric_count == 1:
        return [(lyric_lines[0], float(candidates[0]))]

    total_duration = lyric_end - lyric_start

    # ------------------------------------------------------------------
    # Experiment:
    #
    # Assume every lyric transition has the same expected duration.
    #
    # This deliberately removes lyric-character weighting.
    # ------------------------------------------------------------------

    expected_gap = total_duration / lyric_count

    costs = np.full(
        (lyric_count, candidate_count),
        np.inf,
        dtype=np.float64,
    )

    previous = np.full(
        (lyric_count, candidate_count),
        -1,
        dtype=np.int64,
    )

    # First lyric:
    # Penalize distance from the beginning of the lyric region.
    for candidate_index in range(candidate_count):
        timestamp = float(candidates[candidate_index])

        costs[0, candidate_index] = abs(timestamp - lyric_start)

    # Remaining lyrics.
    for lyric_index in range(1, lyric_count):
        for candidate_index in range(
            lyric_index,
            candidate_count,
        ):
            current_timestamp = float(candidates[candidate_index])

            previous_indices = np.arange(
                lyric_index - 1,
                candidate_index,
            )

            if len(previous_indices) == 0:
                continue

            transition_costs = costs[
                lyric_index - 1,
                previous_indices,
            ]

            previous_timestamps = candidates[previous_indices]

            gaps = current_timestamp - previous_timestamps

            gap_costs = np.abs(
                np.log(np.maximum(gaps, 1e-6)) - np.log(max(expected_gap, 1e-6))
            )

            total_costs = transition_costs + gap_costs

            best_position = int(np.argmin(total_costs))

            best_previous = int(previous_indices[best_position])

            costs[
                lyric_index,
                candidate_index,
            ] = total_costs[best_position]

            previous[
                lyric_index,
                candidate_index,
            ] = best_previous

    final_index = int(np.argmin(costs[-1]))

    if not np.isfinite(costs[-1, final_index]):
        raise ValueError("Unable to match lyric lines.")

    selected_indices = np.empty(
        lyric_count,
        dtype=np.int64,
    )

    selected_indices[-1] = final_index

    for lyric_index in range(
        lyric_count - 1,
        0,
        -1,
    ):
        selected_indices[lyric_index - 1] = previous[
            lyric_index,
            selected_indices[lyric_index],
        ]

    return [
        (
            lyric_line,
            float(candidates[candidate_index]),
        )
        for lyric_line, candidate_index in zip(
            lyric_lines,
            selected_indices,
            strict=True,
        )
    ]


def nearest_candidate(
    timestamp: float,
    candidates: np.ndarray,
) -> tuple[float, float]:
    distances = np.abs(candidates - timestamp)

    index = int(np.argmin(distances))

    candidate = float(candidates[index])

    error = candidate - timestamp

    return candidate, error


def calculate_metrics(
    reference: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    errors = predicted - reference
    absolute_errors = np.abs(errors)

    return {
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

    print(f"Mean absolute error: {metrics['mae']:.3f}s")

    print(f"Median absolute error: {metrics['median']:.3f}s")

    print(f"Maximum absolute error: {metrics['maximum']:.3f}s")

    print(f"Mean signed error: {metrics['signed_mean']:+.3f}s")

    print(f"Within ±0.25s: {metrics['within_025'] * 100:.1f}%")

    print(f"Within ±0.50s: {metrics['within_050'] * 100:.1f}%")

    print(f"Within ±1.00s: {metrics['within_100'] * 100:.1f}%")

    print(f"Within ±2.00s: {metrics['within_200'] * 100:.1f}%")

    print()


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: uv run python "
            "experiments/v1/uniform_matcher_diagnostics.py "
            "<ground_truth.lrc> <predicted.json>"
        )
        raise SystemExit(1)

    ground_truth_path = Path(sys.argv[1])
    predicted_path = Path(sys.argv[2])

    if not ground_truth_path.exists():
        print(f"Ground truth file not found: {ground_truth_path}")
        raise SystemExit(1)

    if not predicted_path.exists():
        print(f"Prediction file not found: {predicted_path}")
        raise SystemExit(1)

    ground_truth_events = parse_lrc(ground_truth_path)

    ground_truth_lyrics = [
        (timestamp, text) for timestamp, text in ground_truth_events if text.strip()
    ]

    prediction = load_prediction(predicted_path)

    candidate_timestamps = np.asarray(
        prediction["candidates"],
        dtype=np.float64,
    )

    lyric_start = float(prediction["lyric_region"]["start"])

    lyric_end = float(prediction["lyric_region"]["end"])

    lyric_lines = [
        LyricLine(
            index=index,
            text=text,
        )
        for index, (_, text) in enumerate(ground_truth_lyrics)
    ]

    reference_timestamps = np.asarray(
        [timestamp for timestamp, _ in ground_truth_lyrics],
        dtype=np.float64,
    )

    # ------------------------------------------------------------------
    # Run uniform-gap experiment.
    # ------------------------------------------------------------------

    matches = uniform_gap_match(
        lyric_lines=lyric_lines,
        candidate_timestamps=candidate_timestamps,
        lyric_start=lyric_start,
        lyric_end=lyric_end,
    )

    uniform_timestamps = np.asarray(
        [timestamp for _, timestamp in matches],
        dtype=np.float64,
    )

    uniform_metrics = calculate_metrics(
        reference_timestamps,
        uniform_timestamps,
    )

    # ------------------------------------------------------------------
    # Calculate nearest-candidate baseline.
    # ------------------------------------------------------------------

    nearest_timestamps = np.asarray(
        [
            nearest_candidate(
                float(timestamp),
                candidate_timestamps,
            )[0]
            for timestamp in reference_timestamps
        ],
        dtype=np.float64,
    )

    nearest_metrics = calculate_metrics(
        reference_timestamps,
        nearest_timestamps,
    )

    # ------------------------------------------------------------------
    # Load current V1.1 matcher result.
    # ------------------------------------------------------------------

    current_alignments = prediction["alignments"]

    current_timestamps = np.asarray(
        [alignment["audio_start"] for alignment in current_alignments],
        dtype=np.float64,
    )

    current_metrics = calculate_metrics(
        reference_timestamps,
        current_timestamps,
    )

    # ------------------------------------------------------------------
    # Output.
    # ------------------------------------------------------------------

    print("=" * 80)
    print("UNIFORM-GAP MATCHER EXPERIMENT")
    print("=" * 80)
    print()

    print(f"Reference lyric events: {len(reference_timestamps)}")

    print(f"Candidate timestamps:   {len(candidate_timestamps)}")

    print(
        f"Uniform expected gap:   {(lyric_end - lyric_start) / len(lyric_lines):.3f}s"
    )

    print()

    print_metrics(
        "NEAREST-CANDIDATE BASELINE",
        nearest_metrics,
    )

    print_metrics(
        "CURRENT V1.1 MATCHER",
        current_metrics,
    )

    print_metrics(
        "UNIFORM-GAP EXPERIMENT",
        uniform_metrics,
    )

    # ------------------------------------------------------------------
    # Direct comparison.
    # ------------------------------------------------------------------

    print("DIRECT COMPARISON")
    print("-" * 80)

    mae_change = uniform_metrics["mae"] - current_metrics["mae"]

    print(f"MAE change vs current V1.1: {mae_change:+.3f}s")

    print(f"MAE improvement: {current_metrics['mae'] - uniform_metrics['mae']:.3f}s")

    print()

    # ------------------------------------------------------------------
    # Per-line comparison.
    # ------------------------------------------------------------------

    print("PER-LINE COMPARISON")
    print("-" * 80)

    print("IDX | GT | CURRENT | UNIFORM | CURRENT ERR | UNIFORM ERR")

    print("-" * 80)

    current_errors = current_timestamps - reference_timestamps

    uniform_errors = uniform_timestamps - reference_timestamps

    for index in range(len(reference_timestamps)):
        print(
            f"{index:03d} | "
            f"{reference_timestamps[index]:7.3f} | "
            f"{current_timestamps[index]:8.3f} | "
            f"{uniform_timestamps[index]:7.3f} | "
            f"{current_errors[index]:+11.3f} | "
            f"{uniform_errors[index]:+10.3f}"
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
