from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from db import get_session
from data.models import (
    MemoryCollectionCreate,
    MemoryCollectionRead,
    MemoryCollectionUpdate,
    MemoryCollectionWithDocuments,
)
from services.memory_collection_service import MemoryCollectionService

router = APIRouter(prefix="/memory-collections", tags=["Memory Collections"])
memory_collection_service = MemoryCollectionService()


@router.post("/", response_model=MemoryCollectionRead)
def create_memory_collection(
    collection: MemoryCollectionCreate,
    session: Session = Depends(get_session)
):
    """Create a new memory collection"""
    return memory_collection_service.create_collection(session, collection)


@router.get("/", response_model=List[MemoryCollectionRead])
def get_memory_collections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all memory collections"""
    return memory_collection_service.get_collections(session, skip=skip, limit=limit)


@router.get("/{collection_id}", response_model=MemoryCollectionRead)
def get_memory_collection(
    collection_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific memory collection by ID"""
    collection = memory_collection_service.get_collection(session, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Memory collection not found")
    return collection


@router.get("/{collection_id}/with-documents", response_model=MemoryCollectionWithDocuments)
def get_memory_collection_with_documents(
    collection_id: int,
    session: Session = Depends(get_session)
):
    """Get a memory collection with all its documents"""
    collection = memory_collection_service.get_collection_with_documents(session, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Memory collection not found")
    return collection


@router.put("/{collection_id}", response_model=MemoryCollectionRead)
def update_memory_collection(
    collection_id: int,
    collection_update: MemoryCollectionUpdate,
    session: Session = Depends(get_session)
):
    """Update a memory collection"""
    collection = memory_collection_service.update_collection(session, collection_id, collection_update)
    if not collection:
        raise HTTPException(status_code=404, detail="Memory collection not found")
    return collection


@router.delete("/{collection_id}", response_model=MemoryCollectionRead)
def archive_memory_collection(
    collection_id: int,
    session: Session = Depends(get_session)
):
    """Archive (soft delete) a memory collection"""
    collection = memory_collection_service.archive_collection(session, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Memory collection not found")
    return collection 