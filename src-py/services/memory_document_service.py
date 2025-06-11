from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, UTC
import json

from data.models import (
    MemoryDocument,
    MemoryDocumentCreate,
    MemoryDocumentUpdate,
)


class MemoryDocumentService:
    def create_document(self, session: Session, document_data: MemoryDocumentCreate) -> MemoryDocument:
        """Create a new memory document"""
        # Convert metadatas dict to JSON string for storage
        db_document = MemoryDocument(
            chroma_id=document_data.chroma_id,
            content=document_data.content,
            collection_id=document_data.collection_id,
            metadatas=json.dumps(document_data.metadatas or {}),
        )
        session.add(db_document)
        session.commit()
        session.refresh(db_document)
        return db_document
    
    def get_document(self, session: Session, document_id: int) -> Optional[MemoryDocument]:
        """Get a memory document by ID"""
        return session.get(MemoryDocument, document_id)
    
    def get_document_by_chroma_id(self, session: Session, chroma_id: str) -> Optional[MemoryDocument]:
        """Get a memory document by ChromaDB ID"""
        statement = select(MemoryDocument).where(MemoryDocument.chroma_id == chroma_id)
        return session.exec(statement).first()
    
    def get_documents_by_collection(self, session: Session, collection_id: int, skip: int = 0, limit: int = 100) -> List[MemoryDocument]:
        """Get all documents in a collection"""
        statement = select(MemoryDocument).where(
            MemoryDocument.collection_id == collection_id,
            MemoryDocument.archived_at.is_(None)
        ).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def get_documents(self, session: Session, skip: int = 0, limit: int = 100) -> List[MemoryDocument]:
        """Get all memory documents"""
        statement = select(MemoryDocument).where(MemoryDocument.archived_at.is_(None)).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def update_document(self, session: Session, document_id: int, document_data: MemoryDocumentUpdate) -> Optional[MemoryDocument]:
        """Update a memory document"""
        document = session.get(MemoryDocument, document_id)
        if document:
            update_data = document_data.model_dump(exclude_unset=True)
            update_data['updated_at'] = datetime.now(UTC)
            # Handle metadatas conversion
            if 'metadatas' in update_data and update_data['metadatas'] is not None:
                update_data['metadatas'] = json.dumps(update_data['metadatas'])
            
            for key, value in update_data.items():
                setattr(document, key, value)
            session.add(document)
            session.commit()
            session.refresh(document)
        return document
    
    def archive_document(self, session: Session, document_id: int) -> Optional[MemoryDocument]:
        """Archive a memory document"""
        document = session.get(MemoryDocument, document_id)
        if document:
            document.archived_at = datetime.now(UTC)
            document.updated_at = datetime.now(UTC)
            session.add(document)
            session.commit()
            session.refresh(document)
        return document
    
    def search_documents(self, session: Session, content_query: str, limit: int = 10) -> List[MemoryDocument]:
        """Simple text search in document content"""
        statement = select(MemoryDocument).where(
            MemoryDocument.content.contains(content_query),
            MemoryDocument.archived_at.is_(None)
        ).limit(limit)
        return session.exec(statement).all() 