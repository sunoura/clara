#!/usr/bin/env python3
"""
Seed script for Clara task management system
Creates initial workspaces, projects, and tasks for testing
"""

from datetime import datetime, UTC, timedelta
from db import session_from_generator
from services.clara_service import ClaraService
from data.models.clara_models import WorkspaceCreate, ProjectCreate, TaskCreate
from data.models._schemas import TaskStatus


def seed_clara_data():
    """Seed initial Clara data"""
    with session_from_generator() as session:
        service = ClaraService(session)
        
        # Create workspaces
        personal_workspace = service.create_workspace(WorkspaceCreate(
            title="Personal",
            description="Personal tasks and projects"
        ))
        
        work_workspace = service.create_workspace(WorkspaceCreate(
            title="Work",
            description="Professional tasks and projects"
        ))
        
        # Create projects in Personal workspace
        home_project = service.create_project(ProjectCreate(
            title="Home Improvements",
            description="Tasks related to home maintenance and improvements",
            workspace_id=personal_workspace.id
        ))
        
        health_project = service.create_project(ProjectCreate(
            title="Health & Fitness",
            description="Personal health and fitness goals",
            workspace_id=personal_workspace.id
        ))
        
        # Create projects in Work workspace
        website_project = service.create_project(ProjectCreate(
            title="Website Redesign",
            description="Complete redesign of company website",
            workspace_id=work_workspace.id
        ))
        
        # Create tasks in Home Improvements project
        service.create_task(TaskCreate(
            title="Fix leaky faucet in kitchen",
            workspace_id=personal_workspace.id,
            project_id=home_project.id,
            status=TaskStatus.TODO,
            due_date=datetime.now(UTC) + timedelta(days=7)
        ))
        
        service.create_task(TaskCreate(
            title="Paint living room walls",
            workspace_id=personal_workspace.id,
            project_id=home_project.id,
            status=TaskStatus.IN_PROGRESS
        ))
        
        service.create_task(TaskCreate(
            title="Replace broken tile in bathroom",
            workspace_id=personal_workspace.id,
            project_id=home_project.id,
            status=TaskStatus.TODO
        ))
        
        # Create tasks in Health & Fitness project
        service.create_task(TaskCreate(
            title="Schedule annual physical exam",
            workspace_id=personal_workspace.id,
            project_id=health_project.id,
            status=TaskStatus.TODO,
            due_date=datetime.now(UTC) + timedelta(days=14)
        ))
        
        service.create_task(TaskCreate(
            title="Start morning jogging routine",
            workspace_id=personal_workspace.id,
            project_id=health_project.id,
            status=TaskStatus.IN_PROGRESS
        ))
        
        # Create tasks in Website Redesign project
        service.create_task(TaskCreate(
            title="Research competitor websites",
            workspace_id=work_workspace.id,
            project_id=website_project.id,
            status=TaskStatus.DONE
        ))
        
        design_task = service.create_task(TaskCreate(
            title="Create wireframes and mockups",
            workspace_id=work_workspace.id,
            project_id=website_project.id,
            status=TaskStatus.IN_PROGRESS
        ))
        
        # Create subtasks for the design task
        service.create_task(TaskCreate(
            title="Design homepage layout",
            workspace_id=work_workspace.id,
            project_id=website_project.id,
            parent_task_id=design_task.id,
            status=TaskStatus.TODO
        ))
        
        service.create_task(TaskCreate(
            title="Design product page template",
            workspace_id=work_workspace.id,
            project_id=website_project.id,
            parent_task_id=design_task.id,
            status=TaskStatus.TODO
        ))
        
        service.create_task(TaskCreate(
            title="Develop responsive CSS framework",
            workspace_id=work_workspace.id,
            project_id=website_project.id,
            status=TaskStatus.TODO,
            due_date=datetime.now(UTC) + timedelta(days=21)
        ))
        
        # Create some tasks directly under workspace (not in projects)
        service.create_task(TaskCreate(
            title="Buy groceries",
            workspace_id=personal_workspace.id,
            status=TaskStatus.TODO,
            due_date=datetime.now(UTC) + timedelta(days=2)
        ))
        
        service.create_task(TaskCreate(
            title="Review quarterly budget",
            workspace_id=work_workspace.id,
            status=TaskStatus.TODO,
            due_date=datetime.now(UTC) + timedelta(days=5)
        ))
        
        print("✅ Clara seed data created successfully!")
        print(f"Created workspaces: {personal_workspace.title}, {work_workspace.title}")
        print(f"Created projects: {home_project.title}, {health_project.title}, {website_project.title}")
        print("Created various tasks and subtasks across workspaces and projects")


if __name__ == "__main__":
    seed_clara_data() 