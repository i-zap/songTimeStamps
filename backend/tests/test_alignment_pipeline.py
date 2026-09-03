import numpy as np

from app.alignment.audio import AudioSamples
from app.alignment.pipeline import build_feature_timeline


def test_build_feature_timeline_creates_frames():
    audio = AudioSamples(
        sample_rate=1000,
        samples=np.ones((4000, 1), dtype=np.float32),
        channels=1,
        duration=4.0,
    )

    timeline = build_feature_timeline(
        audio,
        frame_size=1000,
        hop_size=500,
    )

    assert len(timeline.frames) > 0
    assert timeline.frames[0].timestamp == 0.0
