from app.alignment.feature_frame import FeatureFrame
from app.alignment.feature_timeline import FeatureTimeline


def test_feature_frame_stores_features():
    frame = FeatureFrame(
        timestamp=1.25,
        rms=0.4,
        spectral_flux=0.2,
        onset_strength=0.8,
    )

    assert frame.timestamp == 1.25
    assert frame.rms == 0.4
    assert frame.spectral_flux == 0.2
    assert frame.onset_strength == 0.8


def test_feature_timeline_stores_feature_frames():
    frame = FeatureFrame(
        timestamp=1.25,
        rms=0.4,
        spectral_flux=0.2,
        onset_strength=0.8,
    )

    timeline = FeatureTimeline(frames=[frame])

    assert len(timeline.frames) == 1
    assert timeline.frames[0] == frame
