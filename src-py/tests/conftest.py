import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from db import get_session
from data.models import *  # Import all models to register them


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database override"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_memory_collection(session: Session):
    """Create a sample memory collection for testing"""
    from services.memory_collection_service import MemoryCollectionService
    from data.models import MemoryCollectionCreate
    
    service = MemoryCollectionService()
    collection_data = MemoryCollectionCreate(
        title="Test Collection",
        description="A test memory collection"
    )
    return service.create_collection(session, collection_data)


@pytest.fixture
def sample_memory_document(session: Session, sample_memory_collection):
    """Create a sample memory document for testing"""
    from services.memory_document_service import MemoryDocumentService
    from data.models import MemoryDocumentCreate
    
    service = MemoryDocumentService()
    document_data = MemoryDocumentCreate(
        chroma_id="test_chroma_id_001",
        content="This is a test memory document with some content",
        collection_id=sample_memory_collection.id,
        metadatas={"type": "test", "priority": "high", "tags": ["test", "memory"]}
    )
    return service.create_document(session, document_data)


@pytest.fixture
def sample_interaction_session(session: Session):
    """Create a sample interaction session for testing"""
    from services.interaction_service import InteractionService
    from data.models import InteractionSessionCreate
    
    service = InteractionService()
    session_data = InteractionSessionCreate(
        title="Test Chat Session",
        context_summary="Testing the chat functionality"
    )
    return service.create_session(session, session_data)


@pytest.fixture
def sample_interaction_payload(session: Session, sample_interaction_session):
    """Create a sample interaction payload for testing"""
    from services.interaction_service import InteractionService
    from data.models import InteractionPayloadCreate, InteractionFrom
    
    service = InteractionService()
    payload_data = InteractionPayloadCreate(
        session_id=sample_interaction_session.id,
        content="Hello, this is a test message from user",
        ok=True,
        **{"from": InteractionFrom.USER}
    )
    return service.create_payload(session, payload_data) 