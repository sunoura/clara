from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from db import get_session
from data.models import (
    InteractionSessionCreate,
    InteractionSessionRead,
    InteractionSessionUpdate,
    InteractionSessionWithPayloads,
    InteractionPayloadCreate,
    InteractionPayloadRead,
    InteractionPayloadUpdate,
    InteractionPayloadWithSession,
    InteractionFrom,
)
from services.interaction_service import InteractionService

interaction_service = InteractionService()

# Session router
session_router = APIRouter(prefix="/interaction-sessions", tags=["Interaction Sessions"])

@session_router.post("/", response_model=InteractionSessionRead)
def create_interaction_session(
    session_data: InteractionSessionCreate,
    session: Session = Depends(get_session)
):
    """Create a new interaction session"""
    return interaction_service.create_session(session, session_data)

@session_router.get("/", response_model=List[InteractionSessionRead])
def get_interaction_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all interaction sessions"""
    return interaction_service.get_sessions(session, skip=skip, limit=limit)

@session_router.get("/recent", response_model=List[InteractionSessionRead])
def get_recent_interaction_sessions(
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get recent interaction sessions"""
    return interaction_service.get_recent_sessions(session, limit=limit)

@session_router.get("/{session_id}", response_model=InteractionSessionRead)
def get_interaction_session(
    session_id: str,
    session: Session = Depends(get_session)
):
    """Get a specific interaction session by ID"""
    interaction_session = interaction_service.get_session(session, session_id)
    if not interaction_session:
        raise HTTPException(status_code=404, detail="Interaction session not found")
    return interaction_session

@session_router.get("/{session_id}/with-payloads", response_model=InteractionSessionWithPayloads)
def get_interaction_session_with_payloads(
    session_id: str,
    session: Session = Depends(get_session)
):
    """Get an interaction session with all its payloads"""
    interaction_session = interaction_service.get_session_with_payloads(session, session_id)
    if not interaction_session:
        raise HTTPException(status_code=404, detail="Interaction session not found")
    return interaction_session

@session_router.put("/{session_id}", response_model=InteractionSessionRead)
def update_interaction_session(
    session_id: str,
    session_update: InteractionSessionUpdate,
    session: Session = Depends(get_session)
):
    """Update an interaction session"""
    interaction_session = interaction_service.update_session(session, session_id, session_update)
    if not interaction_session:
        raise HTTPException(status_code=404, detail="Interaction session not found")
    return interaction_session

@session_router.delete("/{session_id}")
def delete_interaction_session(
    session_id: str,
    session: Session = Depends(get_session)
):
    """Delete an interaction session"""
    success = interaction_service.delete_session(session, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction session not found")
    return {"message": "Session deleted successfully"}

# Payload router
payload_router = APIRouter(prefix="/interaction-payloads", tags=["Interaction Payloads"])

@payload_router.post("/", response_model=InteractionPayloadRead)
def create_interaction_payload(
    payload_data: InteractionPayloadCreate,
    session: Session = Depends(get_session)
):
    """Create a new interaction payload"""
    return interaction_service.create_payload(session, payload_data)

@payload_router.get("/", response_model=List[InteractionPayloadRead])
def get_interaction_payloads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all interaction payloads"""
    return interaction_service.get_payloads(session, skip=skip, limit=limit)

@payload_router.get("/by-type/{from_type}", response_model=List[InteractionPayloadRead])
def get_payloads_by_type(
    from_type: InteractionFrom,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get payloads filtered by sender type (user/model)"""
    return interaction_service.get_payloads_by_type(session, from_type, skip=skip, limit=limit)

@payload_router.get("/failed", response_model=List[InteractionPayloadRead])
def get_failed_payloads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get payloads that failed (ok=False)"""
    return interaction_service.get_failed_payloads(session, skip=skip, limit=limit)

@payload_router.get("/by-session/{session_id}", response_model=List[InteractionPayloadRead])
def get_session_payloads(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all payloads for a specific session"""
    return interaction_service.get_session_payloads(session, session_id, skip=skip, limit=limit)

@payload_router.get("/{payload_id}", response_model=InteractionPayloadRead)
def get_interaction_payload(
    payload_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific interaction payload by ID"""
    payload = interaction_service.get_payload(session, payload_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Interaction payload not found")
    return payload

@payload_router.get("/{payload_id}/with-session", response_model=InteractionPayloadWithSession)
def get_payload_with_session(
    payload_id: int,
    session: Session = Depends(get_session)
):
    """Get an interaction payload with its session data"""
    payload = interaction_service.get_payload_with_session(session, payload_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Interaction payload not found")
    return payload

@payload_router.put("/{payload_id}", response_model=InteractionPayloadRead)
def update_interaction_payload(
    payload_id: int,
    payload_update: InteractionPayloadUpdate,
    session: Session = Depends(get_session)
):
    """Update an interaction payload"""
    payload = interaction_service.update_payload(session, payload_id, payload_update)
    if not payload:
        raise HTTPException(status_code=404, detail="Interaction payload not found")
    return payload 