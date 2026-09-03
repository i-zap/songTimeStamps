import numpy as np


def calculate_rms(frames: np.ndarray) -> np.ndarray:
    if frames.ndim != 2:
        raise ValueError("Audio frames must be a 2D array.")
    return np.sqrt(np.mean(np.square(frames), axis=1))
