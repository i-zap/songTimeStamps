import numpy as np

from app.alignment.onset import calculate_onset_strength


def test_calculate_onset_strength_returns_zero_for_first_frame():
    frames = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float32,
    )

    onset = calculate_onset_strength(frames)

    assert onset[0] == 0.0


def test_calculate_onset_strength_detects_positive_spectral_change():
    frames = np.array(
        [
            [0.0, 0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0, 1.0],
        ],
        dtype=np.float32,
    )

    onset = calculate_onset_strength(frames)

    assert onset[1] > 0.0


def test_calculate_onset_strength_ignores_decreasing_energy():
    frames = np.array(
        [
            [1.0, 1.0, 1.0, 1.0],
            [0.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float32,
    )

    onset = calculate_onset_strength(frames)

    assert onset[1] == 0.0
