import numpy as np

from app.alignment.audio import AudioSamples


def to_mono(audio: AudioSamples) -> np.ndarray:
    if audio.channels == 1:
        return audio.samples[:, 0]

    return np.mean(audio.samples, axis=1)
