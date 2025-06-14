from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from db import get_session
from services.clara_service import ClaraService
from data.models.clara_models import (
    WorkspaceCreate, WorkspaceRead, WorkspaceUpdate, WorkspaceSnapshot,
    ProjectCreate, ProjectRead, ProjectUpdate, ProjectSnapshot,
    TaskCreate, TaskRead, TaskUpdate, TaskSnapshot,
    NoteCreate, NoteRead, NoteUpdate,
    CalendarEventCreate, CalendarEventRead, CalendarEventUpdate,
    ReminderCreate, ReminderRead, ReminderUpdate,
    TagCreate, TagRead, TagUpdate,
)

router = APIRouter(prefix="/clara", tags=["clara"])


def get_clara_service(session: Session = Depends(get_session)) -> ClaraService:
    return ClaraService(session)


# Workspace endpoints
@router.post("/workspaces/", response_model=WorkspaceRead)
def create_workspace(
    workspace: WorkspaceCreate,
    service: ClaraService = Depends(get_clara_service)
):
    return service.create_workspace(workspace)


@router.get("/workspaces/", response_model=List[WorkspaceRead])
def get_workspaces(service: ClaraService = Depends(get_clara_service)):
    return service.get_workspaces()


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(
    workspace_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    workspace = service.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.put("/workspaces/{workspace_id}", response_model=WorkspaceRead)
def update_workspace(
    workspace_id: int,
    workspace: WorkspaceUpdate,
    service: ClaraService = Depends(get_clara_service)
):
    updated_workspace = service.update_workspace(workspace_id, workspace)
    if not updated_workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return updated_workspace


@router.delete("/workspaces/{workspace_id}", response_model=WorkspaceRead)
def archive_workspace(
    workspace_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    archived_workspace = service.archive_workspace(workspace_id)
    if not archived_workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return archived_workspace


# Project endpoints
@router.post("/projects/", response_model=ProjectRead)
def create_project(
    project: ProjectCreate,
    service: ClaraService = Depends(get_clara_service)
):
    return service.create_project(project)


@router.get("/workspaces/{workspace_id}/projects/", response_model=List[ProjectRead])
def get_projects_by_workspace(
    workspace_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    return service.get_projects_by_workspace(workspace_id)


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    service: ClaraService = Depends(get_clara_service)
):
    updated_project = service.update_project(project_id, project)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.delete("/projects/{project_id}", response_model=ProjectRead)
def archive_project(
    project_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    archived_project = service.archive_project(project_id)
    if not archived_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return archived_project


# Task endpoints
@router.post("/tasks/", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    service: ClaraService = Depends(get_clara_service)
):
    return service.create_task(task)


@router.get("/workspaces/{workspace_id}/tasks/", response_model=List[TaskRead])
def get_tasks_by_workspace(
    workspace_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    return service.get_tasks_by_workspace(workspace_id)


@router.get("/projects/{project_id}/tasks/", response_model=List[TaskRead])
def get_tasks_by_project(
    project_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    return service.get_tasks_by_project(project_id)


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task: TaskUpdate,
    service: ClaraService = Depends(get_clara_service)
):
    updated_task = service.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.post("/tasks/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    completed_task = service.complete_task(task_id)
    if not completed_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return completed_task


@router.delete("/tasks/{task_id}", response_model=TaskRead)
def archive_task(
    task_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    archived_task = service.archive_task(task_id)
    if not archived_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return archived_task


# Snapshot endpoints - Core feature for fast JSON loading
@router.get("/workspaces/{workspace_id}/snapshot", response_model=WorkspaceSnapshot)
def get_workspace_snapshot(
    workspace_id: int,
    service: ClaraService = Depends(get_clara_service)
):
    """Get the complete hierarchical snapshot of a workspace for fast frontend loading"""
    snapshot = service.get_workspace_snapshot(workspace_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return snapshot


@router.get("/snapshots/", response_model=List[WorkspaceSnapshot])
def get_all_workspaces_snapshot(service: ClaraService = Depends(get_clara_service)):
    """Get snapshots of all workspaces - the main data load for the frontend"""
    return service.get_all_workspaces_snapshot() 