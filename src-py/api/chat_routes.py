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
# Track processing messages to prevent duplicates
processing_messages: Dict[str, set] = {}
chat_service = ChatService()
executor = ThreadPoolExecutor(max_workers=4)


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat communication."""
    
    # PREVENT MULTIPLE CONNECTIONS PER SESSION
    if session_id in active_connections:
        print(f"DEBUG: Rejecting duplicate connection for session {session_id}")
        await websocket.close(code=4000, reason="Session already has active connection")
        return
    
    await websocket.accept()
    active_connections[session_id] = websocket
    
    # Initialize processing tracker for this session
    if session_id not in processing_messages:
        processing_messages[session_id] = set()
    
    print(f"DEBUG: WebSocket connected for session {session_id}. Total connections: {len(active_connections)}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                user_message = message_data.get("content", "")
                
                if user_message.strip():
                    # Create unique message key for deduplication
                    import time
                    message_key = f"{user_message}_{int(time.time() * 1000)}"
                    
                    # Check if this message is already being processed
                    if message_key in processing_messages.get(session_id, set()):
                        print(f"DEBUG: Duplicate message ignored for session {session_id}: '{user_message}'")
                        continue
                    
                    # Mark message as being processed
                    processing_messages[session_id].add(message_key)
                    
                    # Process message and get both user and AI data
                    try:
                        print(f"DEBUG: Processing WebSocket message for session {session_id}: '{user_message}'")
                        response_data = await _process_message_async(session_id, user_message)
                        print(f"DEBUG: Response data: user_id={response_data['user_message']['id']}, ai_id={response_data['ai_response']['id']}")
                        
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
                    finally:
                        # Clean up processing tracker
                        processing_messages[session_id].discard(message_key)
            
            elif message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        print(f"DEBUG: WebSocket disconnected for session {session_id}")
        if session_id in active_connections:
            del active_connections[session_id]
        if session_id in processing_messages:
            del processing_messages[session_id]
    except Exception as e:
        print(f"DEBUG: WebSocket error for session {session_id}: {str(e)}")
        if session_id in active_connections:
            del active_connections[session_id]
        if session_id in processing_messages:
            del processing_messages[session_id]


@router.get("/{session_id}/history")
async def get_chat_history(session_id: str, db_session: Session = Depends(get_session)):
    """Get chat history for a session via HTTP."""
    try:
        messages = chat_service.get_session_messages(session_id, db_session)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/message")
async def send_message_http(
    session_id: str, 
    message_data: dict,
    db_session: Session = Depends(get_session)
):
    """Send a message via HTTP (fallback for non-WebSocket clients)."""
    try:
        user_message = message_data.get("content", "")
        if not user_message.strip():
            raise HTTPException(status_code=400, detail="Message content is required")
        
        response_data = await _process_message_async(session_id, user_message)
        return {
            "user_message": {
                "id": response_data["user_message"]["id"],
                "content": response_data["user_message"]["content"],
                "created_at": response_data["user_message"]["created_at"].isoformat()
            },
            "ai_response": {
                "id": response_data["ai_response"]["id"],
                "content": response_data["ai_response"]["content"],
                "created_at": response_data["ai_response"]["created_at"].isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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