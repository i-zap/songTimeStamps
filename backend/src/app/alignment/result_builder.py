from uuid import UUID

import numpy as np

from app.alignment.matching import match_lyric_lines
from app.domain.alignment import Alignment
from app.domain.lyrics import LyricLine


def build_alignments(
    lyric_lines: list[LyricLine],
    candidate_timestamps: list[float],
    document_id: UUID,
    audio_duration: float,
) -> list[Alignment]:
    if len(candidate_timestamps) == 0:
        raise ValueError("Candidate timestamps cannot be empty.")

    if audio_duration <= 0:
        raise ValueError("Audio duration must be positive.")

    if len(candidate_timestamps) < len(lyric_lines):
        raise ValueError("Not enough candidate timestamps for lyric lines.")

    matches = match_lyric_lines(
        lyric_lines,
        np.asarray(candidate_timestamps, dtype=np.float32),
    )

    alignments = []

    for index, (lyric_line, audio_start) in enumerate(matches):
        if index + 1 < len(matches):
            audio_end = matches[index + 1][1]
        else:
            audio_end = audio_duration

        if audio_end <= audio_start:
            raise ValueError("Alignment timestamps must be increasing.")

        alignments.append(
            Alignment(
                audio_start=audio_start,
                audio_end=audio_end,
                lyric_references=[
                    {
                        "document_id": document_id,
                        "line_id": lyric_line.id,
                    }
                ],
                confidence=0.5,
                method="v1_candidate_order",
            )
        )

    return alignments
