import json
import sys
from pathlib import Path

import numpy as np
from app.alignment.pipeline import build_feature_timeline
from app.alignment.signal import calculate_boundary_strength
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

    print(f"Mean absolute error:   {metrics['mae']:.3f}s")

    print(f"Median absolute error: {metrics['median']:.3f}s")

    print(f"Maximum absolute error: {metrics['maximum']:.3f}s")

    print(f"Mean signed error:     {metrics['signed_mean']:+.3f}s")

    print(f"Within ±0.25s: {metrics['within_025'] * 100:.1f}%")

    print(f"Within ±0.50s: {metrics['within_050'] * 100:.1f}%")

    print(f"Within ±1.00s: {metrics['within_100'] * 100:.1f}%")

    print(f"Within ±2.00s: {metrics['within_200'] * 100:.1f}%")

    print()


def build_adaptive_sequence(
    candidates: np.ndarray,
    strengths: np.ndarray,
    lyric_count: int,
    lyric_start: float,
    lyric_end: float,
) -> np.ndarray:
    """
    Experimental sequence matcher.

    Unlike the current V1.1 matcher, this does NOT use
    lyric character lengths.

    It creates a weak global timing expectation, but allows
    acoustic boundary strength to influence candidate selection.

    The timing prior is intentionally weak so that the acoustic
    evidence can dominate when a strong candidate exists.
    """

    candidate_count = len(candidates)

    if lyric_count == 0:
        return np.asarray([], dtype=np.float64)

    if candidate_count < lyric_count:
        raise ValueError("Not enough candidates for lyric lines.")

    total_duration = lyric_end - lyric_start

    expected_gap = total_duration / lyric_count

    # Normalize candidate strength.
    minimum = float(np.min(strengths))
    maximum = float(np.max(strengths))

    if maximum == minimum:
        normalized_strengths = np.zeros_like(
            strengths,
            dtype=np.float64,
        )
    else:
        normalized_strengths = (strengths - minimum) / (maximum - minimum)

    # --------------------------------------------------------------
    # Cost weights.
    #
    # These are deliberately experimental.
    #
    # Timing = weak
    # Acoustic boundary = strong
    # --------------------------------------------------------------

    acoustic_weight = 2.0
    timing_weight = 0.35

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

    # --------------------------------------------------------------
    # First lyric.
    #
    # We don't force it to the exact start.
    # We use distance from lyric_start as a weak prior.
    # --------------------------------------------------------------

    for candidate_index in range(candidate_count):
        timestamp = float(candidates[candidate_index])

        distance_from_start = abs(timestamp - lyric_start) / total_duration

        acoustic_cost = 1.0 - normalized_strengths[candidate_index]

        costs[
            0,
            candidate_index,
        ] = timing_weight * distance_from_start + acoustic_weight * acoustic_cost

    # --------------------------------------------------------------
    # Remaining lyrics.
    # --------------------------------------------------------------

    for lyric_index in range(
        1,
        lyric_count,
    ):
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

            previous_timestamps = candidates[previous_indices]

            gaps = current_timestamp - previous_timestamps

            valid = gaps > 0

            if not np.any(valid):
                continue

            valid_indices = previous_indices[valid]

            valid_gaps = gaps[valid]

            transition_costs = costs[
                lyric_index - 1,
                valid_indices,
            ]

            # Log-gap difference.
            #
            # This preserves proportional timing without
            # forcing exact durations.
            gap_costs = np.abs(
                np.log(
                    np.maximum(
                        valid_gaps,
                        1e-6,
                    )
                )
                - np.log(
                    max(
                        expected_gap,
                        1e-6,
                    )
                )
            )

            acoustic_cost = 1.0 - normalized_strengths[candidate_index]

            total_costs = (
                transition_costs
                + timing_weight * gap_costs
                + acoustic_weight * acoustic_cost
            )

            best_position = int(np.argmin(total_costs))

            best_previous = int(valid_indices[best_position])

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
        raise ValueError("Unable to construct candidate sequence.")

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

    return candidates[selected_indices]


def nearest_candidates(
    reference: np.ndarray,
    candidates: np.ndarray,
) -> np.ndarray:
    predictions = []

    for timestamp in reference:
        distances = np.abs(candidates - timestamp)

        index = int(np.argmin(distances))

        predictions.append(float(candidates[index]))

    return np.asarray(
        predictions,
        dtype=np.float64,
    )


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: uv run python "
            "experiments/v1/"
            "candidate_sequence_diagnostics.py "
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
    # Load reference.
    # --------------------------------------------------------------

    events = parse_lrc(ground_truth_path)

    lyric_events = [(timestamp, text) for timestamp, text in events if text.strip()]

    reference = np.asarray(
        [timestamp for timestamp, _ in lyric_events],
        dtype=np.float64,
    )

    lyric_lines = [
        LyricLine(
            index=index,
            text=text,
        )
        for index, (_, text) in enumerate(lyric_events)
    ]

    # --------------------------------------------------------------
    # Load exact candidate set from the previous experiment.
    # --------------------------------------------------------------

    prediction_path = Path("experiments/v1/results/predicted.json")

    if not prediction_path.exists():
        print(f"Prediction file not found: {prediction_path}")
        print("Run experiments/v1/run.py first.")
        raise SystemExit(1)

    prediction = load_prediction(prediction_path)

    candidates = np.asarray(
        prediction["candidates"],
        dtype=np.float64,
    )

    lyric_start = float(prediction["lyric_region"]["start"])

    lyric_end = float(prediction["lyric_region"]["end"])

    mask = (candidates >= lyric_start) & (candidates <= lyric_end)

    candidates = candidates[mask]

    # --------------------------------------------------------------
    # Calculate acoustic strength.
    # --------------------------------------------------------------

    frame_timestamps, frame_strengths = calculate_candidate_strengths(audio_path)

    candidate_strengths = np.asarray(
        [
            interpolate_strength(
                float(candidate),
                frame_timestamps,
                frame_strengths,
            )
            for candidate in candidates
        ],
        dtype=np.float64,
    )

    # --------------------------------------------------------------
    # Nearest candidate oracle.
    # --------------------------------------------------------------

    nearest = nearest_candidates(
        reference,
        candidates,
    )

    nearest_metrics = calculate_metrics(
        reference,
        nearest,
    )

    # --------------------------------------------------------------
    # Experimental sequence matcher.
    # --------------------------------------------------------------

    adaptive = build_adaptive_sequence(
        candidates=candidates,
        strengths=candidate_strengths,
        lyric_count=len(lyric_lines),
        lyric_start=lyric_start,
        lyric_end=lyric_end,
    )

    adaptive_metrics = calculate_metrics(
        reference,
        adaptive,
    )

    # --------------------------------------------------------------
    # Output.
    # --------------------------------------------------------------

    print("=" * 80)
    print("ADAPTIVE CANDIDATE SEQUENCE DIAGNOSTICS")
    print("=" * 80)
    print()

    print(f"Reference lyric events: {len(reference)}")

    print(f"Candidates evaluated:   {len(candidates)}")

    print()

    print_metrics(
        "NEAREST-CANDIDATE BASELINE",
        nearest_metrics,
    )

    print_metrics(
        "ADAPTIVE ACOUSTIC SEQUENCE",
        adaptive_metrics,
    )

    print("PER-LINE COMPARISON")
    print("-" * 80)

    print("IDX | GT | NEAREST | ADAPTIVE | NEAREST ERR | ADAPTIVE ERR | STRENGTH")

    print("-" * 80)

    for index, reference_timestamp in enumerate(reference):
        nearest_timestamp = float(nearest[index])

        adaptive_timestamp = float(adaptive[index])

        nearest_error = nearest_timestamp - reference_timestamp

        adaptive_error = adaptive_timestamp - reference_timestamp

        adaptive_strength = interpolate_strength(
            adaptive_timestamp,
            frame_timestamps,
            frame_strengths,
        )

        print(
            f"{index:03d} | "
            f"{reference_timestamp:7.3f} | "
            f"{nearest_timestamp:8.3f} | "
            f"{adaptive_timestamp:8.3f} | "
            f"{nearest_error:+11.3f} | "
            f"{adaptive_error:+12.3f} | "
            f"{adaptive_strength:.3f}"
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
