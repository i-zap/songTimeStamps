from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class LyricLine(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    index: int = Field(ge=0)
    text: str


class LyricDocument(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    language: str
    role: Literal["original", "romanized", "translation"]
    lines: list[LyricLine] = Field(default_factory=list)
