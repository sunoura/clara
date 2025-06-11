import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from data.models import InteractionSessionCreate, InteractionSessionUpdate
from routes.interaction_session.ops import InteractionSessionOps


class TestInteractionSessionOps:
    """Test the InteractionSessionOps class"""

    def test_create_session(self, session: Session):
        """Test creating an interaction session"""
        session_data = InteractionSessionCreate(
            title="Test Chat Session",
            context_summary="Testing session creation"
        )
        interaction_session = InteractionSessionOps.create_session(session, session_data)
        
        assert interaction_session.id is not None
        assert len(interaction_session.id) == 36  # UUID length
        assert interaction_session.title == "Test Chat Session"
        assert interaction_session.context_summary == "Testing session creation"
        assert interaction_session.started_at is not None

    def test_get_session(self, session: Session, sample_interaction_session):
        """Test getting an interaction session by ID"""
        retrieved_session = InteractionSessionOps.get_session(session, sample_interaction_session.id)
        
        assert retrieved_session is not None
        assert retrieved_session.id == sample_interaction_session.id
        assert retrieved_session.title == sample_interaction_session.title

    def test_get_session_not_found(self, session: Session):
        """Test getting a non-existent session"""
        session_result = InteractionSessionOps.get_session(session, "non-existent-uuid")
        assert session_result is None

    def test_get_sessions(self, session: Session, sample_interaction_session):
        """Test getting all sessions"""
        sessions = InteractionSessionOps.get_sessions(session)
        
        assert len(sessions) >= 1
        assert any(s.id == sample_interaction_session.id for s in sessions)
        # Verify they're ordered by started_at desc (most recent first)
        if len(sessions) > 1:
            assert sessions[0].started_at >= sessions[1].started_at

    def test_get_recent_sessions(self, session: Session, sample_interaction_session):
        """Test getting recent sessions"""
        recent_sessions = InteractionSessionOps.get_recent_sessions(session, limit=5)
        
        assert len(recent_sessions) >= 1
        assert len(recent_sessions) <= 5
        assert any(s.id == sample_interaction_session.id for s in recent_sessions)

    def test_update_session(self, session: Session, sample_interaction_session):
        """Test updating an interaction session"""
        update_data = InteractionSessionUpdate(
            title="Updated Session Title",
            context_summary="Updated context summary"
        )
        
        updated_session = InteractionSessionOps.update_session(
            session, sample_interaction_session.id, update_data
        )
        
        assert updated_session is not None
        assert updated_session.title == "Updated Session Title"
        assert updated_session.context_summary == "Updated context summary"
        assert updated_session.id == sample_interaction_session.id

    def test_get_session_with_payloads(self, session: Session, sample_interaction_payload):
        """Test getting a session with its payloads"""
        session_with_payloads = InteractionSessionOps.get_session_with_payloads(
            session, sample_interaction_payload.session_id
        )
        
        assert session_with_payloads is not None
        assert session_with_payloads.id == sample_interaction_payload.session_id


class TestInteractionSessionRoutes:
    """Test the interaction session API routes"""

    def test_create_session_endpoint(self, client: TestClient):
        """Test POST /api/interaction-sessions/"""
        session_data = {
            "title": "API Test Session",
            "context_summary": "Created via API test"
        }
        
        response = client.post("/api/interaction-sessions/", json=session_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "API Test Session"
        assert data["context_summary"] == "Created via API test"
        assert "id" in data
        assert "started_at" in data
        assert len(data["id"]) == 36  # UUID length

    def test_create_session_minimal(self, client: TestClient):
        """Test creating session with minimal data"""
        session_data = {
            "title": "Minimal Session"
        }
        
        response = client.post("/api/interaction-sessions/", json=session_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minimal Session"
        assert data["context_summary"] is None

    def test_get_sessions_endpoint(self, client: TestClient, sample_interaction_session):
        """Test GET /api/interaction-sessions/"""
        response = client.get("/api/interaction-sessions/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_recent_sessions_endpoint(self, client: TestClient, sample_interaction_session):
        """Test GET /api/interaction-sessions/recent"""
        response = client.get("/api/interaction-sessions/recent?limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
        assert len(data) >= 1

    def test_get_session_endpoint(self, client: TestClient, sample_interaction_session):
        """Test GET /api/interaction-sessions/{id}"""
        response = client.get(f"/api/interaction-sessions/{sample_interaction_session.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_interaction_session.id
        assert data["title"] == sample_interaction_session.title

    def test_get_session_not_found(self, client: TestClient):
        """Test GET /api/interaction-sessions/{id} with non-existent ID"""
        fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/interaction-sessions/{fake_uuid}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_session_with_payloads_endpoint(self, client: TestClient, sample_interaction_payload):
        """Test GET /api/interaction-sessions/{id}/with-payloads"""
        response = client.get(f"/api/interaction-sessions/{sample_interaction_payload.session_id}/with-payloads")
        
        assert response.status_code == 200
        data = response.json()
        assert "payloads" in data
        assert len(data["payloads"]) >= 1
        assert any(p["id"] == sample_interaction_payload.id for p in data["payloads"])

    def test_update_session_endpoint(self, client: TestClient, sample_interaction_session):
        """Test PUT /api/interaction-sessions/{id}"""
        update_data = {
            "title": "Updated via API",
            "context_summary": "New summary via API"
        }
        
        response = client.put(
            f"/api/interaction-sessions/{sample_interaction_session.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated via API"
        assert data["context_summary"] == "New summary via API"
        assert data["id"] == sample_interaction_session.id

    def test_update_session_partial(self, client: TestClient, sample_interaction_session):
        """Test partial update of session"""
        update_data = {
            "title": "Only Title Updated"
        }
        
        response = client.put(
            f"/api/interaction-sessions/{sample_interaction_session.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Updated"
        # Context summary should remain unchanged
        assert data["context_summary"] == sample_interaction_session.context_summary

    def test_pagination(self, client: TestClient):
        """Test pagination parameters"""
        # Create multiple sessions
        for i in range(5):
            client.post("/api/interaction-sessions/", json={
                "title": f"Session {i}",
                "context_summary": f"Context {i}"
            })
        
        # Test with limit
        response = client.get("/api/interaction-sessions/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        
        # Test with skip
        response = client.get("/api/interaction-sessions/?skip=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_session_ordering(self, client: TestClient):
        """Test that sessions are returned in correct order (newest first)"""
        # Create sessions with different timestamps
        session_ids = []
        for i in range(3):
            response = client.post("/api/interaction-sessions/", json={
                "title": f"Session {i}",
                "context_summary": f"Context {i}"
            })
            session_ids.append(response.json()["id"])
        
        # Get all sessions
        response = client.get("/api/interaction-sessions/")
        data = response.json()
        
        # Find our created sessions in the response
        our_sessions = [s for s in data if s["id"] in session_ids]
        assert len(our_sessions) == 3
        
        # Verify they're ordered by started_at (newest first)
        for i in range(len(our_sessions) - 1):
            assert our_sessions[i]["started_at"] >= our_sessions[i + 1]["started_at"] 