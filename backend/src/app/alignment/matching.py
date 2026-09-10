import numpy as np

from app.domain.lyrics import LyricLine


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

    if len(candidate_timestamps) < len(lyric_lines):
        raise ValueError("Not enough timestamps for lyric lines.")

    candidates = candidate_timestamps[
        (candidate_timestamps >= lyric_start) & (candidate_timestamps <= lyric_end)
    ]

    if len(candidates) < len(lyric_lines):
        raise ValueError("Not enough candidates inside lyric region.")

    candidates = np.sort(candidates)

    line_count = len(lyric_lines)

    if line_count == 0:
        return []

    target_duration = (lyric_end - lyric_start) / line_count

    min_duration = max(1.0, target_duration * 0.35)
    max_duration = target_duration * 2.0

    dp = np.full((line_count, len(candidates)), np.inf)
    previous = np.full(
        (line_count, len(candidates)),
        -1,
        dtype=np.int32,
    )

    first_candidates = np.where(
        (candidates >= lyric_start) & (candidates <= lyric_start + target_duration)
    )[0]

    for candidate_index in first_candidates:
        distance = candidates[candidate_index] - lyric_start
        dp[0, candidate_index] = distance**2

    for line_index in range(1, line_count):
        for candidate_index in range(len(candidates)):
            current_time = candidates[candidate_index]

            previous_indices = np.where(
                (candidates[:candidate_index] < current_time - min_duration)
                & (candidates[:candidate_index] >= current_time - max_duration)
            )[0]

            if len(previous_indices) == 0:
                continue

            durations = current_time - candidates[previous_indices]

            costs = (
                dp[line_index - 1, previous_indices]
                + (durations - target_duration) ** 2
            )

            best_position = int(np.argmin(costs))
            best_previous = previous_indices[best_position]

            dp[line_index, candidate_index] = costs[best_position]
            previous[line_index, candidate_index] = best_previous

    final_candidates = np.where(np.isfinite(dp[-1]))[0]

    if len(final_candidates) == 0:
        raise ValueError("Not enough candidates inside lyric region.")

    final_index = final_candidates[
        np.argmin(np.abs(candidates[final_candidates] - (lyric_end - target_duration)))
    ]

    selected_indices = []

    current_index = int(final_index)

    for line_index in range(line_count - 1, -1, -1):
        selected_indices.append(current_index)
        current_index = previous[line_index, current_index]

        if line_index > 0 and current_index < 0:
            raise ValueError("Unable to reconstruct lyric alignment.")

    selected_indices.reverse()

    matches = []

    for lyric_line, candidate_index in zip(
        lyric_lines,
        selected_indices,
        strict=True,
    ):
        matches.append(
            (
                lyric_line,
                float(candidates[candidate_index]),
            )
        )

    return matches
