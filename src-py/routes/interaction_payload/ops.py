from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from data.models import (
    InteractionPayload,
    InteractionPayloadCreate,
    InteractionPayloadRead,
    InteractionPayloadUpdate,
    InteractionFrom,
)


class InteractionPayloadOps:
    @staticmethod
    def create_payload(session: Session, payload_data: InteractionPayloadCreate) -> InteractionPayload:
        """Create a new interaction payload"""
        db_payload = InteractionPayload.model_validate(payload_data)
        session.add(db_payload)
        session.commit()
        session.refresh(db_payload)
        return db_payload
    
    @staticmethod
    def get_payload(session: Session, payload_id: int) -> Optional[InteractionPayload]:
        """Get a single payload by ID"""
        return session.get(InteractionPayload, payload_id)
    
    @staticmethod
    def get_session_payloads(session: Session, session_id: str, skip: int = 0, limit: int = 100) -> List[InteractionPayload]:
        """Get all payloads for a session"""
        statement = select(InteractionPayload).where(
            InteractionPayload.session_id == session_id
        ).order_by(InteractionPayload.created_at.asc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    @staticmethod
    def get_payloads(session: Session, skip: int = 0, limit: int = 100) -> List[InteractionPayload]:
        """Get all interaction payloads"""
        statement = select(InteractionPayload).order_by(InteractionPayload.created_at.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    @staticmethod
    def get_payloads_by_type(session: Session, from_type: InteractionFrom, skip: int = 0, limit: int = 100) -> List[InteractionPayload]:
        """Get payloads filtered by sender type (user/model)"""
        statement = select(InteractionPayload).where(
            InteractionPayload.from_ == from_type
        ).order_by(InteractionPayload.created_at.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    @staticmethod
    def get_failed_payloads(session: Session, skip: int = 0, limit: int = 100) -> List[InteractionPayload]:
        """Get payloads that failed (ok=False)"""
        statement = select(InteractionPayload).where(
            InteractionPayload.ok == False
        ).order_by(InteractionPayload.created_at.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    @staticmethod
    def update_payload(session: Session, payload_id: int, payload_data: InteractionPayloadUpdate) -> Optional[InteractionPayload]:
        """Update an interaction payload"""
        payload = session.get(InteractionPayload, payload_id)
        if payload:
            update_data = payload_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(payload, key, value)
            session.add(payload)
            session.commit()
            session.refresh(payload)
        return payload
    
    @staticmethod
    def get_payload_with_session(session: Session, payload_id: int) -> Optional[InteractionPayload]:
        """Get a payload with its session data"""
        statement = select(InteractionPayload).where(InteractionPayload.id == payload_id)
        payload = session.exec(statement).first()
        return payload 