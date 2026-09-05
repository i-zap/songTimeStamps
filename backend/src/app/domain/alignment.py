from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.references import LyricReference


class Alignment(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    audio_start: float = Field(ge=0)
    audio_end: float = Field(gt=0)

    lyric_references: list[LyricReference] = Field(min_length=1)

    confidence: float = Field(ge=0, le=1)

    method: str
