from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from ._schemas import InteractionFrom


class InteractionPayloadBase(BaseModel):
    session_id: str
    content: str
    ok: bool = Field(default=True)
    err: Optional[str] = None
    from_: InteractionFrom = Field(alias="from")


class InteractionPayloadCreate(InteractionPayloadBase):
    pass


class InteractionPayloadRead(InteractionPayloadBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class InteractionPayloadUpdate(BaseModel):
    content: Optional[str] = None
    ok: Optional[bool] = None
    err: Optional[str] = None
    from_: Optional[InteractionFrom] = Field(default=None, alias="from")


class InteractionPayloadWithSession(InteractionPayloadRead):
    session: Optional["InteractionSessionRead"] = None


# Import here to avoid circular imports
from .interaction_session_models import InteractionSessionRead
InteractionPayloadWithSession.model_rebuild() 