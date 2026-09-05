import numpy as np


def detect_candidates(
    timestamps: np.ndarray,
    boundary_strength: np.ndarray,
    threshold: float = 0.5,
) -> np.ndarray:
    if timestamps.ndim != 1 or boundary_strength.ndim != 1:
        raise ValueError("Timestamps and Boundary Strength must be 1D array.")

    if len(timestamps) != len(boundary_strength):
        raise ValueError(
            "Timestamps and Boundary Strength must always have same length"
        )

    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Threshold must be between 0 and 1.")

    if len(timestamps) < 3:
        return np.array([], dtype=np.float32)

    candidates = []

    for index in range(1, len(boundary_strength) - 1):
        current = boundary_strength[index]

        if (
            current >= threshold
            and current >= boundary_strength[index - 1]
            and current >= boundary_strength[index + 1]
        ):
            candidates.append(timestamps[index])

    return np.asarray(candidates, dtype=np.float32)
