import numpy as np
import pytest

from app.alignment.candidates import detect_candidates


def test_detect_candidates_finds_local_peaks():
    timestamps = np.array([0, 1, 2, 3, 4], dtype=np.float32)
    strength = np.array([0.1, 0.2, 0.9, 0.2, 0.1], dtype=np.float32)

    candidates = detect_candidates(timestamps, strength)

    np.testing.assert_allclose(candidates, [2.0])


def test_detect_candidates_ignores_values_below_threshold():
    timestamps = np.array([0, 1, 2], dtype=np.float32)
    strength = np.array([0.1, 0.4, 0.1], dtype=np.float32)

    candidates = detect_candidates(timestamps, strength)

    assert len(candidates) == 0


def test_detect_candidates_rejects_mismatched_lengths():
    timestamps = np.array([0, 1], dtype=np.float32)
    strength = np.array([0.1], dtype=np.float32)

    with pytest.raises(ValueError, match="same length"):
        detect_candidates(timestamps, strength)


def test_detect_candidates_rejects_invalid_threshold():
    timestamps = np.array([0, 1, 2], dtype=np.float32)
    strength = np.array([0.1, 0.9, 0.1], dtype=np.float32)

    with pytest.raises(ValueError, match="between 0 and 1"):
        detect_candidates(timestamps, strength, threshold=1.5)


def test_detect_candidates_enforces_minimum_spacing():
    timestamps = np.array([0, 1, 1.2, 2.5, 3.0], dtype=np.float32)
    strength = np.array([0.1, 0.9, 0.8, 0.9, 0.1], dtype=np.float32)

    candidates = detect_candidates(
        timestamps,
        strength,
        min_spacing=1.0,
    )

    np.testing.assert_allclose(candidates, [1.0, 2.5])
