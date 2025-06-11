from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from db import get_session
from data.models import (
    InteractionSessionCreate,
    InteractionSessionRead,
    InteractionSessionUpdate,
    InteractionSessionWithPayloads,
)
from .ops import InteractionSessionOps

router = APIRouter(prefix="/interaction-sessions", tags=["Interaction Sessions"])


@router.post("/", response_model=InteractionSessionRead)
def create_interaction_session(
    session_data: InteractionSessionCreate,
    session: Session = Depends(get_session)
):
    """Create a new interaction session"""
    return InteractionSessionOps.create_session(session, session_data)


@router.get("/", response_model=List[InteractionSessionRead])
def get_interaction_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all interaction sessions"""
    return InteractionSessionOps.get_sessions(session, skip=skip, limit=limit)


@router.get("/recent", response_model=List[InteractionSessionRead])
def get_recent_interaction_sessions(
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get recent interaction sessions"""
    return InteractionSessionOps.get_recent_sessions(session, limit=limit)


@router.get("/{session_id}", response_model=InteractionSessionRead)
def get_interaction_session(
    session_id: str,
    session: Session = Depends(get_session)
):
    """Get a specific interaction session by ID"""
    interaction_session = InteractionSessionOps.get_session(session, session_id)
    if not interaction_session:
        raise HTTPException(status_code=404, detail="Interaction session not found")
    return interaction_session


@router.get("/{session_id}/with-payloads", response_model=InteractionSessionWithPayloads)
def get_interaction_session_with_payloads(
    session_id: str,
    session: Session = Depends(get_session)
):
    """Get an interaction session with all its payloads"""
    interaction_session = InteractionSessionOps.get_session_with_payloads(session, session_id)
    if not interaction_session:
        raise HTTPException(status_code=404, detail="Interaction session not found")
    return interaction_session


@router.put("/{session_id}", response_model=InteractionSessionRead)
def update_interaction_session(
    session_id: str,
    session_update: InteractionSessionUpdate,
    session: Session = Depends(get_session)
):
    """Update an interaction session"""
    interaction_session = InteractionSessionOps.update_session(session, session_id, session_update)
    if not interaction_session:
        raise HTTPException(status_code=404, detail="Interaction session not found")
    return interaction_session


@router.delete("/{session_id}")
def delete_interaction_session(
    session_id: str,
    session: Session = Depends(get_session)
):
    """Delete an interaction session"""
    success = InteractionSessionOps.delete_session(session, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction session not found")
    return {"message": "Session deleted successfully"} 