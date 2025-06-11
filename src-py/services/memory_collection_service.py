from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, UTC

from data.models import (
    MemoryCollection, 
    MemoryCollectionCreate, 
    MemoryCollectionUpdate,
)


class MemoryCollectionService:
    def create_collection(self, session: Session, collection_data: MemoryCollectionCreate) -> MemoryCollection:
        """Create a new memory collection"""
        db_collection = MemoryCollection.model_validate(collection_data)
        session.add(db_collection)
        session.commit()
        session.refresh(db_collection)
        return db_collection
    
    def get_collection(self, session: Session, collection_id: int) -> Optional[MemoryCollection]:
        """Get a memory collection by ID"""
        return session.get(MemoryCollection, collection_id)
    
    def get_collections(self, session: Session, skip: int = 0, limit: int = 100) -> List[MemoryCollection]:
        """Get all memory collections"""
        statement = select(MemoryCollection).where(MemoryCollection.archived_at.is_(None)).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def update_collection(self, session: Session, collection_id: int, collection_data: MemoryCollectionUpdate) -> Optional[MemoryCollection]:
        """Update a memory collection"""
        collection = session.get(MemoryCollection, collection_id)
        if collection:
            update_data = collection_data.model_dump(exclude_unset=True)
            update_data['updated_at'] = datetime.now(UTC)
            for key, value in update_data.items():
                setattr(collection, key, value)
            session.add(collection)
            session.commit()
            session.refresh(collection)
        return collection
    
    def archive_collection(self, session: Session, collection_id: int) -> Optional[MemoryCollection]:
        """Archive a memory collection"""
        collection = session.get(MemoryCollection, collection_id)
        if collection:
            collection.archived_at = datetime.now(UTC)
            collection.updated_at = datetime.now(UTC)
            session.add(collection)
            session.commit()
            session.refresh(collection)
        return collection
    
    def get_collection_with_documents(self, session: Session, collection_id: int) -> Optional[MemoryCollection]:
        """Get a memory collection with its documents"""
        statement = select(MemoryCollection).where(MemoryCollection.id == collection_id)
        collection = session.exec(statement).first()
        return collection 