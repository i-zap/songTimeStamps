from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.alignment import Alignment
from app.domain.audio import AudioAsset
from app.domain.lyrics import LyricDocument


class Project(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    audio: AudioAsset | None = None
    lyric_documents: list[LyricDocument] = Field(default_factory=list)
    alignments: list[Alignment] = Field(default_factory=list)
