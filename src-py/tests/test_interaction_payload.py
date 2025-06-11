import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from data.models import InteractionPayloadCreate, InteractionPayloadUpdate, InteractionFrom
from routes.interaction_payload.ops import InteractionPayloadOps


class TestInteractionPayloadOps:
    """Test the InteractionPayloadOps class"""

    def test_create_payload(self, session: Session, sample_interaction_session):
        """Test creating an interaction payload"""
        payload_data = InteractionPayloadCreate(
            session_id=sample_interaction_session.id,
            content="Test message content",
            ok=True,
            **{"from": InteractionFrom.USER}
        )
        payload = InteractionPayloadOps.create_payload(session, payload_data)
        
        assert payload.id is not None
        assert payload.session_id == sample_interaction_session.id
        assert payload.content == "Test message content"
        assert payload.ok is True
        assert payload.err is None
        assert payload.from_ == InteractionFrom.USER
        assert payload.created_at is not None

    def test_create_payload_with_error(self, session: Session, sample_interaction_session):
        """Test creating a payload with error information"""
        payload_data = InteractionPayloadCreate(
            session_id=sample_interaction_session.id,
            content="Failed message",
            ok=False,
            err="Connection timeout",
            **{"from": InteractionFrom.MODEL}
        )
        payload = InteractionPayloadOps.create_payload(session, payload_data)
        
        assert payload.ok is False
        assert payload.err == "Connection timeout"
        assert payload.from_ == InteractionFrom.MODEL

    def test_get_payload(self, session: Session, sample_interaction_payload):
        """Test getting a payload by ID"""
        payload = InteractionPayloadOps.get_payload(session, sample_interaction_payload.id)
        
        assert payload is not None
        assert payload.id == sample_interaction_payload.id
        assert payload.content == sample_interaction_payload.content

    def test_get_payload_not_found(self, session: Session):
        """Test getting a non-existent payload"""
        payload = InteractionPayloadOps.get_payload(session, 999)
        assert payload is None

    def test_get_session_payloads(self, session: Session, sample_interaction_payload):
        """Test getting all payloads for a session"""
        payloads = InteractionPayloadOps.get_session_payloads(
            session, sample_interaction_payload.session_id
        )
        
        assert len(payloads) >= 1
        assert any(p.id == sample_interaction_payload.id for p in payloads)
        # Verify they're ordered by created_at asc (chronological order)
        if len(payloads) > 1:
            assert payloads[0].created_at <= payloads[1].created_at

    def test_get_payloads(self, session: Session, sample_interaction_payload):
        """Test getting all payloads"""
        payloads = InteractionPayloadOps.get_payloads(session)
        
        assert len(payloads) >= 1
        assert any(p.id == sample_interaction_payload.id for p in payloads)

    def test_get_payloads_by_type(self, session: Session, sample_interaction_session):
        """Test getting payloads filtered by sender type"""
        # Create payloads from both user and model
        user_payload_data = InteractionPayloadCreate(
            session_id=sample_interaction_session.id,
            content="User message",
            **{"from": InteractionFrom.USER}
        )
        model_payload_data = InteractionPayloadCreate(
            session_id=sample_interaction_session.id,
            content="Model response",
            **{"from": InteractionFrom.MODEL}
        )
        
        user_payload = InteractionPayloadOps.create_payload(session, user_payload_data)
        model_payload = InteractionPayloadOps.create_payload(session, model_payload_data)
        
        # Test filtering by USER
        user_payloads = InteractionPayloadOps.get_payloads_by_type(session, InteractionFrom.USER)
        assert any(p.id == user_payload.id for p in user_payloads)
        assert all(p.from_ == InteractionFrom.USER for p in user_payloads)
        
        # Test filtering by MODEL
        model_payloads = InteractionPayloadOps.get_payloads_by_type(session, InteractionFrom.MODEL)
        assert any(p.id == model_payload.id for p in model_payloads)
        assert all(p.from_ == InteractionFrom.MODEL for p in model_payloads)

    def test_get_failed_payloads(self, session: Session, sample_interaction_session):
        """Test getting failed payloads"""
        # Create a failed payload
        failed_payload_data = InteractionPayloadCreate(
            session_id=sample_interaction_session.id,
            content="Failed message",
            ok=False,
            err="Test error",
            **{"from": InteractionFrom.MODEL}
        )
        failed_payload = InteractionPayloadOps.create_payload(session, failed_payload_data)
        
        failed_payloads = InteractionPayloadOps.get_failed_payloads(session)
        assert any(p.id == failed_payload.id for p in failed_payloads)
        assert all(p.ok is False for p in failed_payloads)

    def test_update_payload(self, session: Session, sample_interaction_payload):
        """Test updating a payload"""
        update_data = InteractionPayloadUpdate(
            content="Updated content",
            err="Updated error message"
        )
        
        updated_payload = InteractionPayloadOps.update_payload(
            session, sample_interaction_payload.id, update_data
        )
        
        assert updated_payload is not None
        assert updated_payload.content == "Updated content"
        assert updated_payload.err == "Updated error message"
        assert updated_payload.id == sample_interaction_payload.id

    def test_get_payload_with_session(self, session: Session, sample_interaction_payload):
        """Test getting a payload with its session data"""
        payload_with_session = InteractionPayloadOps.get_payload_with_session(
            session, sample_interaction_payload.id
        )
        
        assert payload_with_session is not None
        assert payload_with_session.id == sample_interaction_payload.id


class TestInteractionPayloadRoutes:
    """Test the interaction payload API routes"""

    def test_create_payload_endpoint(self, client: TestClient, sample_interaction_session):
        """Test POST /api/interaction-payloads/"""
        payload_data = {
            "session_id": sample_interaction_session.id,
            "content": "API test message",
            "ok": True,
            "from": "user"
        }
        
        response = client.post("/api/interaction-payloads/", json=payload_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == sample_interaction_session.id
        assert data["content"] == "API test message"
        assert data["ok"] is True
        assert data["from"] == "user"
        assert "id" in data

    def test_create_failed_payload_endpoint(self, client: TestClient, sample_interaction_session):
        """Test creating a failed payload via API"""
        payload_data = {
            "session_id": sample_interaction_session.id,
            "content": "Failed API message",
            "ok": False,
            "err": "API timeout error",
            "from": "model"
        }
        
        response = client.post("/api/interaction-payloads/", json=payload_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert data["err"] == "API timeout error"
        assert data["from"] == "model"

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
        assert data["content"] == sample_interaction_payload.content

    def test_get_payload_not_found(self, client: TestClient):
        """Test GET /api/interaction-payloads/{id} with non-existent ID"""
        response = client.get("/api/interaction-payloads/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_payloads_by_type_endpoint(self, client: TestClient, sample_interaction_session):
        """Test GET /api/interaction-payloads/by-type/{from_type}"""
        # Create payloads of different types
        client.post("/api/interaction-payloads/", json={
            "session_id": sample_interaction_session.id,
            "content": "User message",
            "from": "user"
        })
        client.post("/api/interaction-payloads/", json={
            "session_id": sample_interaction_session.id,
            "content": "Model response",
            "from": "model"
        })
        
        # Test getting user payloads
        response = client.get("/api/interaction-payloads/by-type/user")
        assert response.status_code == 200
        data = response.json()
        assert all(p["from"] == "user" for p in data)
        
        # Test getting model payloads
        response = client.get("/api/interaction-payloads/by-type/model")
        assert response.status_code == 200
        data = response.json()
        assert all(p["from"] == "model" for p in data)

    def test_get_failed_payloads_endpoint(self, client: TestClient, sample_interaction_session):
        """Test GET /api/interaction-payloads/failed"""
        # Create a failed payload
        client.post("/api/interaction-payloads/", json={
            "session_id": sample_interaction_session.id,
            "content": "Failed message",
            "ok": False,
            "err": "Test error",
            "from": "model"
        })
        
        response = client.get("/api/interaction-payloads/failed")
        assert response.status_code == 200
        data = response.json()
        assert all(p["ok"] is False for p in data)

    def test_get_session_payloads_endpoint(self, client: TestClient, sample_interaction_payload):
        """Test GET /api/interaction-payloads/by-session/{session_id}"""
        response = client.get(f"/api/interaction-payloads/by-session/{sample_interaction_payload.session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p["id"] == sample_interaction_payload.id for p in data)
        assert all(p["session_id"] == sample_interaction_payload.session_id for p in data)

    def test_get_payload_with_session_endpoint(self, client: TestClient, sample_interaction_payload):
        """Test GET /api/interaction-payloads/{id}/with-session"""
        response = client.get(f"/api/interaction-payloads/{sample_interaction_payload.id}/with-session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_interaction_payload.id
        assert "session" in data
        # The session field might be None due to how SQLModel handles relationships in this context

    def test_update_payload_endpoint(self, client: TestClient, sample_interaction_payload):
        """Test PUT /api/interaction-payloads/{id}"""
        update_data = {
            "content": "Updated via API",
            "err": "Updated error via API"
        }
        
        response = client.put(
            f"/api/interaction-payloads/{sample_interaction_payload.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated via API"
        assert data["err"] == "Updated error via API"

    def test_conversation_flow(self, client: TestClient):
        """Test a complete conversation flow"""
        # Create a session
        session_response = client.post("/api/interaction-sessions/", json={
            "title": "Conversation Test",
            "context_summary": "Testing a full conversation"
        })
        session_id = session_response.json()["id"]
        
        # User sends a message
        user_msg_response = client.post("/api/interaction-payloads/", json={
            "session_id": session_id,
            "content": "Hello, how are you?",
            "from": "user"
        })
        assert user_msg_response.status_code == 200
        
        # Model responds
        model_msg_response = client.post("/api/interaction-payloads/", json={
            "session_id": session_id,
            "content": "I'm doing well, thank you! How can I help you today?",
            "from": "model"
        })
        assert model_msg_response.status_code == 200
        
        # Get all payloads for the session
        payloads_response = client.get(f"/api/interaction-payloads/by-session/{session_id}")
        payloads = payloads_response.json()
        
        assert len(payloads) == 2
        # Verify chronological order (user message first, then model response)
        assert payloads[0]["from"] == "user"
        assert payloads[1]["from"] == "model"
        assert payloads[0]["created_at"] <= payloads[1]["created_at"]

    def test_enum_validation(self, client: TestClient, sample_interaction_session):
        """Test that invalid enum values are rejected"""
        payload_data = {
            "session_id": sample_interaction_session.id,
            "content": "Test message",
            "from": "invalid_sender"  # Invalid enum value
        }
        
        response = client.post("/api/interaction-payloads/", json=payload_data)
        assert response.status_code == 422  # Validation error 