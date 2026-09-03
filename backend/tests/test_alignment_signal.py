import numpy as np
import pytest

from app.alignment.signal import (
    calculate_boundary_strength,
    normalize_feature,
)


def test_normalize_feature_scales_values_between_zero_and_one():
    values = np.array([10.0, 20.0, 30.0], dtype=np.float32)

    normalized = normalize_feature(values)

    np.testing.assert_allclose(
        normalized,
        [0.0, 0.5, 1.0],
    )


def test_normalize_feature_handles_constant_values():
    values = np.array([5.0, 5.0, 5.0], dtype=np.float32)

    normalized = normalize_feature(values)

    np.testing.assert_allclose(
        normalized,
        [0.0, 0.0, 0.0],
    )


def test_boundary_strength_combines_features():
    rms = np.array([0.0, 1.0], dtype=np.float32)
    flux = np.array([0.0, 1.0], dtype=np.float32)
    onset = np.array([0.0, 1.0], dtype=np.float32)

    strength = calculate_boundary_strength(rms, flux, onset)

    np.testing.assert_allclose(
        strength,
        [0.0, 1.0],
    )


def test_boundary_strength_rejects_different_lengths():
    rms = np.array([0.0, 1.0], dtype=np.float32)
    flux = np.array([0.0], dtype=np.float32)
    onset = np.array([0.0, 1.0], dtype=np.float32)

    with pytest.raises(ValueError, match="same length"):
        calculate_boundary_strength(rms, flux, onset)
