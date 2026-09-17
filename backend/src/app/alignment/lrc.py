from app.domain.alignment import Alignment
from app.domain.lyrics import LyricLine


def format_lrc_timestamp(seconds: float) -> str:
    if seconds < 0:
        raise ValueError("LRC timestamp cannot be negative.")

    total_centiseconds = round(seconds * 100)

    minutes, remainder = divmod(total_centiseconds, 6000)

    secs, hundredths = divmod(remainder, 100)

    return f"[{minutes:02d}:{secs:02d}.{hundredths:02d}]"


def alignment_to_lrc_line(
    alignment: Alignment,
    lyric_line: LyricLine,
) -> str:
    timestamp = format_lrc_timestamp(alignment.audio_start)
    return f"{timestamp}{lyric_line.text}"


def alignments_to_lrc(
    alignments: list[Alignment],
    lyric_lines: list[LyricLine],
) -> str:
    lines_by_id = {lyric_line.id: lyric_line for lyric_line in lyric_lines}
    lrc_lines = []

    for alignment in alignments:
        if not alignment.lyric_references:
            raise ValueError(f"Alignment {alignment.id} has no lyric references.")

        reference = alignment.lyric_references[0]
        lyric_line = lines_by_id.get(reference.line_id)

        if lyric_line is None:
            raise ValueError(f"Lyric line {reference.line_id} was not found.")

        lrc_lines.append(alignment_to_lrc_line(alignment, lyric_line))

    return "\n".join(lrc_lines) + "\n"
