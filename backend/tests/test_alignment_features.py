import numpy as np

from app.alignment.features import frame_audio


def test_frame_audio_creates_overlapping_frames():
    samples = np.arange(10, dtype=np.float32)

    frames = frame_audio(
        samples,
        frame_size=4,
        hop_size=2,
    )

    expected = np.array(
        [
            [0, 1, 2, 3],
            [2, 3, 4, 5],
            [4, 5, 6, 7],
            [6, 7, 8, 9],
        ],
        dtype=np.float32,
    )

    np.testing.assert_array_equal(frames, expected)


def test_frame_audio_rejects_stereo_input():
    samples = np.zeros((10, 2), dtype=np.float32)

    try:
        frame_audio(samples)
    except ValueError as error:
        assert str(error) == "Audio samples must be mono."
    else:
        raise AssertionError("Expected stereo input to be rejected.")
