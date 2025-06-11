import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from data.models import MemoryDocumentCreate, MemoryDocumentUpdate
from services.memory_document_service import MemoryDocumentService


class TestMemoryDocumentService:
    """Test the MemoryDocumentService class"""

    def test_create_document(self, session: Session, sample_memory_collection):
        """Test creating a memory document"""
        service = MemoryDocumentService()
        document_data = MemoryDocumentCreate(
            chroma_id="test_chroma_123",
            content="Test document content",
            collection_id=sample_memory_collection.id,
            metadatas={"type": "test", "priority": "medium"}
        )
        document = service.create_document(session, document_data)
        
        assert document.id is not None
        assert document.chroma_id == "test_chroma_123"
        assert document.content == "Test document content"
        assert document.collection_id == sample_memory_collection.id
        assert document.created_at is not None
        assert document.updated_at is not None
        assert document.archived_at is None

    def test_get_document(self, session: Session, sample_memory_document):
        """Test getting a memory document by ID"""
        service = MemoryDocumentService()
        document = service.get_document(session, sample_memory_document.id)
        
        assert document is not None
        assert document.id == sample_memory_document.id
        assert document.chroma_id == sample_memory_document.chroma_id

    def test_get_document_not_found(self, session: Session):
        """Test getting a non-existent document"""
        service = MemoryDocumentService()
        document = service.get_document(session, 999)
        assert document is None

    def test_get_document_by_chroma_id(self, session: Session, sample_memory_document):
        """Test getting a document by ChromaDB ID"""
        service = MemoryDocumentService()
        document = service.get_document_by_chroma_id(
            session, sample_memory_document.chroma_id
        )
        
        assert document is not None
        assert document.id == sample_memory_document.id
        assert document.chroma_id == sample_memory_document.chroma_id

    def test_get_documents_by_collection(self, session: Session, sample_memory_document):
        """Test getting documents by collection"""
        service = MemoryDocumentService()
        documents = service.get_documents_by_collection(
            session, sample_memory_document.collection_id
        )
        
        assert len(documents) >= 1
        assert any(d.id == sample_memory_document.id for d in documents)

    def test_get_documents(self, session: Session, sample_memory_document):
        """Test getting all documents"""
        service = MemoryDocumentService()
        documents = service.get_documents(session)
        
        assert len(documents) >= 1
        assert any(d.id == sample_memory_document.id for d in documents)

    def test_update_document(self, session: Session, sample_memory_document):
        """Test updating a memory document"""
        service = MemoryDocumentService()
        original_updated_at = sample_memory_document.updated_at
        
        update_data = MemoryDocumentUpdate(
            content="Updated content",
            metadatas={"updated": True, "priority": "high"}
        )
        
        updated_document = service.update_document(
            session, sample_memory_document.id, update_data
        )
        
        assert updated_document is not None
        assert updated_document.content == "Updated content"
        assert updated_document.updated_at >= original_updated_at

    def test_archive_document(self, session: Session, sample_memory_document):
        """Test archiving a memory document"""
        service = MemoryDocumentService()
        archived_document = service.archive_document(
            session, sample_memory_document.id
        )
        
        assert archived_document is not None
        assert archived_document.archived_at is not None
        
        # Verify it doesn't appear in regular queries
        documents = service.get_documents(session)
        assert not any(d.id == sample_memory_document.id for d in documents)

    def test_search_documents(self, session: Session, sample_memory_document):
        """Test searching documents by content"""
        service = MemoryDocumentService()
        # Search for part of the content
        search_term = "test memory document"
        documents = service.search_documents(session, search_term)
        
        assert len(documents) >= 1
        assert any(d.id == sample_memory_document.id for d in documents)


class TestMemoryDocumentRoutes:
    """Test the memory document API routes"""

    def test_create_document_endpoint(self, client: TestClient, sample_memory_collection):
        """Test POST /api/memory-documents/"""
        document_data = {
            "chroma_id": "api_test_123",
            "content": "Document created via API",
            "collection_id": sample_memory_collection.id,
            "metadatas": {"source": "api", "test": True}
        }
        
        response = client.post("/api/memory-documents/", json=document_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["chroma_id"] == "api_test_123"
        assert data["content"] == "Document created via API"
        assert data["collection_id"] == sample_memory_collection.id
        assert "id" in data

    def test_get_documents_endpoint(self, client: TestClient, sample_memory_document):
        """Test GET /api/memory-documents/"""
        response = client.get("/api/memory-documents/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_document_endpoint(self, client: TestClient, sample_memory_document):
        """Test GET /api/memory-documents/{id}"""
        response = client.get(f"/api/memory-documents/{sample_memory_document.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_memory_document.id
        assert data["chroma_id"] == sample_memory_document.chroma_id

    def test_get_document_not_found(self, client: TestClient):
        """Test GET /api/memory-documents/{id} with non-existent ID"""
        response = client.get("/api/memory-documents/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_document_by_chroma_id_endpoint(self, client: TestClient, sample_memory_document):
        """Test GET /api/memory-documents/by-chroma-id/{chroma_id}"""
        response = client.get(f"/api/memory-documents/by-chroma-id/{sample_memory_document.chroma_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["chroma_id"] == sample_memory_document.chroma_id
        assert data["id"] == sample_memory_document.id

    def test_get_documents_by_collection_endpoint(self, client: TestClient, sample_memory_document):
        """Test GET /api/memory-documents/by-collection/{collection_id}"""
        response = client.get(f"/api/memory-documents/by-collection/{sample_memory_document.collection_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(d["id"] == sample_memory_document.id for d in data)

    def test_search_documents_endpoint(self, client: TestClient, sample_memory_document):
        """Test GET /api/memory-documents/search"""
        response = client.get("/api/memory-documents/search?q=test")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should find our sample document which contains "test"
        assert any(d["id"] == sample_memory_document.id for d in data)

    def test_update_document_endpoint(self, client: TestClient, sample_memory_document):
        """Test PUT /api/memory-documents/{id}"""
        update_data = {
            "content": "Updated via API",
            "metadatas": {"updated": True, "source": "api"}
        }
        
        response = client.put(
            f"/api/memory-documents/{sample_memory_document.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated via API"

    def test_archive_document_endpoint(self, client: TestClient, sample_memory_document):
        """Test DELETE /api/memory-documents/{id}"""
        response = client.delete(f"/api/memory-documents/{sample_memory_document.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["archived_at"] is not None

    def test_metadata_handling(self, client: TestClient, sample_memory_collection):
        """Test that metadata is properly handled as JSON"""
        document_data = {
            "chroma_id": "metadata_test_123",
            "content": "Testing metadata handling",
            "collection_id": sample_memory_collection.id,
            "metadatas": {
                "tags": ["test", "metadata"],
                "priority": 5,
                "active": True,
                "nested": {"key": "value"}
            }
        }
        
        # Create document
        response = client.post("/api/memory-documents/", json=document_data)
        assert response.status_code == 200
        created_doc = response.json()
        
        # Get document and verify metadata
        response = client.get(f"/api/memory-documents/{created_doc['id']}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["metadatas"]["tags"] == ["test", "metadata"]
        assert data["metadatas"]["priority"] == 5
        assert data["metadatas"]["active"] is True
        assert data["metadatas"]["nested"]["key"] == "value" 
 