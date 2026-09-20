from app.alignment.feature_timeline import FeatureTimeline


def print_feature_timeline(timeline: FeatureTimeline) -> None:
    print("timestamp | rms | spectral_flux | onset | boundary")

    for frame in timeline.frames:
        boundary = (
            0.2 * frame.rms + 0.3 * frame.spectral_flux + 0.5 * frame.onset_strength
        )

        print(
            f"{frame.timestamp:8.3f} | "
            f"{frame.rms:.3f} | "
            f"{frame.spectral_flux:.3f} | "
            f"{frame.onset_strength:.3f} | "
            f"{boundary:.3f}"
        )
