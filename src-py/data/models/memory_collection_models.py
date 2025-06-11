from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, UTC
import json


class MemoryCollectionBase(BaseModel):
    title: str = Field(max_length=255)
    description: str = Field(default="")


class MemoryCollectionCreate(MemoryCollectionBase):
    pass


class MemoryCollectionRead(MemoryCollectionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class MemoryCollectionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = None


class MemoryCollectionWithDocuments(MemoryCollectionRead):
    documents: List["MemoryDocumentRead"] = []


# Import here to avoid circular imports
from .memory_document_models import MemoryDocumentRead
MemoryCollectionWithDocuments.model_rebuild() 