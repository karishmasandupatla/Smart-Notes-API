from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Note(BaseModel):
    text: str = Field(..., min_length=8, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class NoteResponse(BaseModel):
    id: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None