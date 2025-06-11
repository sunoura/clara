from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, UTC

from data.models import (
    InteractionSession,
    InteractionSessionCreate,
    InteractionSessionUpdate,
    InteractionPayload,
    InteractionPayloadCreate,
    InteractionPayloadUpdate,
    InteractionFrom,
)


class InteractionService:
    # Session operations
    def create_session(self, session: Session, session_data: InteractionSessionCreate) -> InteractionSession:
        """Create a new interaction session"""
        db_session = InteractionSession.model_validate(session_data)
        session.add(db_session)
        session.commit()
        session.refresh(db_session)
        return db_session
    
    def get_session(self, session: Session, session_id: str) -> Optional[InteractionSession]:
        """Get an interaction session by ID"""
        return session.get(InteractionSession, session_id)
    
    def get_sessions(self, session: Session, skip: int = 0, limit: int = 100) -> List[InteractionSession]:
        """Get all interaction sessions"""
        statement = select(InteractionSession).order_by(InteractionSession.started_at.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def get_recent_sessions(self, session: Session, limit: int = 10) -> List[InteractionSession]:
        """Get recent interaction sessions"""
        statement = select(InteractionSession).order_by(InteractionSession.started_at.desc()).limit(limit)
        return session.exec(statement).all()
    
    def update_session(self, session: Session, session_id: str, session_data: InteractionSessionUpdate) -> Optional[InteractionSession]:
        """Update an interaction session"""
        interaction_session = session.get(InteractionSession, session_id)
        if interaction_session:
            update_data = session_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(interaction_session, key, value)
            session.add(interaction_session)
            session.commit()
            session.refresh(interaction_session)
        return interaction_session
    
    def delete_session(self, session: Session, session_id: str) -> bool:
        """Delete an interaction session and all its payloads"""
        interaction_session = session.get(InteractionSession, session_id)
        if interaction_session:
            # First delete all associated payloads
            statement = select(InteractionPayload).where(InteractionPayload.session_id == session_id)
            payloads = session.exec(statement).all()
            for payload in payloads:
                session.delete(payload)
            
            # Then delete the session
            session.delete(interaction_session)
            session.commit()
            return True
        return False
    
    def get_session_with_payloads(self, session: Session, session_id: str) -> Optional[InteractionSession]:
        """Get an interaction session with all its payloads"""
        statement = select(InteractionSession).where(InteractionSession.id == session_id)
        interaction_session = session.exec(statement).first()
        return interaction_session
    
    # Payload operations
    def create_payload(self, session: Session, payload_data: InteractionPayloadCreate) -> InteractionPayload:
        """Create a new interaction payload"""
        db_payload = InteractionPayload.model_validate(payload_data)
        session.add(db_payload)
        session.commit()
        session.refresh(db_payload)
        return db_payload
    
    def get_payload(self, session: Session, payload_id: int) -> Optional[InteractionPayload]:
        """Get an interaction payload by ID"""
        return session.get(InteractionPayload, payload_id)
    
    def get_payloads(self, session: Session, skip: int = 0, limit: int = 100) -> List[InteractionPayload]:
        """Get all interaction payloads"""
        statement = select(InteractionPayload).order_by(InteractionPayload.created_at.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def get_payloads_by_type(self, session: Session, from_type: InteractionFrom, skip: int = 0, limit: int = 100) -> List[InteractionPayload]:
        """Get payloads filtered by sender type (user/model)"""
        statement = select(InteractionPayload).where(
            InteractionPayload.from_ == from_type
        ).order_by(InteractionPayload.created_at.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def get_failed_payloads(self, session: Session, skip: int = 0, limit: int = 100) -> List[InteractionPayload]:
        """Get payloads that failed (ok=False)"""
        statement = select(InteractionPayload).where(
            InteractionPayload.ok == False
        ).order_by(InteractionPayload.created_at.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def get_session_payloads(self, session: Session, session_id: str, skip: int = 0, limit: int = 100) -> List[InteractionPayload]:
        """Get all payloads for a specific session"""
        statement = select(InteractionPayload).where(
            InteractionPayload.session_id == session_id
        ).order_by(InteractionPayload.created_at.asc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    def update_payload(self, session: Session, payload_id: int, payload_data: InteractionPayloadUpdate) -> Optional[InteractionPayload]:
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
    
    def get_payload_with_session(self, session: Session, payload_id: int) -> Optional[InteractionPayload]:
        """Get an interaction payload with its session data"""
        statement = select(InteractionPayload).where(InteractionPayload.id == payload_id)
        payload = session.exec(statement).first()
        return payload 