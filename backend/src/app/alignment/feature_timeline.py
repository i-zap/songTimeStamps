from dataclasses import dataclass

from app.alignment.feature_frame import FeatureFrame


@dataclass
class FeatureTimeline:
    frames: list[FeatureFrame]
