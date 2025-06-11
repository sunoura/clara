from sqlmodel import Session, select
from typing import List, Dict, Optional
from datetime import datetime, UTC

from lib.gemini import GeminiClient
from data.models import (
    InteractionPayloadCreate,
    InteractionFrom,
)
from .interaction_service import InteractionService


class ChatService:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.interaction_service = InteractionService()
    
    def send_message(self, session_id: str, message: str, db_session: Session) -> Dict:
        """
        Send a message and get AI response, storing both in the database.
        
        Args:
            session_id: The interaction session ID
            message: User's message content
            db_session: Database session
            
        Returns:
            Dict containing the AI response and metadata
        """
        # Verify session exists
        interaction_session = self.interaction_service.get_session(db_session, session_id)
        if not interaction_session:
            raise ValueError(f"Session {session_id} not found")
        
        # Store user message
        user_payload = InteractionPayloadCreate(
            session_id=session_id,
            content=message,
            ok=True,
            **{"from": InteractionFrom.USER}
        )
        user_record = self.interaction_service.create_payload(db_session, user_payload)
        
        try:
            # Get conversation history
            conversation_history = self._get_conversation_history(session_id, db_session)
            
            # Generate AI response
            ai_response = self.gemini_client.generate_response(conversation_history)
            
            # Store AI response
            ai_payload = InteractionPayloadCreate(
                session_id=session_id,
                content=ai_response,
                ok=True,
                **{"from": InteractionFrom.MODEL}
            )
            ai_payload_record = self.interaction_service.create_payload(db_session, ai_payload)
            
            return {
                "response": ai_response,
                "payload_id": ai_payload_record.id,
                "created_at": ai_payload_record.created_at
            }
            
        except Exception as e:
            # Store failed AI response
            error_payload = InteractionPayloadCreate(
                session_id=session_id,
                content="",
                ok=False,
                err=str(e),
                **{"from": InteractionFrom.MODEL}
            )
            self.interaction_service.create_payload(db_session, error_payload)
            raise Exception(f"Failed to generate AI response: {str(e)}")
    
    def _get_conversation_history(self, session_id: str, db_session: Session) -> List[Dict]:
        """Get conversation history for a session in the format expected by Gemini."""
        payloads = self.interaction_service.get_session_payloads(db_session, session_id)
        
        history = []
        for payload in payloads:
            if payload.ok:  # Only include successful messages
                role = "user" if payload.from_ == InteractionFrom.USER else "model"
                history.append({
                    "role": role,
                    "content": payload.content
                })
        
        return history
    
    def get_session_messages(self, session_id: str, db_session: Session) -> List[Dict]:
        """Get all messages for a session formatted for the frontend."""
        payloads = self.interaction_service.get_session_payloads(db_session, session_id)
        
        messages = []
        for payload in payloads:
            messages.append({
                "id": payload.id,
                "content": payload.content,
                "from": payload.from_,
                "ok": payload.ok,
                "error": payload.err,
                "created_at": payload.created_at.isoformat()
            })
        
        return messages
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        return datetime.now(UTC).isoformat() 