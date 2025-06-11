import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from data.models import InteractionPayloadCreate, InteractionPayloadUpdate, InteractionFrom
from services.interaction_service import InteractionService


class TestInteractionService:
    """Test the InteractionService class (payloads)"""

    def test_create_payload(self, session: Session, sample_interaction_session):
        """Test creating an interaction payload"""
        service = InteractionService()
        payload_data = InteractionPayloadCreate(
            session_id=sample_interaction_session.id,
            content="Test payload content",
            ok=True,
            **{"from": InteractionFrom.USER}
        )
        payload = service.create_payload(session, payload_data)
        
        assert payload.id is not None
        assert payload.session_id == sample_interaction_session.id
        assert payload.content == "Test payload content"
        assert payload.ok is True
        assert payload.from_ == InteractionFrom.USER
        assert payload.created_at is not None

    def test_get_payload(self, session: Session, sample_interaction_payload):
        """Test getting an interaction payload by ID"""
        service = InteractionService()
        payload = service.get_payload(session, sample_interaction_payload.id)
        
        assert payload is not None
        assert payload.id == sample_interaction_payload.id
        assert payload.content == sample_interaction_payload.content

    def test_get_payload_not_found(self, session: Session):
        """Test getting a non-existent payload"""
        service = InteractionService()
        payload = service.get_payload(session, 999)
        assert payload is None

    def test_get_session_payloads(self, session: Session, sample_interaction_payload):
        """Test getting payloads by session"""
        service = InteractionService()
        payloads = service.get_session_payloads(session, sample_interaction_payload.session_id)
        
        assert len(payloads) >= 1
        assert any(p.id == sample_interaction_payload.id for p in payloads)

    def test_get_payloads(self, session: Session, sample_interaction_payload):
        """Test getting all payloads"""
        service = InteractionService()
        payloads = service.get_payloads(session)
        
        assert len(payloads) >= 1
        assert any(p.id == sample_interaction_payload.id for p in payloads)

    def test_update_payload(self, session: Session, sample_interaction_payload):
        """Test updating an interaction payload"""
        service = InteractionService()
        
        update_data = InteractionPayloadUpdate(
            content="Updated content",
            ok=False
        )
        
        updated_payload = service.update_payload(
            session, sample_interaction_payload.id, update_data
        )
        
        assert updated_payload is not None
        assert updated_payload.content == "Updated content"
        assert updated_payload.ok is False


class TestInteractionPayloadRoutes:
    """Test the interaction payload API routes"""

    def test_create_payload_endpoint(self, client: TestClient, sample_interaction_session):
        """Test POST /api/interaction-payloads/"""
        payload_data = {
            "session_id": sample_interaction_session.id,
            "content": "API test payload",
            "ok": True,
            "from": "user"
        }
        
        response = client.post("/api/interaction-payloads/", json=payload_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "API test payload"
        assert data["ok"] is True
        assert data["from"] == "user"
        assert "id" in data

    def test_get_payloads_endpoint(self, client: TestClient, sample_interaction_payload):
        """Test GET /api/interaction-payloads/"""
        response = client.get("/api/interaction-payloads/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_payload_endpoint(self, client: TestClient, sample_interaction_payload):
        """Test GET /api/interaction-payloads/{id}"""
        response = client.get(f"/api/interaction-payloads/{sample_interaction_payload.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_interaction_payload.id

    def test_get_payload_not_found(self, client: TestClient):
        """Test GET /api/interaction-payloads/{id} with non-existent ID"""
        response = client.get("/api/interaction-payloads/999")
        
        assert response.status_code == 404

    def test_get_payloads_by_session_endpoint(self, client: TestClient, sample_interaction_payload):
        """Test GET /api/interaction-payloads/by-session/{session_id}"""
        response = client.get(f"/api/interaction-payloads/by-session/{sample_interaction_payload.session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_update_payload_endpoint(self, client: TestClient, sample_interaction_payload):
        """Test PUT /api/interaction-payloads/{id}"""
        update_data = {
            "content": "Updated via API",
            "ok": False
        }
        
        response = client.put(
            f"/api/interaction-payloads/{sample_interaction_payload.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated via API"
        assert data["ok"] is False 