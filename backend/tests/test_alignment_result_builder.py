from uuid import uuid4

import pytest

from app.alignment.result_builder import build_alignments
from app.domain.lyrics import LyricLine


def test_build_alignments_creates_time_ranges():
    document_id = uuid4()

    lyrics = [
        LyricLine(index=0, text="first line"),
        LyricLine(index=1, text="second line"),
        LyricLine(index=2, text="third line"),
    ]

    alignments = build_alignments(
        lyric_lines=lyrics,
        candidate_timestamps=[1.0, 3.0, 5.0],
        document_id=document_id,
        audio_duration=7.0,
        lyric_start=0.0,
        lyric_end=7.0,
    )

    assert len(alignments) == 3

    assert alignments[0].audio_start == pytest.approx(1.0)
    assert alignments[0].audio_end == pytest.approx(3.0)

    assert alignments[1].audio_start == pytest.approx(3.0)
    assert alignments[1].audio_end == pytest.approx(5.0)

    assert alignments[2].audio_start == pytest.approx(5.0)
    assert alignments[2].audio_end == pytest.approx(7.0)


def test_build_alignments_references_correct_lyric_lines():
    document_id = uuid4()

    lyrics = [
        LyricLine(index=0, text="first line"),
        LyricLine(index=1, text="second line"),
    ]

    alignments = build_alignments(
        lyric_lines=lyrics,
        candidate_timestamps=[1.0, 3.0],
        document_id=document_id,
        audio_duration=5.0,
    )

    assert alignments[0].lyric_references[0].document_id == document_id
    assert alignments[0].lyric_references[0].line_id == lyrics[0].id

    assert alignments[1].lyric_references[0].document_id == document_id
    assert alignments[1].lyric_references[0].line_id == lyrics[1].id
