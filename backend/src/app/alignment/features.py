import numpy as np

DEFAULT_FRAME_SIZE = 2048
DEFAULT_HOP_SIZE = 512


def frame_audio(
    samples: np.ndarray,
    frame_size: int = DEFAULT_FRAME_SIZE,
    hop_size: int = DEFAULT_HOP_SIZE,
) -> np.ndarray:
    if samples.ndim != 1:
        raise ValueError("Audio samples must be mono.")

    if frame_size <= 0:
        raise ValueError("Frame size must be positive.")

    if hop_size <= 0:
        raise ValueError("Hop size m`ust be positive.")

    if len(samples) < frame_size:
        return np.empty((0, frame_size), dtype=samples.dtype)

    frame_count = 1 + (len(samples) - frame_size) // hop_size

    frames = np.empty(
        (frame_count, frame_size),
        dtype=samples.dtype,
    )

    for index in range(frame_count):
        start = index * hop_size
        frames[index] = samples[start : start + frame_size]
    return frames
