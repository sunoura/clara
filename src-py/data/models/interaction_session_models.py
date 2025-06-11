from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class InteractionSessionBase(BaseModel):
    title: str = Field(max_length=255)
    context_summary: Optional[str] = None


class InteractionSessionCreate(InteractionSessionBase):
    pass


class InteractionSessionRead(InteractionSessionBase):
    id: str
    started_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InteractionSessionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    context_summary: Optional[str] = None


class InteractionSessionWithPayloads(InteractionSessionRead):
    payloads: List["InteractionPayloadRead"] = []


# Import here to avoid circular imports
from .interaction_payload_models import InteractionPayloadRead
InteractionSessionWithPayloads.model_rebuild() 