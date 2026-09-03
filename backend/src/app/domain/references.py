from uuid import UUID

from pydantic import BaseModel


class LyricReference(BaseModel):
    document_id: UUID
    line_id: UUID
