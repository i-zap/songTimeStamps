import numpy as np


def normalize_feature(values: np.ndarray) -> np.ndarray:
    if values.ndim != 1:
        raise ValueError("Feature values must be a 1D array.")

    if len(values) == 0:
        return np.array([], dtype=np.float32)

    minimum = np.min(values)
    maximum = np.max(values)

    if maximum == minimum:
        return np.zeros_like(values, dtype=np.float32)

    return ((values - minimum) / (maximum - minimum)).astype(np.float32)


def calculate_boundary_strength(
    rms: np.ndarray, spectral_flux: np.ndarray, onset_strength: np.ndarray
) -> np.ndarray:
    if not (rms.ndim == 1 and spectral_flux.ndim == 1 and onset_strength.ndim == 1):
        raise ValueError("All features must be 1D array.")

    if not (len(rms) == len(spectral_flux) == len(onset_strength)):
        raise ValueError("All features must have the same length.")

    normalized_rms = normalize_feature(rms)
    normalized_flux = normalize_feature(spectral_flux)
    normalized_onset = normalize_feature(onset_strength)

    return (
        0.2 * normalized_rms + 0.3 * normalized_flux + 0.5 * normalized_onset
    ).astype(np.float32)
