import sys
from pathlib import Path

from app.alignment.audio import load_audio
from app.alignment.pipeline import build_alignment
from app.domain.lyrics import LyricDocument, LyricLine


def load_lyrics(path: Path) -> LyricDocument:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    lyric_lines = [
        LyricLine(index=index, text=text) for index, text in enumerate(lines)
    ]

    return LyricDocument(
        language="unknown",
        role="original",
        lines=lyric_lines,
    )


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: uv run python experiments/v1/run.py <audio> <lyrics>")
        raise SystemExit(1)

    audio_path = Path(sys.argv[1])
    lyrics_path = Path(sys.argv[2])

    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}")
        raise SystemExit(1)

    if not lyrics_path.exists():
        print(f"Lyrics file not found: {lyrics_path}")
        raise SystemExit(1)

    audio = load_audio(audio_path)
    lyrics = load_lyrics(lyrics_path)

    alignments = build_alignment(
        audio=audio,
        lyrics=lyrics,
    )

    print(f"Audio duration: {audio.duration:.3f}s")
    print(f"Audio sample rate: {audio.sample_rate}")
    print(f"Lyric lines: {len(lyrics.lines)}")
    print(f"Alignments: {len(alignments)}")
    print()

    for alignment in alignments:
        reference = alignment.lyric_references[0]

        lyric_line = next(line for line in lyrics.lines if line.id == reference.line_id)

        print(
            f"{alignment.audio_start:8.3f}s → "
            f"{alignment.audio_end:8.3f}s | "
            f"{lyric_line.index:03d} | "
            f"{lyric_line.text}"
        )


if __name__ == "__main__":
    main()
