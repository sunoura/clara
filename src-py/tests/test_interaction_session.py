import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from data.models import InteractionSessionCreate, InteractionSessionUpdate
from services.interaction_service import InteractionService


class TestInteractionService:
    """Test the InteractionService class (sessions)"""

    def test_create_session(self, session: Session):
        """Test creating an interaction session"""
        service = InteractionService()
        session_data = InteractionSessionCreate(
            title="Test Session",
            context_summary="Testing session creation"
        )
        interaction_session = service.create_session(session, session_data)
        
        assert interaction_session.id is not None
        assert interaction_session.title == "Test Session"
        assert interaction_session.context_summary == "Testing session creation"
        assert interaction_session.started_at is not None

    def test_get_session(self, session: Session, sample_interaction_session):
        """Test getting an interaction session by ID"""
        service = InteractionService()
        interaction_session = service.get_session(session, sample_interaction_session.id)
        
        assert interaction_session is not None
        assert interaction_session.id == sample_interaction_session.id
        assert interaction_session.title == sample_interaction_session.title

    def test_get_session_not_found(self, session: Session):
        """Test getting a non-existent session"""
        service = InteractionService()
        interaction_session = service.get_session(session, "non-existent-uuid")
        assert interaction_session is None

    def test_get_sessions(self, session: Session, sample_interaction_session):
        """Test getting all interaction sessions"""
        service = InteractionService()
        sessions = service.get_sessions(session)
        
        assert len(sessions) >= 1
        assert any(s.id == sample_interaction_session.id for s in sessions)

    def test_update_session(self, session: Session, sample_interaction_session):
        """Test updating an interaction session"""
        service = InteractionService()
        
        update_data = InteractionSessionUpdate(
            title="Updated Session",
            context_summary="Updated context"
        )
        
        updated_session = service.update_session(
            session, sample_interaction_session.id, update_data
        )
        
        assert updated_session is not None
        assert updated_session.title == "Updated Session"
        assert updated_session.context_summary == "Updated context"

    def test_delete_session(self, session: Session, sample_interaction_session):
        """Test deleting an interaction session"""
        service = InteractionService()
        deleted = service.delete_session(session, sample_interaction_session.id)
        
        assert deleted is True
        
        # Verify session no longer exists
        sessions = service.get_sessions(session)
        assert not any(s.id == sample_interaction_session.id for s in sessions)


class TestInteractionSessionRoutes:
    """Test the interaction session API routes"""

    def test_create_session_endpoint(self, client: TestClient):
        """Test POST /api/interaction-sessions/"""
        session_data = {
            "title": "API Test Session",
            "context_summary": "Created via API"
        }
        
        response = client.post("/api/interaction-sessions/", json=session_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "API Test Session"
        assert data["context_summary"] == "Created via API"
        assert "id" in data

    def test_get_sessions_endpoint(self, client: TestClient, sample_interaction_session):
        """Test GET /api/interaction-sessions/"""
        response = client.get("/api/interaction-sessions/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_session_endpoint(self, client: TestClient, sample_interaction_session):
        """Test GET /api/interaction-sessions/{id}"""
        response = client.get(f"/api/interaction-sessions/{sample_interaction_session.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_interaction_session.id

    def test_get_session_not_found(self, client: TestClient):
        """Test GET /api/interaction-sessions/{id} with non-existent ID"""
        fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/interaction-sessions/{fake_uuid}")
        
        assert response.status_code == 404

    def test_update_session_endpoint(self, client: TestClient, sample_interaction_session):
        """Test PUT /api/interaction-sessions/{id}"""
        update_data = {
            "title": "Updated via API",
            "context_summary": "New context"
        }
        
        response = client.put(
            f"/api/interaction-sessions/{sample_interaction_session.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated via API"

    def test_delete_session_endpoint(self, client: TestClient, sample_interaction_session):
        """Test DELETE /api/interaction-sessions/{id}"""
        response = client.delete(f"/api/interaction-sessions/{sample_interaction_session.id}")
        
        assert response.status_code == 200

    def test_get_recent_sessions(self, client: TestClient):
        """Test GET /api/interaction-sessions/recent"""
        # Create multiple sessions
        for i in range(3):
            client.post("/api/interaction-sessions/", json={
                "title": f"Recent Session {i}",
                "context_summary": f"Context {i}"
            })
        
        response = client.get("/api/interaction-sessions/recent?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2 