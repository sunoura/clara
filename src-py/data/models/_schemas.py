from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, UTC
from enum import Enum
import uuid


# Enums
class InteractionFrom(str, Enum):
    USER = "user"
    MODEL = "model"


# Database Tables
class MemoryCollection(SQLModel, table=True):
    __tablename__ = "memory_collections"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    documents: List["MemoryDocument"] = Relationship(back_populates="collection")


class MemoryDocument(SQLModel, table=True):
    __tablename__ = "memory_documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    chroma_id: str = Field(max_length=255, index=True)
    content: str
    collection_id: int = Field(foreign_key="memory_collections.id")
    metadatas: str = Field(default="{}")  # Stringified JSON
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    collection: Optional[MemoryCollection] = Relationship(back_populates="documents")


class InteractionSession(SQLModel, table=True):
    __tablename__ = "interaction_sessions"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(max_length=255)
    context_summary: Optional[str] = Field(default=None)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # Relationships
    payloads: List["InteractionPayload"] = Relationship(back_populates="session")


class InteractionPayload(SQLModel, table=True):
    __tablename__ = "interaction_payloads"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="interaction_sessions.id")
    content: str
    ok: bool = Field(default=True)
    err: Optional[str] = Field(default=None)
    from_: InteractionFrom = Field(alias="from")  # Using alias to avoid Python keyword conflict
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # Relationships
    session: Optional[InteractionSession] = Relationship(back_populates="payloads")
