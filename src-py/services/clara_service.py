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
        # Check for circular dependency if parent_task_id is specified
        if task_data.parent_task_id is not None:
            # For new tasks, we just need to ensure the parent exists
            parent_task = self.session.get(Task, task_data.parent_task_id)
            if not parent_task:
                raise ValueError(f"Parent task {task_data.parent_task_id} does not exist")
        
        # Calculate the next order_index for this parent/workspace
        if task_data.parent_task_id is not None:
            # Get the highest order_index for this parent
            max_order = self.session.exec(
                select(Task.order_index).where(
                    Task.parent_task_id == task_data.parent_task_id,
                    Task.archived_at.is_(None)
                ).order_by(Task.order_index.desc()).limit(1)
            ).first()
        else:
            # Get the highest order_index for root tasks in this workspace
            max_order = self.session.exec(
                select(Task.order_index).where(
                    Task.workspace_id == task_data.workspace_id,
                    Task.parent_task_id.is_(None),
                    Task.archived_at.is_(None)
                ).order_by(Task.order_index.desc()).limit(1)
            ).first()
        
        next_order = (max_order or 0) + 1
        
        task_dict = task_data.model_dump()
        task_dict['order_index'] = next_order
        task = Task(**task_dict)
        
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
            ).order_by(Task.order_index)
        ).all()

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        return self.session.exec(
            select(Task).where(
                Task.project_id == project_id,
                Task.archived_at.is_(None)
            ).order_by(Task.order_index)
        ).all()

    def get_subtasks(self, parent_task_id: int) -> List[Task]:
        return self.session.exec(
            select(Task).where(
                Task.parent_task_id == parent_task_id,
                Task.archived_at.is_(None)
            ).order_by(Task.order_index)
        ).all()

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        
        # Check for circular dependency if parent_task_id is being updated
        if 'parent_task_id' in update_data and update_data['parent_task_id'] is not None:
            new_parent_id = update_data['parent_task_id']
            
            # Prevent self-assignment
            if new_parent_id == task_id:
                raise ValueError(f"Task {task_id} cannot be its own parent")
            
            # Prevent circular dependency
            if self._would_create_circular_dependency(task_id, new_parent_id):
                raise ValueError(f"Setting parent_task_id to {new_parent_id} would create a circular dependency")
        
        for key, value in update_data.items():
            setattr(task, key, value)
        
        task.updated_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(task)
        self.log_activity("update", "task", task.id, update_data)
        return task

    def reorder_tasks(self, task_ids: List[int], parent_task_id: Optional[int] = None, workspace_id: Optional[int] = None) -> bool:
        """
        Reorder tasks by setting their order_index based on the provided list order.
        Either parent_task_id or workspace_id should be provided to identify the scope.
        """
        try:
            for index, task_id in enumerate(task_ids):
                task = self.session.get(Task, task_id)
                if task:
                    task.order_index = index
                    task.updated_at = datetime.now(UTC)
            
            self.session.commit()
            self.log_activity("reorder", "task", 0, {
                "task_ids": task_ids,
                "parent_task_id": parent_task_id,
                "workspace_id": workspace_id
            })
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error reordering tasks: {e}")
            return False

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

    def _would_create_circular_dependency(self, task_id: int, potential_parent_id: int) -> bool:
        """
        Check if setting potential_parent_id as parent of task_id would create a circular dependency.
        This happens if potential_parent_id is actually a descendant of task_id.
        """
        return self._is_task_descendant(task_id, potential_parent_id)
    
    def _is_task_descendant(self, ancestor_task_id: int, potential_descendant_id: int) -> bool:
        """
        Check if potential_descendant_id is a descendant of ancestor_task_id.
        Uses iterative approach to avoid stack overflow on deep hierarchies.
        """
        # Get all direct children of the ancestor
        children_to_check = [ancestor_task_id]
        visited = set()
        
        while children_to_check:
            current_id = children_to_check.pop()
            
            # Avoid infinite loops (shouldn't happen with proper data, but safety first)
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Get direct children of current task
            children = self.session.exec(
                select(Task).where(
                    Task.parent_task_id == current_id,
                    Task.archived_at.is_(None)
                )
            ).all()
            
            for child in children:
                if child.id == potential_descendant_id:
                    return True
                children_to_check.append(child.id)
        
        return False

    # Hierarchical snapshot methods
    def build_task_snapshot(self, task: Task, visited_task_ids: set = None) -> TaskSnapshot:
        """Build a complete task snapshot with all nested data"""
        if visited_task_ids is None:
            visited_task_ids = set()
        
        # Prevent infinite recursion from circular dependencies
        if task.id in visited_task_ids:
            # Log the circular dependency and return a minimal snapshot
            print(f"Warning: Circular dependency detected for task {task.id}")
            return TaskSnapshot(
                id=task.id,
                title=f"{task.title} [CIRCULAR DEPENDENCY DETECTED]",
                status=task.status,
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at,
                subtasks=[],  # Don't include subtasks to break the cycle
                notes=[],
                calendar_events=[],
                reminders=[]
            )
        
        visited_task_ids.add(task.id)
        subtasks = [self.build_task_snapshot(subtask, visited_task_ids.copy()) for subtask in self.get_subtasks(task.id)]
        
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
            ).order_by(Task.order_index)
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