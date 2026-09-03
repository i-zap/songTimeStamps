from pathlib import Path
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AudioAsset(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    path: Path
    format: str
    duration: float = Field(gt=0)
