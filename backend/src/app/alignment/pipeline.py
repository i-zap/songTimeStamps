import numpy as np

from app.alignment.audio import AudioSamples
from app.alignment.candidates import detect_candidates
from app.alignment.feature_frame import FeatureFrame
from app.alignment.feature_timeline import FeatureTimeline
from app.alignment.features import frame_audio
from app.alignment.onset import calculate_onset_strength
from app.alignment.preprocessing import to_mono
from app.alignment.result_builder import build_alignments
from app.alignment.rms import calculate_rms
from app.alignment.signal import calculate_boundary_strength
from app.alignment.spectral import calculate_spectral_flux
from app.domain.alignment import Alignment
from app.domain.lyrics import LyricDocument


def build_feature_timeline(
    audio: AudioSamples,
    frame_size: int = 1024,
    hop_size: int = 512,
) -> FeatureTimeline:
    mono_samples = to_mono(audio)

    frames = frame_audio(
        mono_samples,
        frame_size=frame_size,
        hop_size=hop_size,
    )

    rms = calculate_rms(frames)
    spectral_flux = calculate_spectral_flux(frames)
    onset_strength = calculate_onset_strength(frames)

    feature_frames = []

    frame_duration = hop_size / audio.sample_rate

    for index in range(len(frames)):
        feature_frames.append(
            FeatureFrame(
                timestamp=index * frame_duration,
                rms=float(rms[index]),
                spectral_flux=float(spectral_flux[index]),
                onset_strength=float(onset_strength[index]),
            )
        )

    return FeatureTimeline(frames=feature_frames)


def find_candidates_timestamps(
    audio: AudioSamples,
    frame_size: int = 1024,
    hop_size: int = 512,
    threshold: float = 0.5,
) -> np.ndarray:
    timeline = build_feature_timeline(
        audio,
        frame_size=frame_size,
        hop_size=hop_size,
    )

    rms = np.array(
        [frame.rms for frame in timeline.frames],
        dtype=np.float32,
    )

    spectral_flux = np.array(
        [frame.spectral_flux for frame in timeline.frames],
        dtype=np.float32,
    )

    onset_strength = np.array(
        [frame.onset_strength for frame in timeline.frames],
        dtype=np.float32,
    )

    boundary_strength = calculate_boundary_strength(
        rms,
        spectral_flux,
        onset_strength,
    )

    timestamps = np.array(
        [frame.timestamp for frame in timeline.frames],
        dtype=np.float32,
    )

    return detect_candidates(
        timestamps,
        boundary_strength,
        threshold=threshold,
        min_spacing=0.5,
    )


def build_alignment(
    audio: AudioSamples,
    lyrics: LyricDocument,
    frame_size: int = 1024,
    hop_size: int = 512,
    threshold: float = 0.5,
    lyric_start: float = 0.0,
    lyric_end: float | None = None,
) -> list[Alignment]:
    candidate_timestamps = find_candidates_timestamps(
        audio,
        frame_size=frame_size,
        hop_size=hop_size,
        threshold=threshold,
    )

    return build_alignments(
        lyric_lines=lyrics.lines,
        candidate_timestamps=candidate_timestamps,
        document_id=lyrics.id,
        audio_duration=audio.duration,
        lyric_start=lyric_start,
        lyric_end=lyric_end,
    )
