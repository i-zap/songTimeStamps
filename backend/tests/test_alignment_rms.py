import numpy as np

from app.alignment.rms import calculate_rms


def test_calculate_rms():
    frames = np.array(
        [
            [1.0, 1.0, 1.0, 1.0],
            [0.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float32,
    )

    rms = calculate_rms(frames)

    np.testing.assert_allclose(rms, [1.0, 0.0])


def test_calculate_rms_handles_multiple_frames():
    frames = np.array(
        [
            [1.0, -1.0],
            [0.5, -0.5],
        ],
        dtype=np.float32,
    )

    rms = calculate_rms(frames)

    np.testing.assert_allclose(
        rms,
        [1.0, 0.5],
    )
