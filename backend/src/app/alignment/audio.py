from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf


@dataclass
class AudioSamples:
    sample_rate: int
    samples: np.ndarray
    channels: int
    duration: float


def load_audio(path: Path) -> AudioSamples:
    samples, sample_rate = sf.read(
        path,
        dtype="float32",
        always_2d=True,
    )

    channels = samples.shape[1]
    duration = samples.shape[0] / sample_rate

    return AudioSamples(
        sample_rate=sample_rate,
        samples=samples,
        channels=channels,
        duration=duration,
    )
