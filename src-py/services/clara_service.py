from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, UTC
import json

# Database models from _schemas
from data.models._schemas import (
    Workspace, Project, Task, Note, CalendarEvent, Reminder, 
    ActivityLog, Tag, TaggedItem, TaskStatus
)
# API models from clara_models
from data.models.clara_models import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceSnapshot,
    ProjectCreate, ProjectUpdate, ProjectSnapshot,
    TaskCreate, TaskUpdate, TaskSnapshot,
    NoteCreate, NoteUpdate, NoteRead,
    CalendarEventCreate, CalendarEventUpdate, CalendarEventRead,
    ReminderCreate, ReminderUpdate, ReminderRead,
    TagCreate, TagUpdate
)


class ClaraService:
    def __init__(self, session: Session):
        self.session = session

    def log_activity(self, action_type: str, entity_type: str, entity_id: int, data: dict = None):
        """Log an activity to the activity log"""
        # Convert datetime objects to strings for JSON serialization
        if data:
            serializable_data = {}
            for key, value in data.items():
                if isinstance(value, datetime):
                    serializable_data[key] = value.isoformat()
                else:
                    serializable_data[key] = value
        else:
            serializable_data = {}
            
        activity = ActivityLog(
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            data=json.dumps(serializable_data),
            created_at=datetime.now(UTC)
        )
        self.session.add(activity)
        self.session.commit()

    # Workspace operations
    def create_workspace(self, workspace_data: WorkspaceCreate) -> Workspace:
        workspace = Workspace(**workspace_data.model_dump())
        self.session.add(workspace)
        self.session.commit()
        self.session.refresh(workspace)
        self.log_activity("create", "workspace", workspace.id, workspace_data.model_dump())
        return workspace

    def get_workspace(self, workspace_id: int) -> Optional[Workspace]:
        return self.session.get(Workspace, workspace_id)

    def get_workspaces(self) -> List[Workspace]:
        return self.session.exec(select(Workspace).where(Workspace.archived_at.is_(None))).all()

    def update_workspace(self, workspace_id: int, workspace_data: WorkspaceUpdate) -> Optional[Workspace]:
        workspace = self.session.get(Workspace, workspace_id)
        if not workspace:
            return None
        
        update_data = workspace_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(workspace, key, value)
        
        workspace.updated_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(workspace)
        self.log_activity("update", "workspace", workspace.id, update_data)
        return workspace

    def archive_workspace(self, workspace_id: int) -> Optional[Workspace]:
        workspace = self.session.get(Workspace, workspace_id)
        if not workspace:
            return None
        
        workspace.archived_at = datetime.now(UTC)
        self.session.commit()
        self.log_activity("archive", "workspace", workspace.id)
        return workspace

    # Project operations
    def create_project(self, project_data: ProjectCreate) -> Project:
        project = Project(**project_data.model_dump())
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        self.log_activity("create", "project", project.id, project_data.model_dump())
        return project

    def get_project(self, project_id: int) -> Optional[Project]:
        return self.session.get(Project, project_id)

    def get_projects_by_workspace(self, workspace_id: int) -> List[Project]:
        return self.session.exec(
            select(Project).where(
                Project.workspace_id == workspace_id,
                Project.archived_at.is_(None)
            )
        ).all()

    def update_project(self, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
        project = self.session.get(Project, project_id)
        if not project:
            return None
        
        update_data = project_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        
        project.updated_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(project)
        self.log_activity("update", "project", project.id, update_data)
        return project

    def archive_project(self, project_id: int) -> Optional[Project]:
        project = self.session.get(Project, project_id)
        if not project:
            return None
        
        project.archived_at = datetime.now(UTC)
        self.session.commit()
        self.log_activity("archive", "project", project.id)
        return project

    # Task operations
    def create_task(self, task_data: TaskCreate) -> Task:
        task = Task(**task_data.model_dump())
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        self.log_activity("create", "task", task.id, task_data.model_dump())
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def get_tasks_by_workspace(self, workspace_id: int) -> List[Task]:
        return self.session.exec(
            select(Task).where(
                Task.workspace_id == workspace_id,
                Task.archived_at.is_(None)
            )
        ).all()

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        return self.session.exec(
            select(Task).where(
                Task.project_id == project_id,
                Task.archived_at.is_(None)
            )
        ).all()

    def get_subtasks(self, parent_task_id: int) -> List[Task]:
        return self.session.exec(
            select(Task).where(
                Task.parent_task_id == parent_task_id,
                Task.archived_at.is_(None)
            )
        ).all()

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        
        task.updated_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(task)
        self.log_activity("update", "task", task.id, update_data)
        return task

    def archive_task(self, task_id: int) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if not task:
            return None
        
        task.archived_at = datetime.now(UTC)
        self.session.commit()
        self.log_activity("archive", "task", task.id)
        return task

    def complete_task(self, task_id: int) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if not task:
            return None
        
        task.status = TaskStatus.DONE
        task.updated_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(task)
        self.log_activity("complete", "task", task.id)
        return task

    # Hierarchical snapshot methods
    def build_task_snapshot(self, task: Task) -> TaskSnapshot:
        """Build a complete task snapshot with all nested data"""
        subtasks = [self.build_task_snapshot(subtask) for subtask in self.get_subtasks(task.id)]
        
        notes = self.session.exec(
            select(Note).where(
                Note.attached_to_type == "task",
                Note.attached_to_id == task.id,
                Note.archived_at.is_(None)
            )
        ).all()
        
        calendar_events = self.session.exec(
            select(CalendarEvent).where(
                CalendarEvent.linked_to_type == "task",
                CalendarEvent.linked_to_id == task.id,
                CalendarEvent.archived_at.is_(None)
            )
        ).all()
        
        reminders = self.session.exec(
            select(Reminder).where(
                Reminder.linked_to_type == "task",
                Reminder.linked_to_id == task.id,
                Reminder.archived_at.is_(None)
            )
        ).all()
        
        return TaskSnapshot(
            id=task.id,
            title=task.title,
            status=task.status,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            subtasks=subtasks,
            notes=[NoteRead.model_validate(note) for note in notes],
            calendar_events=[CalendarEventRead.model_validate(event) for event in calendar_events],
            reminders=[ReminderRead.model_validate(reminder) for reminder in reminders]
        )

    def build_project_snapshot(self, project: Project) -> ProjectSnapshot:
        """Build a complete project snapshot with all nested data"""
        tasks = self.get_tasks_by_project(project.id)
        task_snapshots = [self.build_task_snapshot(task) for task in tasks if task.parent_task_id is None]
        
        notes = self.session.exec(
            select(Note).where(
                Note.attached_to_type == "project",
                Note.attached_to_id == project.id,
                Note.archived_at.is_(None)
            )
        ).all()
        
        calendar_events = self.session.exec(
            select(CalendarEvent).where(
                CalendarEvent.linked_to_type == "project",
                CalendarEvent.linked_to_id == project.id,
                CalendarEvent.archived_at.is_(None)
            )
        ).all()
        
        reminders = self.session.exec(
            select(Reminder).where(
                Reminder.linked_to_type == "project",
                Reminder.linked_to_id == project.id,
                Reminder.archived_at.is_(None)
            )
        ).all()
        
        return ProjectSnapshot(
            id=project.id,
            title=project.title,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            tasks=task_snapshots,
            notes=[NoteRead.model_validate(note) for note in notes],
            calendar_events=[CalendarEventRead.model_validate(event) for event in calendar_events],
            reminders=[ReminderRead.model_validate(reminder) for reminder in reminders]
        )

    def build_workspace_snapshot(self, workspace: Workspace) -> WorkspaceSnapshot:
        """Build a complete workspace snapshot with all nested data"""
        projects = self.get_projects_by_workspace(workspace.id)
        project_snapshots = [self.build_project_snapshot(project) for project in projects]
        
        # Get tasks directly under workspace (not in projects)
        workspace_tasks = self.session.exec(
            select(Task).where(
                Task.workspace_id == workspace.id,
                Task.project_id.is_(None),
                Task.parent_task_id.is_(None),
                Task.archived_at.is_(None)
            )
        ).all()
        task_snapshots = [self.build_task_snapshot(task) for task in workspace_tasks]
        
        notes = self.session.exec(
            select(Note).where(
                Note.attached_to_type == "workspace",
                Note.attached_to_id == workspace.id,
                Note.archived_at.is_(None)
            )
        ).all()
        
        calendar_events = self.session.exec(
            select(CalendarEvent).where(
                CalendarEvent.linked_to_type == "workspace",
                CalendarEvent.linked_to_id == workspace.id,
                CalendarEvent.archived_at.is_(None)
            )
        ).all()
        
        reminders = self.session.exec(
            select(Reminder).where(
                Reminder.linked_to_type == "workspace",
                Reminder.linked_to_id == workspace.id,
                Reminder.archived_at.is_(None)
            )
        ).all()
        
        return WorkspaceSnapshot(
            id=workspace.id,
            title=workspace.title,
            description=workspace.description,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
            projects=project_snapshots,
            tasks=task_snapshots,
            notes=[NoteRead.model_validate(note) for note in notes],
            calendar_events=[CalendarEventRead.model_validate(event) for event in calendar_events],
            reminders=[ReminderRead.model_validate(reminder) for reminder in reminders]
        )

    def get_workspace_snapshot(self, workspace_id: int) -> Optional[WorkspaceSnapshot]:
        """Get the complete hierarchical snapshot of a workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return None
        return self.build_workspace_snapshot(workspace)

    def get_all_workspaces_snapshot(self) -> List[WorkspaceSnapshot]:
        """Get snapshots of all workspaces"""
        workspaces = self.get_workspaces()
        return [self.build_workspace_snapshot(workspace) for workspace in workspaces] 