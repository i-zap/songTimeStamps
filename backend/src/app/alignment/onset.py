import numpy as np


def calculate_onset_strength(frames: np.ndarray) -> np.ndarray:
    if frames.ndim != 2:
        raise ValueError("Audio frames must be a 2D array.")

    if len(frames) == 0:
        return np.array([], dtype=np.float32)

    spectrum = np.abs(np.fft.rfft(frames, axis=1))

    onset = np.zeros(len(frames), dtype=np.float32)

    if len(frames) > 1:
        differences = np.diff(spectrum, axis=0)
        positive_changes = np.maximum(differences, 0)
        onset[1:] = np.sum(positive_changes, axis=1)

    return onset
