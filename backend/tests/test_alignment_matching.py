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
        [1.2, 2.8, 4.1],
        dtype=np.float32,
    )

    matches = match_lyric_lines(lyrics, timestamps)

    assert matches[0][0].text == "first line"
    assert matches[0][1] == pytest.approx(1.2)

    assert matches[1][0].text == "second line"
    assert matches[1][1] == pytest.approx(2.8)

    assert matches[2][0].text == "third line"
    assert matches[2][1] == pytest.approx(4.1)
