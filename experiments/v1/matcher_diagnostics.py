import json
import sys
from pathlib import Path

import numpy as np
from app.alignment.matching import match_lyric_lines
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


def nearest_candidate(
    timestamp: float,
    candidates: np.ndarray,
) -> tuple[float, float]:
    distances = np.abs(candidates - timestamp)
    index = int(np.argmin(distances))

    candidate = float(candidates[index])
    error = candidate - timestamp

    return candidate, error


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: uv run python "
            "experiments/v1/matcher_diagnostics.py "
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

    lyric_lines = []

    for index, (_, text) in enumerate(ground_truth_lyrics):
        lyric_lines.append(
            LyricLine(
                index=index,
                text=text,
            )
        )

    matches = match_lyric_lines(
        lyric_lines=lyric_lines,
        candidate_timestamps=candidate_timestamps,
        lyric_start=lyric_start,
        lyric_end=lyric_end,
    )

    selected_timestamps = np.asarray(
        [timestamp for _, timestamp in matches],
        dtype=np.float64,
    )

    reference_timestamps = np.asarray(
        [timestamp for timestamp, _ in ground_truth_lyrics],
        dtype=np.float64,
    )

    if len(selected_timestamps) != len(reference_timestamps):
        raise ValueError("Prediction/reference lyric counts do not match.")

    print("=" * 80)
    print("MATCHER SELECTION DIAGNOSTICS")
    print("=" * 80)
    print()

    print("STRUCTURE")
    print("-" * 80)
    print(f"Reference lyric events: {len(reference_timestamps)}")
    print(f"Candidate timestamps:   {len(candidate_timestamps)}")
    print(f"Matcher selections:     {len(selected_timestamps)}")
    print()

    print("SELECTION COMPARISON")
    print("-" * 80)
    print(
        "IDX | "
        "GROUND TRUTH | "
        "NEAREST CAND | "
        "SELECTED | "
        "NEAREST ERR | "
        "SELECTED ERR | "
        "EXTRA SELECTION ERROR"
    )

    print("-" * 80)

    selected_errors = []
    nearest_errors = []
    extra_errors = []

    for index, (
        reference_timestamp,
        selected_timestamp,
    ) in enumerate(
        zip(
            reference_timestamps,
            selected_timestamps,
            strict=True,
        )
    ):
        nearest_timestamp, nearest_error = nearest_candidate(
            float(reference_timestamp),
            candidate_timestamps,
        )

        selected_error = float(selected_timestamp) - float(reference_timestamp)

        extra_error = abs(selected_error) - abs(nearest_error)

        selected_errors.append(abs(selected_error))
        nearest_errors.append(abs(nearest_error))
        extra_errors.append(extra_error)

        print(
            f"{index:03d} | "
            f"{reference_timestamp:11.3f}s | "
            f"{nearest_timestamp:11.3f}s | "
            f"{selected_timestamp:8.3f}s | "
            f"{nearest_error:+10.3f}s | "
            f"{selected_error:+11.3f}s | "
            f"{extra_error:+18.3f}s"
        )

    selected_errors_array = np.asarray(
        selected_errors,
        dtype=np.float64,
    )

    nearest_errors_array = np.asarray(
        nearest_errors,
        dtype=np.float64,
    )

    extra_errors_array = np.asarray(
        extra_errors,
        dtype=np.float64,
    )

    print()
    print("SUMMARY")
    print("-" * 80)

    print(f"Nearest-candidate MAE: {np.mean(nearest_errors_array):.3f}s")

    print(f"Matcher-selected MAE:  {np.mean(selected_errors_array):.3f}s")

    print(f"Average extra error:    {np.mean(extra_errors_array):.3f}s")

    print(f"Median extra error:     {np.median(extra_errors_array):.3f}s")

    print(f"Worst extra error:      {np.max(extra_errors_array):.3f}s")

    print()

    print("MATCHER REGRESSIONS")
    print("-" * 80)

    regressions = [
        index
        for index, extra_error in enumerate(extra_errors_array)
        if extra_error > 1.0
    ]

    if not regressions:
        print("No selections were more than 1.0s worse than nearest candidate.")
    else:
        print(f"Selections >1.0s worse than nearest candidate: {len(regressions)}")
        print()

        for index in regressions:
            print(
                f"{index:03d} | "
                f"GT {reference_timestamps[index]:8.3f}s | "
                f"Nearest {nearest_errors_array[index]:+7.3f}s | "
                f"Selected {selected_errors_array[index]:7.3f}s | "
                f"Extra {extra_errors_array[index]:+7.3f}s"
            )

    print()
    print("SELECTIONS WITHIN THRESHOLDS")
    print("-" * 80)

    for threshold in (0.25, 0.5, 1.0, 2.0):
        nearest_count = int(np.sum(nearest_errors_array <= threshold))

        selected_count = int(np.sum(selected_errors_array <= threshold))

        total = len(reference_timestamps)

        print(
            f"±{threshold:.2f}s | "
            f"Nearest: {nearest_count:2d}/{total} "
            f"({nearest_count / total * 100:5.1f}%) | "
            f"Matcher: {selected_count:2d}/{total} "
            f"({selected_count / total * 100:5.1f}%)"
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
