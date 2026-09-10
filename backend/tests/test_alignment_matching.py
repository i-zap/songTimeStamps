import numpy as np
import pytest

from app.alignment.matching import match_lyric_lines
from app.domain.lyrics import LyricLine


def test_match_lyric_lines_assigns_candidates_in_order():
    lyrics = [
        LyricLine(index=0, text="first line"),
        LyricLine(index=1, text="second line"),
        LyricLine(index=2, text="third line"),
    ]

    timestamps = np.array(
        [1.2, 2.8, 4.1, 5.7, 7.3],
        dtype=np.float32,
    )

    matches = match_lyric_lines(
        lyrics,
        timestamps,
        lyric_start=2.0,
        lyric_end=6.0,
    )

    assert matches[0][0].text == "first line"
    assert matches[0][1] == pytest.approx(2.8)

    assert matches[1][0].text == "second line"
    assert matches[1][1] == pytest.approx(4.1)

    assert matches[2][0].text == "third line"
    assert matches[2][1] == pytest.approx(5.7)


def test_match_lyric_lines_rejects_invalid_region():
    lyrics = [
        LyricLine(index=0, text="first line"),
    ]

    timestamps = np.array(
        [1.0, 2.0],
        dtype=np.float32,
    )

    with pytest.raises(ValueError, match="greater than lyric start"):
        match_lyric_lines(
            lyrics,
            timestamps,
            lyric_start=5.0,
            lyric_end=4.0,
        )


def test_match_lyric_lines_rejects_too_few_candidates_in_region():
    lyrics = [
        LyricLine(index=0, text="first line"),
        LyricLine(index=1, text="second line"),
        LyricLine(index=2, text="third line"),
    ]

    timestamps = np.array(
        [1.0, 2.0, 3.0, 10.0, 11.0],
        dtype=np.float32,
    )

    with pytest.raises(ValueError, match="inside lyric region"):
        match_lyric_lines(
            lyrics,
            timestamps,
            lyric_start=0.0,
            lyric_end=2.5,
        )
