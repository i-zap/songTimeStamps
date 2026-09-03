from app.alignment.audio import AudioSamples


def test_audio_samples_support_multichannel_audio():
    audio = AudioSamples(
        sample_rate=44_100,
        samples=[[0.1, 0.2], [0.3, 0.4]],
        channels=2,
        duration=2 / 44_100,
    )

    assert audio.sample_rate == 44_100
    assert audio.channels == 2
    assert len(audio.samples) == 2
    assert audio.duration == 2 / 44_100
