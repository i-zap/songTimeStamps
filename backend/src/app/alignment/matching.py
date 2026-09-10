import numpy as np

from app.domain.lyrics import LyricLine


def match_lyric_lines(
    lyric_lines: list[LyricLine],
    candidate_timestamps: np.ndarray,
    lyric_start: float = 0.0,
    lyric_end: float | None = None,
) -> list[tuple[LyricLine, float]]:
    if candidate_timestamps.ndim != 1:
        raise ValueError("Candidate timestamps must be a 1D array.")

    if lyric_start < 0:
        raise ValueError("Lyric start must not be negative.")

    if lyric_end is not None and lyric_end <= lyric_start:
        raise ValueError("Lyric end must be greater than lyric start.")

    if len(candidate_timestamps) < len(lyric_lines):
        raise ValueError("Not enough timestamps for lyric lines.")

    if lyric_end is None:
        lyric_end = float(candidate_timestamps[-1])

    candidates = candidate_timestamps[
        (candidate_timestamps >= lyric_start) & (candidate_timestamps <= lyric_end)
    ]

    if len(candidates) < len(lyric_lines):
        raise ValueError("Not enough candidates inside lyric region.")

    indices = np.linspace(
        0,
        len(candidates) - 1,
        len(lyric_lines),
        dtype=int,
    )

    matches = []

    for lyric_line, candidate_index in zip(lyric_lines, indices, strict=True):
        matches.append(
            (
                lyric_line,
                float(candidates[candidate_index]),
            )
        )

    return matches
