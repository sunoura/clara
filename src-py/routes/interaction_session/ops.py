from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from data.models import (
    InteractionSession,
    InteractionSessionCreate,
    InteractionSessionRead,
    InteractionSessionUpdate,
    InteractionPayload,
)


class InteractionSessionOps:
    @staticmethod
    def create_session(session: Session, session_data: InteractionSessionCreate) -> InteractionSession:
        """Create a new interaction session"""
        db_session = InteractionSession.model_validate(session_data)
        session.add(db_session)
        session.commit()
        session.refresh(db_session)
        return db_session
    
    @staticmethod
    def get_session(session: Session, session_id: str) -> Optional[InteractionSession]:
        """Get an interaction session by ID"""
        return session.get(InteractionSession, session_id)
    
    @staticmethod
    def get_sessions(session: Session, skip: int = 0, limit: int = 100) -> List[InteractionSession]:
        """Get all interaction sessions"""
        statement = select(InteractionSession).order_by(InteractionSession.started_at.desc()).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    @staticmethod
    def get_recent_sessions(session: Session, limit: int = 10) -> List[InteractionSession]:
        """Get recent interaction sessions"""
        statement = select(InteractionSession).order_by(InteractionSession.started_at.desc()).limit(limit)
        return session.exec(statement).all()
    
    @staticmethod
    def update_session(session: Session, session_id: str, session_data: InteractionSessionUpdate) -> Optional[InteractionSession]:
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
    
    @staticmethod
    def delete_session(session: Session, session_id: str) -> bool:
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
    
    @staticmethod
    def get_session_with_payloads(session: Session, session_id: str) -> Optional[InteractionSession]:
        """Get an interaction session with all its payloads"""
        statement = select(InteractionSession).where(InteractionSession.id == session_id)
        interaction_session = session.exec(statement).first()
        return interaction_session 