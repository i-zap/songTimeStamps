import numpy as np


def calculate_spectral_flux(frames: np.ndarray) -> np.ndarray:
    if frames.ndim != 2:
        raise ValueError("Audio frames must be a 2D array.")

    if len(frames) == 0:
        return np.array([], dtype=np.float32)

    spectrum = np.abs(np.fft.rfft(frames, axis=1))

    spectrum_sum = np.sum(spectrum, axis=1, keepdims=True)
    normalized_spectrum = spectrum / np.maximum(spectrum_sum, 1e-12)

    flux = np.zeros(len(frames), dtype=np.float32)

    if len(frames) > 1:
        differences = np.diff(normalized_spectrum, axis=0)
        flux[1:] = np.sqrt(np.sum(np.maximum(differences, 0) ** 2, axis=1))
    return flux
