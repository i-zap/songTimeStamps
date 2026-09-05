from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    name: str
    score: float = Field(ge=0, le=1)
    source: str
    details: dict[str, str | float | int | bool] = Field(default_factory=dict)


class LocalAlignmentEvidence(BaseModel):
    alignment_id: UUID
    items: list[EvidenceItem] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class GlobalAlignmentEvidence(BaseModel):
    items: list[EvidenceItem] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class AlignmentResult(BaseModel):
    alignments: list[UUID] = Field(default_factory=list)
    local_evidence: list[LocalAlignmentEvidence] = Field(default_factory=list)
    global_evidence: GlobalAlignmentEvidence
