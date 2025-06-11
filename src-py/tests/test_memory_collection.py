import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from data.models import MemoryCollectionCreate, MemoryCollectionUpdate
from services.memory_collection_service import MemoryCollectionService


class TestMemoryCollectionService:
    """Test the MemoryCollectionService class"""

    def test_create_collection(self, session: Session):
        """Test creating a memory collection"""
        service = MemoryCollectionService()
        collection_data = MemoryCollectionCreate(
            title="Test Collection",
            description="A test collection"
        )
        collection = service.create_collection(session, collection_data)
        
        assert collection.id is not None
        assert collection.title == "Test Collection"
        assert collection.description == "A test collection"
        assert collection.created_at is not None
        assert collection.updated_at is not None
        assert collection.archived_at is None

    def test_get_collection(self, session: Session, sample_memory_collection):
        """Test getting a memory collection by ID"""
        service = MemoryCollectionService()
        collection = service.get_collection(session, sample_memory_collection.id)
        
        assert collection is not None
        assert collection.id == sample_memory_collection.id
        assert collection.title == sample_memory_collection.title

    def test_get_collection_not_found(self, session: Session):
        """Test getting a non-existent collection"""
        service = MemoryCollectionService()
        collection = service.get_collection(session, 999)
        assert collection is None

    def test_get_collections(self, session: Session, sample_memory_collection):
        """Test getting all collections"""
        service = MemoryCollectionService()
        collections = service.get_collections(session)
        
        assert len(collections) >= 1
        assert any(c.id == sample_memory_collection.id for c in collections)

    def test_update_collection(self, session: Session, sample_memory_collection):
        """Test updating a memory collection"""
        service = MemoryCollectionService()
        original_updated_at = sample_memory_collection.updated_at
        
        update_data = MemoryCollectionUpdate(
            title="Updated Title",
            description="Updated description"
        )
        
        updated_collection = service.update_collection(
            session, sample_memory_collection.id, update_data
        )
        
        assert updated_collection is not None
        assert updated_collection.title == "Updated Title"
        assert updated_collection.description == "Updated description"
        assert updated_collection.updated_at >= original_updated_at

    def test_archive_collection(self, session: Session, sample_memory_collection):
        """Test archiving a memory collection"""
        service = MemoryCollectionService()
        archived_collection = service.archive_collection(
            session, sample_memory_collection.id
        )
        
        assert archived_collection is not None
        assert archived_collection.archived_at is not None
        
        # Verify it doesn't appear in regular queries
        collections = service.get_collections(session)
        assert not any(c.id == sample_memory_collection.id for c in collections)


class TestMemoryCollectionRoutes:
    """Test the memory collection API routes"""

    def test_create_collection_endpoint(self, client: TestClient):
        """Test POST /api/memory-collections/"""
        collection_data = {
            "title": "API Test Collection",
            "description": "Created via API"
        }
        
        response = client.post("/api/memory-collections/", json=collection_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "API Test Collection"
        assert data["description"] == "Created via API"
        assert "id" in data
        assert "created_at" in data

    def test_get_collections_endpoint(self, client: TestClient, sample_memory_collection):
        """Test GET /api/memory-collections/"""
        response = client.get("/api/memory-collections/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_collection_endpoint(self, client: TestClient, sample_memory_collection):
        """Test GET /api/memory-collections/{id}"""
        response = client.get(f"/api/memory-collections/{sample_memory_collection.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_memory_collection.id
        assert data["title"] == sample_memory_collection.title

    def test_get_collection_not_found(self, client: TestClient):
        """Test GET /api/memory-collections/{id} with non-existent ID"""
        response = client.get("/api/memory-collections/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_collection_endpoint(self, client: TestClient, sample_memory_collection):
        """Test PUT /api/memory-collections/{id}"""
        update_data = {
            "title": "Updated via API",
            "description": "New description"
        }
        
        response = client.put(
            f"/api/memory-collections/{sample_memory_collection.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated via API"
        assert data["description"] == "New description"

    def test_archive_collection_endpoint(self, client: TestClient, sample_memory_collection):
        """Test DELETE /api/memory-collections/{id}"""
        response = client.delete(f"/api/memory-collections/{sample_memory_collection.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["archived_at"] is not None

    def test_get_collection_with_documents(self, client: TestClient, sample_memory_document):
        """Test GET /api/memory-collections/{id}/with-documents"""
        collection_id = sample_memory_document.collection_id
        response = client.get(f"/api/memory-collections/{collection_id}/with-documents")
        
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) >= 1

    def test_pagination(self, client: TestClient):
        """Test pagination parameters"""
        # Create multiple collections
        for i in range(5):
            client.post("/api/memory-collections/", json={
                "title": f"Collection {i}",
                "description": f"Description {i}"
            })
        
        # Test with limit
        response = client.get("/api/memory-collections/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        
        # Test with skip
        response = client.get("/api/memory-collections/?skip=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2 