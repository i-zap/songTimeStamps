from dataclasses import dataclass


@dataclass
class FeatureFrame:
    timestamp: float
    rms: float
    spectral_flux: float
    onset_strength: float
