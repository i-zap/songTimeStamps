import re
import sys
from pathlib import Path

TIMESTAMP_PATTERN = re.compile(r"^\[(\d{2}):(\d{2})\.(\d{2})\](.*)$")


def parse_lrc(path: Path) -> list[tuple[float, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()

    entries = []

    for line in lines:
        match = TIMESTAMP_PATTERN.match(line.strip())

        if not match:
            continue

        minutes, seconds, centiseconds, text = match.groups()
        text = text.strip()

        timestamp = int(minutes) * 60 + int(seconds) + int(centiseconds) / 100

        entries.append((timestamp, text))

    return entries


def split_reference_events(
    entries: list[tuple[float, str]],
) -> tuple[
    list[tuple[float, str]],
    list[tuple[float, str]],
]:
    lyric_events = []
    sync_events = []

    for timestamp, text in entries:
        if text:
            lyric_events.append((timestamp, text))
        else:
            sync_events.append((timestamp, text))

    return lyric_events, sync_events


def calculate_errors(
    predicted: list[tuple[float, str]],
    ground_truth: list[tuple[float, str]],
) -> list[float]:
    if len(predicted) != len(ground_truth):
        raise ValueError(
            "Prediction and ground truth must contain the same "
            f"number of lyric segments. "
            f"Predicted: {len(predicted)}, "
            f"Ground truth: {len(ground_truth)}."
        )

    return [
        predicted_timestamp - ground_truth_timestamp
        for (predicted_timestamp, _), (ground_truth_timestamp, _) in zip(
            predicted, ground_truth, strict=True
        )
    ]


def calculate_percentage_within(
    errors: list[float],
    threshold: float,
) -> float:
    if not errors:
        return 0.0

    count = sum(abs(error) <= threshold for error in errors)

    return (count / len(errors)) * 100


def calculate_median(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot calculate median of an empty list.")

    sorted_values = sorted(values)
    middle = len(sorted_values) // 2

    if len(sorted_values) % 2 == 0:
        return (sorted_values[middle - 1] + sorted_values[middle]) / 2

    return sorted_values[middle]


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: uv run python experiments/v1/evaluate.py "
            "<predicted.lrc> <ground_truth.lrc>"
        )

    predicted_path = Path(sys.argv[1])
    ground_truth_path = Path(sys.argv[2])

    predicted_entries = parse_lrc(predicted_path)
    ground_truth_entries = parse_lrc(ground_truth_path)

    predicted_lyrics, predicted_sync = split_reference_events(predicted_entries)
    ground_truth_lyrics, ground_truth_sync = split_reference_events(
        ground_truth_entries
    )

    errors = calculate_errors(
        predicted_lyrics,
        ground_truth_lyrics,
    )

    if not errors:
        raise SystemExit("No lyric segments found.")

    absolute_errors = [abs(error) for error in errors]

    mean_absolute_error = sum(absolute_errors) / len(absolute_errors)

    median_absolute_error = calculate_median(absolute_errors)

    maximum_absolute_error = max(absolute_errors)

    mean_signed_error = sum(errors) / len(errors)

    print("V1 ALIGNMENT EVALUATION")
    print("=" * 32)

    print()
    print("REFERENCE STRUCTURE")
    print("-" * 32)
    print(f"Predicted lyric events:     {len(predicted_lyrics)}")
    print(f"Ground-truth lyric events:  {len(ground_truth_lyrics)}")
    print(f"Predicted sync events:      {len(predicted_sync)}")
    print(f"Ground-truth sync events:   {len(ground_truth_sync)}")

    print()
    print("ALIGNMENT ERROR")
    print("-" * 32)
    print(f"Mean absolute error:   {mean_absolute_error:.3f}s")
    print(f"Median absolute error: {median_absolute_error:.3f}s")
    print(f"Maximum absolute error: {maximum_absolute_error:.3f}s")
    print(f"Mean signed error:     {mean_signed_error:+.3f}s")

    print()
    print("ACCURACY THRESHOLDS")
    print("-" * 32)
    print(f"Within ±0.25s: {calculate_percentage_within(errors, 0.25):.1f}%")
    print(f"Within ±0.50s: {calculate_percentage_within(errors, 0.50):.1f}%")
    print(f"Within ±1.00s: {calculate_percentage_within(errors, 1.00):.1f}%")
    print(f"Within ±2.00s: {calculate_percentage_within(errors, 2.00):.1f}%")

    print()
    print("PER-LINE ERROR")
    print("-" * 72)
    print("INDEX | PREDICTED | GROUND TRUTH | SIGNED ERROR | ABS ERROR")
    print("-" * 72)

    for index, (
        (predicted_timestamp, _),
        (ground_truth_timestamp, _),
        error,
    ) in enumerate(
        zip(
            predicted_lyrics,
            ground_truth_lyrics,
            errors,
            strict=True,
        )
    ):
        print(
            f"{index:03d} | "
            f"{predicted_timestamp:9.3f} | "
            f"{ground_truth_timestamp:12.3f} | "
            f"{error:+12.3f} | "
            f"{abs(error):9.3f}"
        )


if __name__ == "__main__":
    main()
