import numpy as np

from app.alignment.spectral import calculate_spectral_flux


def test_calculate_spectral_flux_returns_zero_for_first_frame():
    frames = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float32,
    )

    flux = calculate_spectral_flux(frames)

    assert flux[0] == 0.0


def test_calculate_spectral_flux_detects_spectral_change():
    frames = np.array(
        [
            [1.0, 1.0, 1.0, 1.0],
            [1.0, -1.0, 1.0, -1.0],
        ],
        dtype=np.float32,
    )

    flux = calculate_spectral_flux(frames)

    assert flux[1] > 0.0


def test_calculate_spectral_flux_returns_zero_for_identical_frames():
    frames = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float32,
    )

    flux = calculate_spectral_flux(frames)

    np.testing.assert_allclose(flux, [0.0, 0.0])
