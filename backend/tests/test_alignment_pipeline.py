import numpy as np

from app.alignment.audio import AudioSamples
from app.alignment.pipeline import build_alignment
from app.domain.lyrics import LyricDocument, LyricLine


def test_build_alignment_creates_alignments():
    sample_rate = 44_100

    samples = np.zeros(7 * sample_rate, dtype=np.float32)

    samples[1 * sample_rate : 2 * sample_rate] = 1.0
    samples[3 * sample_rate : 4 * sample_rate] = 1.0
    samples[5 * sample_rate : 6 * sample_rate] = 1.0

    audio = AudioSamples(
        sample_rate=sample_rate,
        samples=samples.reshape(-1, 1),
        channels=1,
        duration=7.0,
    )

    lyrics = LyricDocument(
        language="en",
        role="original",
        lines=[
            LyricLine(index=0, text="first line"),
            LyricLine(index=1, text="second line"),
            LyricLine(index=2, text="third line"),
        ],
    )

    alignments = build_alignment(
        audio=audio,
        lyrics=lyrics,
    )

    assert isinstance(alignments, list)
    assert len(alignments) == 3
