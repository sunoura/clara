from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, UTC
import json


class MemoryDocumentBase(BaseModel):
    chroma_id: str = Field(max_length=255)
    content: str
    collection_id: int
    metadatas: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MemoryDocumentCreate(MemoryDocumentBase):
    pass


class MemoryDocumentRead(MemoryDocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('metadatas', mode='before')
    @classmethod
    def parse_metadatas(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}


class MemoryDocumentUpdate(BaseModel):
    chroma_id: Optional[str] = Field(default=None, max_length=255)
    content: Optional[str] = None
    collection_id: Optional[int] = None
    metadatas: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = None


class MemoryDocumentWithCollection(MemoryDocumentRead):
    collection: Optional["MemoryCollectionRead"] = None


# Import here to avoid circular imports
from .memory_collection_models import MemoryCollectionRead
MemoryDocumentWithCollection.model_rebuild() 