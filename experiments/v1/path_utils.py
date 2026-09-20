from pathlib import Path

V1_ROOT = Path(__file__).resolve().parent
V1_DATA_DIR = V1_ROOT / "data"
V1_RESULTS_DIR = V1_ROOT / "results"


def resolve_data_file(path: str | Path) -> Path:
    return _resolve_within(path, V1_DATA_DIR)


def resolve_result_file(path: str | Path) -> Path:
    return _resolve_within(path, V1_RESULTS_DIR)


def _resolve_within(path: str | Path, allowed_root: Path) -> Path:
    candidate = Path(path)

    if not candidate.is_absolute():
        candidate = V1_ROOT.parent.parent / candidate

    candidate = candidate.resolve()
    allowed_root = allowed_root.resolve()

    try:
        candidate.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError(f"Path must be inside {allowed_root}: {candidate}") from exc

    return candidate
