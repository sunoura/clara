from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlmodel import Session
import json
import asyncio
from typing import Dict
from concurrent.futures import ThreadPoolExecutor

from db import get_session
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}
chat_service = ChatService()
executor = ThreadPoolExecutor(max_workers=4)


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat communication."""
    
    # Prevent multiple connections per session
    if session_id in active_connections:
        await websocket.close(code=4000, reason="Session already has active connection")
        return
    
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                user_message = message_data.get("content", "")
                
                if user_message.strip():
                    # Process message and get both user and AI data
                    try:
                        response_data = await _process_message_async(session_id, user_message)
                        
                        # Send user message confirmation with real ID
                        await websocket.send_text(json.dumps({
                            "type": "user_message",
                            "content": response_data["user_message"]["content"],
                            "payload_id": response_data["user_message"]["id"],
                            "timestamp": response_data["user_message"]["created_at"].isoformat()
                        }))
                        
                        # Send AI response
                        await websocket.send_text(json.dumps({
                            "type": "ai_response",
                            "content": response_data["ai_response"]["content"],
                            "payload_id": response_data["ai_response"]["id"],
                            "timestamp": response_data["ai_response"]["created_at"].isoformat()
                        }))
                    except Exception as e:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"Failed to generate response: {str(e)}"
                        }))
            
            elif message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        if session_id in active_connections:
            del active_connections[session_id]


@router.get("/{session_id}/history")
async def get_chat_history(session_id: str, db_session: Session = Depends(get_session)):
    """Get chat history for a session via HTTP."""
    try:
        messages = chat_service.get_session_messages(session_id, db_session)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/active-connections")
async def get_active_connections():
    """Get list of active WebSocket connections (for debugging)."""
    return {"active_sessions": list(active_connections.keys())}


# Helper function for async processing
async def _process_message_async(session_id: str, message: str) -> dict:
    """Process a chat message asynchronously using thread pool."""
    loop = asyncio.get_event_loop()
    
    def _send_message():
        with next(get_session()) as db_session:
            return chat_service.send_message(session_id, message, db_session)
    
    return await loop.run_in_executor(executor, _send_message) 