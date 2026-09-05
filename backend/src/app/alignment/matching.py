import numpy as np

from app.domain.lyrics import LyricLine


def match_lyric_lines(
    lyric_lines: list[LyricLine],
    candidate_timestamps: np.ndarray,
) -> list[tuple[LyricLine, float]]:
    if candidate_timestamps.ndim != 1:
        raise ValueError("Candidate timestamps must be a 1D array.")

    if len(candidate_timestamps) < len(lyric_lines):
        raise ValueError("Not enough timestamps for lyric lines.")

    matches = []

    for index, lyric_line in enumerate(lyric_lines):
        matches.append(
            (
                lyric_line,
                float(candidate_timestamps[index]),
            )
        )

    return matches
