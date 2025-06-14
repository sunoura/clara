import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import app
from db import get_session, create_db_and_tables
from data.models import Workspace, Project, Task


@pytest.fixture
def client():
    """Test client for API calls"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Database session for direct DB operations"""
    create_db_and_tables()
    with get_session() as session:
        yield session


class TestWorkspaceCRUD:
    """Test workspace CRUD operations"""
    
    def test_create_workspace(self, client):
        """Test workspace creation"""
        response = client.post("/api/clara/workspaces/", json={
            "title": "Test Workspace",
            "description": "A test workspace"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Workspace"
        assert data["description"] == "A test workspace"
        assert "id" in data
        assert "created_at" in data
        
    def test_get_workspace(self, client, db_session):
        """Test workspace retrieval"""
        # Create workspace directly in DB
        workspace = Workspace(title="Direct Workspace", description="Created directly")
        db_session.add(workspace)
        db_session.commit()
        db_session.refresh(workspace)
        
        # Retrieve via API
        response = client.get(f"/api/clara/workspaces/{workspace.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Direct Workspace"
        assert data["id"] == workspace.id
        
    def test_update_workspace(self, client):
        """Test workspace update"""
        # Create workspace
        response = client.post("/api/clara/workspaces/", json={
            "title": "Original Title",
            "description": "Original description"
        })
        workspace_id = response.json()["id"]
        
        # Update workspace
        response = client.put(f"/api/clara/workspaces/{workspace_id}", json={
            "title": "Updated Title",
            "description": "Updated description"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        
    def test_delete_workspace(self, client):
        """Test workspace deletion (archiving)"""
        # Create workspace
        response = client.post("/api/clara/workspaces/", json={
            "title": "To Delete",
            "description": "Will be deleted"
        })
        workspace_id = response.json()["id"]
        
        # Delete workspace
        response = client.delete(f"/api/clara/workspaces/{workspace_id}")
        assert response.status_code == 200
        
        # Verify it's archived (not actually deleted)
        response = client.get(f"/api/clara/workspaces/{workspace_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["archived_at"] is not None
        
    def test_get_all_workspaces_snapshot(self, client):
        """Test getting all workspace snapshots"""
        # Create multiple workspaces
        for i in range(3):
            client.post("/api/clara/workspaces/", json={
                "title": f"Workspace {i}",
                "description": f"Description {i}"
            })
            
        response = client.get("/api/clara/snapshots/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        
        # Check snapshot structure
        for workspace in data:
            assert "id" in workspace
            assert "title" in workspace
            assert "projects" in workspace
            assert "tasks" in workspace
            assert "notes" in workspace


class TestTaskCRUD:
    """Test task CRUD operations"""
    
    def test_create_root_task(self, client):
        """Test creating a root-level task"""
        # Create workspace first
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Task Workspace",
            "description": "For task testing"
        })
        workspace_id = workspace_response.json()["id"]
        
        # Create root task
        response = client.post("/api/clara/tasks/", json={
            "title": "Root Task",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Root Task"
        assert data["status"] == "todo"
        assert data["parent_task_id"] is None
        
    def test_create_subtask(self, client):
        """Test creating a subtask"""
        # Create workspace and parent task
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Subtask Workspace"
        })
        workspace_id = workspace_response.json()["id"]
        
        parent_response = client.post("/api/clara/tasks/", json={
            "title": "Parent Task",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        parent_id = parent_response.json()["id"]
        
        # Create subtask
        response = client.post("/api/clara/tasks/", json={
            "title": "Subtask",
            "workspace_id": workspace_id,
            "parent_task_id": parent_id,
            "status": "todo"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Subtask"
        assert data["parent_task_id"] == parent_id
        
    def test_update_task(self, client):
        """Test task update"""
        # Create workspace and task
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Update Workspace"
        })
        workspace_id = workspace_response.json()["id"]
        
        task_response = client.post("/api/clara/tasks/", json={
            "title": "Original Task",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        task_id = task_response.json()["id"]
        
        # Update task
        response = client.put(f"/api/clara/tasks/{task_id}", json={
            "title": "Updated Task",
            "status": "in-progress"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["status"] == "in-progress"
        
    def test_move_task_parent(self, client):
        """Test moving task to different parent (drag-and-drop simulation)"""
        # Create workspace
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Move Workspace"
        })
        workspace_id = workspace_response.json()["id"]
        
        # Create parent tasks
        parent1_response = client.post("/api/clara/tasks/", json={
            "title": "Parent 1",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        parent1_id = parent1_response.json()["id"]
        
        parent2_response = client.post("/api/clara/tasks/", json={
            "title": "Parent 2",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        parent2_id = parent2_response.json()["id"]
        
        # Create child task under parent1
        child_response = client.post("/api/clara/tasks/", json={
            "title": "Child Task",
            "workspace_id": workspace_id,
            "parent_task_id": parent1_id,
            "status": "todo"
        })
        child_id = child_response.json()["id"]
        
        # Move child from parent1 to parent2
        response = client.put(f"/api/clara/tasks/{child_id}", json={
            "parent_task_id": parent2_id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["parent_task_id"] == parent2_id
        
    def test_circular_dependency_prevention(self, client):
        """Test that circular dependencies are prevented"""
        # Create workspace
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Circular Test Workspace"
        })
        workspace_id = workspace_response.json()["id"]
        
        # Create parent task
        parent_response = client.post("/api/clara/tasks/", json={
            "title": "Parent Task",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        parent_id = parent_response.json()["id"]
        
        # Create child task
        child_response = client.post("/api/clara/tasks/", json={
            "title": "Child Task",
            "workspace_id": workspace_id,
            "parent_task_id": parent_id,
            "status": "todo"
        })
        child_id = child_response.json()["id"]
        
        # Try to make parent a child of child (should fail)
        response = client.put(f"/api/clara/tasks/{parent_id}", json={
            "parent_task_id": child_id
        })
        assert response.status_code == 400
        assert "circular dependency" in response.json()["detail"].lower()
        
    def test_delete_task(self, client):
        """Test task deletion"""
        # Create workspace and task
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Delete Workspace"
        })
        workspace_id = workspace_response.json()["id"]
        
        task_response = client.post("/api/clara/tasks/", json={
            "title": "Task to Delete",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        task_id = task_response.json()["id"]
        
        # Delete task
        response = client.delete(f"/api/clara/tasks/{task_id}")
        assert response.status_code == 200
        
        # Verify task is archived
        response = client.get(f"/api/clara/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["archived_at"] is not None
        
    def test_complete_task(self, client):
        """Test task completion"""
        # Create workspace and task
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Complete Workspace"
        })
        workspace_id = workspace_response.json()["id"]
        
        task_response = client.post("/api/clara/tasks/", json={
            "title": "Task to Complete",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        task_id = task_response.json()["id"]
        
        # Complete task
        response = client.post(f"/api/clara/tasks/{task_id}/complete")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"


class TestWorkspaceSnapshot:
    """Test workspace snapshot functionality"""
    
    def test_workspace_snapshot_structure(self, client):
        """Test that workspace snapshots have correct hierarchical structure"""
        # Create workspace
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Snapshot Workspace"
        })
        workspace_id = workspace_response.json()["id"]
        
        # Create hierarchical tasks
        # Root task
        root_response = client.post("/api/clara/tasks/", json={
            "title": "Root Task",
            "workspace_id": workspace_id,
            "status": "todo"
        })
        root_id = root_response.json()["id"]
        
        # Child task
        child_response = client.post("/api/clara/tasks/", json={
            "title": "Child Task",
            "workspace_id": workspace_id,
            "parent_task_id": root_id,
            "status": "todo"
        })
        child_id = child_response.json()["id"]
        
        # Grandchild task
        grandchild_response = client.post("/api/clara/tasks/", json={
            "title": "Grandchild Task",
            "workspace_id": workspace_id,
            "parent_task_id": child_id,
            "status": "todo"
        })
        
        # Get workspace snapshot
        response = client.get(f"/api/clara/workspaces/{workspace_id}/snapshot")
        assert response.status_code == 200
        data = response.json()
        
        # Verify hierarchical structure
        assert len(data["tasks"]) == 1  # Only root task at top level
        root_task = data["tasks"][0]
        assert root_task["title"] == "Root Task"
        assert len(root_task["subtasks"]) == 1  # One child
        
        child_task = root_task["subtasks"][0]
        assert child_task["title"] == "Child Task"
        assert len(child_task["subtasks"]) == 1  # One grandchild
        
        grandchild_task = child_task["subtasks"][0]
        assert grandchild_task["title"] == "Grandchild Task"
        assert len(grandchild_task["subtasks"]) == 0  # No children


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_nonexistent_workspace(self, client):
        """Test accessing non-existent workspace"""
        response = client.get("/api/clara/workspaces/99999")
        assert response.status_code == 404
        
    def test_nonexistent_task(self, client):
        """Test accessing non-existent task"""
        response = client.get("/api/clara/tasks/99999")
        assert response.status_code == 404
        
    def test_invalid_task_status(self, client):
        """Test creating task with invalid status"""
        workspace_response = client.post("/api/clara/workspaces/", json={
            "title": "Invalid Status Workspace"
        })
        workspace_id = workspace_response.json()["id"]
        
        response = client.post("/api/clara/tasks/", json={
            "title": "Invalid Task",
            "workspace_id": workspace_id,
            "status": "invalid-status"
        })
        assert response.status_code == 422  # Validation error
        
    def test_task_without_workspace(self, client):
        """Test creating task without workspace"""
        response = client.post("/api/clara/tasks/", json={
            "title": "Orphan Task",
            "status": "todo"
            # Missing workspace_id
        })
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 