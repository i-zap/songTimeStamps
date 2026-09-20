import json
import sys
from pathlib import Path
from statistics import median


def parse_timestamp(timestamp: str) -> float:
    minutes, seconds = timestamp.split(":")
    return int(minutes) * 60 + float(seconds)


def parse_lrc(path: Path) -> list[tuple[float, str]]:
    events = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or not line.startswith("["):
            continue

        closing_bracket = line.find("]")
        if closing_bracket == -1:
            continue

        timestamp_text = line[1:closing_bracket]
        text = line[closing_bracket + 1 :].strip()

        try:
            timestamp = parse_timestamp(timestamp_text)
        except ValueError:
            continue

        events.append((timestamp, text))

    return sorted(events)


def split_reference_events(
    events: list[tuple[float, str]],
) -> tuple[list[float], list[float]]:
    lyric_events = []
    sync_events = []

    for timestamp, text in events:
        if text:
            lyric_events.append(timestamp)
        else:
            sync_events.append(timestamp)

    return lyric_events, sync_events


def load_candidates(path: Path) -> list[float]:
    data = json.loads(path.read_text(encoding="utf-8"))

    return [float(timestamp) for timestamp in data["candidates"]]


def nearest_candidate(
    timestamp: float,
    candidates: list[float],
) -> tuple[float, float]:
    candidate = min(
        candidates,
        key=lambda value: abs(value - timestamp),
    )

    error = candidate - timestamp

    return candidate, error


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: uv run python "
            "experiments/v1/candidate_diagnostics.py "
            "<ground_truth.lrc> <predicted.json>"
        )
        raise SystemExit(1)

    ground_truth_path = Path(sys.argv[1])
    predicted_json_path = Path(sys.argv[2])

    if not ground_truth_path.exists():
        print(f"Ground truth file not found: {ground_truth_path}")
        raise SystemExit(1)

    if not predicted_json_path.exists():
        print(f"Prediction JSON not found: {predicted_json_path}")
        raise SystemExit(1)

    reference_events = parse_lrc(ground_truth_path)

    lyric_timestamps, sync_timestamps = split_reference_events(reference_events)

    candidates = load_candidates(predicted_json_path)

    if not candidates:
        print("No candidates found in predicted.json.")
        raise SystemExit(1)

    diagnostics = []

    for index, ground_truth in enumerate(lyric_timestamps):
        candidate, signed_error = nearest_candidate(
            ground_truth,
            candidates,
        )

        diagnostics.append(
            {
                "index": index,
                "ground_truth": ground_truth,
                "nearest_candidate": candidate,
                "signed_error": signed_error,
                "absolute_error": abs(signed_error),
            }
        )

    absolute_errors = [item["absolute_error"] for item in diagnostics]

    print("=" * 72)
    print("CANDIDATE DETECTION DIAGNOSTICS")
    print("=" * 72)
    print()

    print("REFERENCE STRUCTURE")
    print(f"Ground-truth lyric events: {len(lyric_timestamps)}")
    print(f"Ground-truth sync events:  {len(sync_timestamps)}")
    print(f"Detected candidates:      {len(candidates)}")
    print()

    print("NEAREST-CANDIDATE ERROR")
    print(f"Mean absolute error:   {sum(absolute_errors) / len(absolute_errors):.3f}s")
    print(f"Median absolute error: {median(absolute_errors):.3f}s")
    print(f"Maximum absolute error: {max(absolute_errors):.3f}s")
    print()

    print("CANDIDATE COVERAGE")

    thresholds = [0.25, 0.50, 1.00, 2.00]

    for threshold in thresholds:
        matches = sum(error <= threshold for error in absolute_errors)

        percentage = (matches / len(absolute_errors)) * 100

        print(
            f"Within ±{threshold:.2f}s: "
            f"{matches:2d}/{len(absolute_errors)} "
            f"({percentage:.1f}%)"
        )

    print()

    print("PER-LINE NEAREST CANDIDATE")
    print("-" * 72)

    for item in diagnostics:
        print(
            f"{item['index']:03d} | "
            f"GT {item['ground_truth']:8.3f}s | "
            f"Candidate {item['nearest_candidate']:8.3f}s | "
            f"Error {item['signed_error']:+7.3f}s"
        )

    print()

    print("POORLY COVERED TIMESTAMPS")
    print("-" * 72)

    poor_candidates = [item for item in diagnostics if item["absolute_error"] > 2.0]

    if not poor_candidates:
        print("Every lyric timestamp has a candidate within ±2.00s.")
    else:
        for item in poor_candidates:
            print(
                f"{item['index']:03d} | "
                f"GT {item['ground_truth']:8.3f}s | "
                f"Nearest {item['nearest_candidate']:8.3f}s | "
                f"Error {item['signed_error']:+7.3f}s"
            )

    print()
    print("=" * 72)


if __name__ == "__main__":
    main()
