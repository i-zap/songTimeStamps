import re
import sys
from pathlib import Path


TIMESTAMP_PATTERN = re.compile(
    r"^\[(\d{2}):(\d{2})\.(\d{2})\](.*)$"
)


def parse_lrc(path: Path) -> list[tuple[float, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()

    entries = []

    for line in lines:
        match = TIMESTAMP_PATTERN.match(line.strip())

        if not match:
            continue

        minutes, seconds, centiseconds, text = match.groups()

        text = text.strip()

        # Ignore timestamp-only markers such as [00:00.00]
        # because they do not represent lyric segments.
        if not text:
            continue

        timestamp = (
            int(minutes) * 60
            + int(seconds)
            + int(centiseconds) / 100
        )

        entries.append((timestamp, text))

    return entries


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
        abs(predicted_timestamp - ground_truth_timestamp)
        for (predicted_timestamp, _),
        (ground_truth_timestamp, _)
        in zip(predicted, ground_truth, strict=True)
    ]


def calculate_percentage_within(
    errors: list[float],
    threshold: float,
) -> float:
    if not errors:
        return 0.0

    count = sum(error <= threshold for error in errors)

    return (count / len(errors)) * 100


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: uv run python experiments/v1/evaluate.py "
            "<predicted.lrc> <ground_truth.lrc>"
        )

    predicted_path = Path(sys.argv[1])
    ground_truth_path = Path(sys.argv[2])

    predicted = parse_lrc(predicted_path)
    ground_truth = parse_lrc(ground_truth_path)

    errors = calculate_errors(predicted, ground_truth)

    if not errors:
        raise SystemExit("No lyric segments found.")

    mean_error = sum(errors) / len(errors)

    sorted_errors = sorted(errors)
    middle = len(sorted_errors) // 2

    if len(sorted_errors) % 2 == 0:
        median_error = (
            sorted_errors[middle - 1] + sorted_errors[middle]
        ) / 2
    else:
        median_error = sorted_errors[middle]

    max_error = max(errors)

    print("V1 ALIGNMENT EVALUATION")
    print("=" * 32)
    print(f"Predicted segments: {len(predicted)}")
    print(f"Ground-truth segments: {len(ground_truth)}")
    print()
    print(f"Mean absolute error:   {mean_error:.3f}s")
    print(f"Median absolute error: {median_error:.3f}s")
    print(f"Maximum absolute error: {max_error:.3f}s")
    print()
    print(
        f"Within ±0.25s: "
        f"{calculate_percentage_within(errors, 0.25):.1f}%"
    )
    print(
        f"Within ±0.50s: "
        f"{calculate_percentage_within(errors, 0.50):.1f}%"
    )
    print(
        f"Within ±1.00s: "
        f"{calculate_percentage_within(errors, 1.00):.1f}%"
    )
    print(
        f"Within ±2.00s: "
        f"{calculate_percentage_within(errors, 2.00):.1f}%"
    )


if __name__ == "__main__":
    main()