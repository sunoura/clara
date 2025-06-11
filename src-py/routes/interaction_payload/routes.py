from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List

from db import get_session
from data.models import (
    InteractionPayloadCreate,
    InteractionPayloadRead,
    InteractionPayloadUpdate,
    InteractionPayloadWithSession,
    InteractionFrom,
)
from .ops import InteractionPayloadOps

router = APIRouter(prefix="/interaction-payloads", tags=["Interaction Payloads"])


@router.post("/", response_model=InteractionPayloadRead)
def create_interaction_payload(
    payload_data: InteractionPayloadCreate,
    session: Session = Depends(get_session)
):
    """Create a new interaction payload"""
    return InteractionPayloadOps.create_payload(session, payload_data)


@router.get("/", response_model=List[InteractionPayloadRead])
def get_interaction_payloads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all interaction payloads"""
    return InteractionPayloadOps.get_payloads(session, skip=skip, limit=limit)


@router.get("/by-type/{from_type}", response_model=List[InteractionPayloadRead])
def get_payloads_by_type(
    from_type: InteractionFrom,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get payloads filtered by sender type (user/model)"""
    return InteractionPayloadOps.get_payloads_by_type(session, from_type, skip=skip, limit=limit)


@router.get("/failed", response_model=List[InteractionPayloadRead])
def get_failed_payloads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get payloads that failed (ok=False)"""
    return InteractionPayloadOps.get_failed_payloads(session, skip=skip, limit=limit)


@router.get("/by-session/{session_id}", response_model=List[InteractionPayloadRead])
def get_session_payloads(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session)
):
    """Get all payloads for a specific session"""
    return InteractionPayloadOps.get_session_payloads(session, session_id, skip=skip, limit=limit)


@router.get("/{payload_id}", response_model=InteractionPayloadRead)
def get_interaction_payload(
    payload_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific interaction payload by ID"""
    payload = InteractionPayloadOps.get_payload(session, payload_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Interaction payload not found")
    return payload


@router.get("/{payload_id}/with-session", response_model=InteractionPayloadWithSession)
def get_payload_with_session(
    payload_id: int,
    session: Session = Depends(get_session)
):
    """Get an interaction payload with its session data"""
    payload = InteractionPayloadOps.get_payload_with_session(session, payload_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Interaction payload not found")
    return payload


@router.put("/{payload_id}", response_model=InteractionPayloadRead)
def update_interaction_payload(
    payload_id: int,
    payload_update: InteractionPayloadUpdate,
    session: Session = Depends(get_session)
):
    """Update an interaction payload"""
    payload = InteractionPayloadOps.update_payload(session, payload_id, payload_update)
    if not payload:
        raise HTTPException(status_code=404, detail="Interaction payload not found")
    return payload 