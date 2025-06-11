"""
API module - Clean flat router registration
"""
from fastapi import APIRouter

def create_api_router() -> APIRouter:
    """Create and configure the main API router with all sub-routers"""
    api_router = APIRouter(prefix="/api")

    # Import and register all route modules
    from .memory_collection_routes import router as memory_collection_router
    from .memory_document_routes import router as memory_document_router
    from .interaction_routes import session_router, payload_router
    from .chat_routes import router as chat_router

    # Memory and RAG routes
    api_router.include_router(memory_collection_router)
    api_router.include_router(memory_document_router)
    
    # Interaction routes
    api_router.include_router(session_router)
    api_router.include_router(payload_router)
    
    # Chat routes
    api_router.include_router(chat_router)

    return api_router

# Export
api_router = create_api_router() 