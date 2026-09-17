import numpy as np

from app.domain.lyrics import LyricLine


def _line_weight(lyric_line: LyricLine) -> float:
    text = " ".join(lyric_line.text.split())
    if not text:
        return 1.0
    return float(max(len(text), 1))


def match_lyric_lines(
    lyric_lines: list[LyricLine],
    candidate_timestamps: np.ndarray,
    lyric_start: float,
    lyric_end: float,
) -> list[tuple[LyricLine, float]]:
    if candidate_timestamps.ndim != 1:
        raise ValueError("Candidate timestamps must be a 1D array.")
    if lyric_start < 0:
        raise ValueError("Lyric start must not be negative.")
    if lyric_end <= lyric_start:
        raise ValueError("Lyric end must be greater than lyric start.")
    if len(candidate_timestamps) == 0:
        raise ValueError("Candidate timestamps cannot be empty.")
    if len(candidate_timestamps) < len(lyric_lines):
        raise ValueError("Not enough timestamps for lyric lines.")

    candidates = candidate_timestamps[
        (candidate_timestamps >= lyric_start) & (candidate_timestamps <= lyric_end)
    ]
    if len(candidates) < len(lyric_lines):
        raise ValueError("Not enough candidates inside lyric region.")

    if len(lyric_lines) == 0:
        return []
    if len(lyric_lines) == 1:
        return [(lyric_lines[0], float(candidates[0]))]

    line_weights = np.asarray(
        [_line_weight(line) for line in lyric_lines],
        dtype=np.float64,
    )
    total_weight = float(np.sum(line_weights))
    total_duration = lyric_end - lyric_start

    expected_positions = np.cumsum(line_weights) / total_weight
    expected_positions -= line_weights / total_weight
    expected_timestamps = lyric_start + expected_positions * total_duration

    candidate_count = len(candidates)
    lyric_count = len(lyric_lines)

    costs = np.full((lyric_count, candidate_count), np.inf, dtype=np.float64)
    previous = np.full((lyric_count, candidate_count), -1, dtype=np.int64)

    for candidate_index in range(candidate_count):
        costs[0, candidate_index] = abs(
            float(candidates[candidate_index]) - float(expected_timestamps[0])
        )

    for lyric_index in range(1, lyric_count):
        expected_gap_seconds = (
            float(line_weights[lyric_index - 1]) / total_weight
        ) * total_duration

        for candidate_index in range(lyric_index, candidate_count):
            current_timestamp = float(candidates[candidate_index])
            previous_candidates = np.arange(lyric_index - 1, candidate_index)

            if len(previous_candidates) == 0:
                continue

            transition_costs = costs[lyric_index - 1, previous_candidates]
            previous_timestamps = candidates[previous_candidates]

            gap = current_timestamp - previous_timestamps

            gap_cost = np.abs(
                np.log(np.maximum(gap, 1e-6)) - np.log(max(expected_gap_seconds, 1e-6))
            )

            total_costs = transition_costs + gap_cost
            best_position = int(np.argmin(total_costs))
            best_previous = int(previous_candidates[best_position])

            costs[lyric_index, candidate_index] = total_costs[best_position]
            previous[lyric_index, candidate_index] = best_previous

    final_index = int(np.argmin(costs[-1]))
    if not np.isfinite(costs[-1, final_index]):
        raise ValueError("Unable to match lyric lines to candidate timestamps.")

    selected_indices = np.empty(lyric_count, dtype=np.int64)
    selected_indices[-1] = final_index

    for lyric_index in range(lyric_count - 1, 0, -1):
        selected_indices[lyric_index - 1] = previous[
            lyric_index, selected_indices[lyric_index]
        ]

    matches = []
    for lyric_line, candidate_index in zip(lyric_lines, selected_indices, strict=True):
        matches.append((lyric_line, float(candidates[candidate_index])))

    return matches
