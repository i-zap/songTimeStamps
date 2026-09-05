import numpy as np

from app.alignment.audio import AudioSamples
from app.alignment.preprocessing import to_mono


def test_to_mono_converts_stereo_audio():
    audio = AudioSamples(
        sample_rate=44_100,
        samples=np.array(
            [
                [0.2, 0.4],
                [0.6, 0.2],
            ],
            dtype=np.float32,
        ),
        channels=2,
        duration=2 / 44_100,
    )

    mono = to_mono(audio)

    assert mono.dtype == np.float32
    np.testing.assert_allclose(mono, [0.3, 0.4])


def test_to_mono_keeps_mono_audio_mono():
    audio = AudioSamples(
        sample_rate=44_100,
        samples=np.array(
            [
                [0.2],
                [0.4],
            ],
            dtype=np.float32,
        ),
        channels=1,
        duration=2 / 44_100,
    )

    mono = to_mono(audio)

    assert mono.dtype == np.float32
    np.testing.assert_allclose(mono, [0.2, 0.4])
