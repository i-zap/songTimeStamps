import json
import sys
from pathlib import Path

from app.alignment.audio import load_audio
from app.alignment.lrc import alignments_to_lrc
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

    lyric_start = 17.15
    lyric_end = 233.47

    alignments = build_alignment(
        audio=audio,
        lyrics=lyrics,
        lyric_start=lyric_start,
        lyric_end=lyric_end,
    )

    # ------------------------------------------------------------------
    # Generate experiment artifacts
    # ------------------------------------------------------------------
    results_dir = Path("experiments/v1/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Human-readable LRC prediction
    lrc_text = alignments_to_lrc(
        alignments=alignments,
        lyric_lines=lyrics.lines,
    )
    predicted_lrc_path = results_dir / "predicted.lrc"
    predicted_lrc_path.write_text(
        lrc_text,
        encoding="utf-8",
    )

    # Machine-readable prediction/evidence
    predicted_json_path = results_dir / "predicted.json"
    predicted_json = {
        "version": "v1",
        "audio": {
            "filename": audio_path.name,
            "duration": audio.duration,
            "sample_rate": audio.sample_rate,
        },
        "lyrics": {
            "filename": lyrics_path.name,
            "document_id": str(lyrics.id),
            "line_count": len(lyrics.lines),
        },
        "lyric_region": {
            "start": lyric_start,
            "end": lyric_end,
        },
        "alignments": [
            {
                "id": str(alignment.id),
                "audio_start": alignment.audio_start,
                "audio_end": alignment.audio_end,
                "confidence": alignment.confidence,
                "method": alignment.method,
                "lyric_references": [
                    {
                        "document_id": str(reference.document_id),
                        "line_id": str(reference.line_id),
                    }
                    for reference in alignment.lyric_references
                ],
            }
            for alignment in alignments
        ],
    }
    predicted_json_path.write_text(
        json.dumps(
            predicted_json,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # ------------------------------------------------------------------
    # Terminal output
    # ------------------------------------------------------------------
    print(f"Audio duration: {audio.duration:.3f}s")
    print(f"Audio sample rate: {audio.sample_rate}")
    print(f"Lyric lines: {len(lyrics.lines)}")
    print(f"Lyric region: {lyric_start:.2f}s → {lyric_end:.2f}s")
    print(f"Alignments: {len(alignments)}")
    print()

    for alignment in alignments:
        reference = alignment.lyric_references[0]
        lyric_line = next(
            line for line in lyrics.lines if line.id == reference.line_id
        )
        print(
            f"{alignment.audio_start:8.3f}s → "
            f"{alignment.audio_end:8.3f}s | "
            f"{lyric_line.index:03d} | "
            f"{lyric_line.text}"
        )

    print()
    print(f"Prediction LRC: {predicted_lrc_path}")
    print(f"Prediction JSON: {predicted_json_path}")


if __name__ == "__main__":
    main()
