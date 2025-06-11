"""
Routes module - Central router registration
"""
from fastapi import APIRouter
from .items.route import router as items_router
from .memory_collection.routes import router as memory_collection_router
from .memory_document.routes import router as memory_document_router
from .interaction_session.routes import router as interaction_session_router
from .interaction_payload.routes import router as interaction_payload_router


def create_api_router() -> APIRouter:
    """
    Create and configure the main API router with all sub-routers
    """
    api_router = APIRouter(prefix="/api")

    # Register all route modules
    api_router.include_router(
        items_router,
        prefix="/items",
        tags=["items"]
    )
    
    # Memory and RAG routes
    api_router.include_router(memory_collection_router)
    api_router.include_router(memory_document_router)
    
    # Interaction and chat routes
    api_router.include_router(interaction_session_router)
    api_router.include_router(interaction_payload_router)

    return api_router


# Export
api_router = create_api_router()

# Also export individual routers if needed
__all__ = [
    "api_router",
    "memory_collection_router",
    "memory_document_router", 
    "interaction_session_router",
    "interaction_payload_router",
]
