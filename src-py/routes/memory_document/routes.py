from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from db import get_session
from data.models import (
    MemoryDocumentCreate,
    MemoryDocumentRead,
    MemoryDocumentUpdate,
    MemoryDocumentWithCollection,
)
from .ops import MemoryDocumentOps

router = APIRouter(prefix="/memory-documents", tags=["Memory Documents"])


@router.post("/", response_model=MemoryDocumentRead)
def create_memory_document(
    document: MemoryDocumentCreate,
    session: Session = Depends(get_session)
):
    """Create a new memory document"""
    return MemoryDocumentOps.create_document(session, document)


@router.get("/", response_model=List[MemoryDocumentRead])
def get_memory_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all memory documents"""
    return MemoryDocumentOps.get_documents(session, skip=skip, limit=limit)


@router.get("/search", response_model=List[MemoryDocumentRead])
def search_memory_documents(
    q: str = Query(..., description="Search query for document content"),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Search memory documents by content"""
    return MemoryDocumentOps.search_documents(session, q, limit=limit)


@router.get("/by-collection/{collection_id}", response_model=List[MemoryDocumentRead])
def get_documents_by_collection(
    collection_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all documents in a specific collection"""
    return MemoryDocumentOps.get_documents_by_collection(session, collection_id, skip=skip, limit=limit)


@router.get("/by-chroma-id/{chroma_id}", response_model=MemoryDocumentRead)
def get_document_by_chroma_id(
    chroma_id: str,
    session: Session = Depends(get_session)
):
    """Get a memory document by its ChromaDB ID"""
    document = MemoryDocumentOps.get_document_by_chroma_id(session, chroma_id)
    if not document:
        raise HTTPException(status_code=404, detail="Memory document not found")
    return document


@router.get("/{document_id}", response_model=MemoryDocumentRead)
def get_memory_document(
    document_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific memory document by ID"""
    document = MemoryDocumentOps.get_document(session, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Memory document not found")
    return document


@router.put("/{document_id}", response_model=MemoryDocumentRead)
def update_memory_document(
    document_id: int,
    document_update: MemoryDocumentUpdate,
    session: Session = Depends(get_session)
):
    """Update a memory document"""
    document = MemoryDocumentOps.update_document(session, document_id, document_update)
    if not document:
        raise HTTPException(status_code=404, detail="Memory document not found")
    return document


@router.delete("/{document_id}", response_model=MemoryDocumentRead)
def archive_memory_document(
    document_id: int,
    session: Session = Depends(get_session)
):
    """Archive (soft delete) a memory document"""
    document = MemoryDocumentOps.archive_document(session, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Memory document not found")
    return document 