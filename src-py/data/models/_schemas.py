from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, UTC
from enum import Enum
import uuid


# Enums
class InteractionFrom(str, Enum):
    USER = "user"
    MODEL = "model"


# Database Tables
class MemoryCollection(SQLModel, table=True):
    __tablename__ = "memory_collections"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    documents: List["MemoryDocument"] = Relationship(back_populates="collection")


class MemoryDocument(SQLModel, table=True):
    __tablename__ = "memory_documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    chroma_id: str = Field(max_length=255, index=True)
    content: str
    collection_id: int = Field(foreign_key="memory_collections.id")
    metadatas: str = Field(default="{}")  # Stringified JSON
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    collection: Optional[MemoryCollection] = Relationship(back_populates="documents")


class InteractionSession(SQLModel, table=True):
    __tablename__ = "interaction_sessions"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(max_length=255)
    context_summary: Optional[str] = Field(default=None)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # Relationships
    payloads: List["InteractionPayload"] = Relationship(back_populates="session")


class InteractionPayload(SQLModel, table=True):
    __tablename__ = "interaction_payloads"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="interaction_sessions.id")
    content: str
    ok: bool = Field(default=True)
    err: Optional[str] = Field(default=None)
    from_: InteractionFrom = Field(alias="from")  # Using alias to avoid Python keyword conflict
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # Relationships
    session: Optional[InteractionSession] = Relationship(back_populates="payloads")


# Clara Task Management System Models

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"
    ARCHIVED = "archived"


class Workspace(SQLModel, table=True):
    __tablename__ = "workspaces"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    projects: List["Project"] = Relationship(back_populates="workspace")
    tasks: List["Task"] = Relationship(back_populates="workspace")
    notes: List["Note"] = Relationship(
        back_populates="workspace",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Note.attached_to_type=='workspace', Note.attached_to_id==Workspace.id)", 
            "foreign_keys": "[Note.attached_to_id]",
            "overlaps": "project,task"
        }
    )
    calendar_events: List["CalendarEvent"] = Relationship(
        back_populates="workspace",
        sa_relationship_kwargs={
            "primaryjoin": "and_(CalendarEvent.linked_to_type=='workspace', CalendarEvent.linked_to_id==Workspace.id)", 
            "foreign_keys": "[CalendarEvent.linked_to_id]",
            "overlaps": "project,task"
        }
    )
    reminders: List["Reminder"] = Relationship(
        back_populates="workspace",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Reminder.linked_to_type=='workspace', Reminder.linked_to_id==Workspace.id)", 
            "foreign_keys": "[Reminder.linked_to_id]",
            "overlaps": "project,task"
        }
    )


class Project(SQLModel, table=True):
    __tablename__ = "projects"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(foreign_key="workspaces.id")
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    workspace: Optional[Workspace] = Relationship(back_populates="projects")
    tasks: List["Task"] = Relationship(back_populates="project")
    notes: List["Note"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Note.attached_to_type=='project', Note.attached_to_id==Project.id)", 
            "foreign_keys": "[Note.attached_to_id]",
            "overlaps": "notes"
        }
    )
    calendar_events: List["CalendarEvent"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "primaryjoin": "and_(CalendarEvent.linked_to_type=='project', CalendarEvent.linked_to_id==Project.id)", 
            "foreign_keys": "[CalendarEvent.linked_to_id]",
            "overlaps": "calendar_events"
        }
    )
    reminders: List["Reminder"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Reminder.linked_to_type=='project', Reminder.linked_to_id==Project.id)", 
            "foreign_keys": "[Reminder.linked_to_id]",
            "overlaps": "reminders"
        }
    )


class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    status: TaskStatus = Field(default=TaskStatus.TODO)
    workspace_id: int = Field(foreign_key="workspaces.id")
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    order_index: int = Field(default=0)  # For ordering tasks within their parent/workspace
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    workspace: Optional[Workspace] = Relationship(back_populates="tasks")
    project: Optional[Project] = Relationship(back_populates="tasks")
    parent_task: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
    subtasks: List["Task"] = Relationship(back_populates="parent_task")
    notes: List["Note"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Note.attached_to_type=='task', Note.attached_to_id==Task.id)", 
            "foreign_keys": "[Note.attached_to_id]",
            "overlaps": "notes,notes"
        }
    )
    calendar_events: List["CalendarEvent"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={
            "primaryjoin": "and_(CalendarEvent.linked_to_type=='task', CalendarEvent.linked_to_id==Task.id)", 
            "foreign_keys": "[CalendarEvent.linked_to_id]",
            "overlaps": "calendar_events,calendar_events"
        }
    )
    reminders: List["Reminder"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Reminder.linked_to_type=='task', Reminder.linked_to_id==Task.id)", 
            "foreign_keys": "[Reminder.linked_to_id]",
            "overlaps": "reminders,reminders"
        }
    )


class Note(SQLModel, table=True):
    __tablename__ = "notes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    attached_to_type: str = Field(max_length=50)  # "task", "project", or "workspace"
    attached_to_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships (polymorphic)
    workspace: Optional[Workspace] = Relationship(
        back_populates="notes",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Note.attached_to_type=='workspace', Note.attached_to_id==Workspace.id)", 
            "foreign_keys": "[Note.attached_to_id]",
            "overlaps": "notes,notes"
        }
    )
    project: Optional[Project] = Relationship(
        back_populates="notes",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Note.attached_to_type=='project', Note.attached_to_id==Project.id)", 
            "foreign_keys": "[Note.attached_to_id]",
            "overlaps": "notes"
        }
    )
    task: Optional[Task] = Relationship(
        back_populates="notes",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Note.attached_to_type=='task', Note.attached_to_id==Task.id)", 
            "foreign_keys": "[Note.attached_to_id]",
            "overlaps": "notes"
        }
    )


class CalendarEvent(SQLModel, table=True):
    __tablename__ = "calendar_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    start_time: datetime
    end_time: datetime
    linked_to_type: str = Field(max_length=50)  # "task", "project", or "workspace"
    linked_to_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships (polymorphic)
    workspace: Optional[Workspace] = Relationship(
        back_populates="calendar_events",
        sa_relationship_kwargs={
            "primaryjoin": "and_(CalendarEvent.linked_to_type=='workspace', CalendarEvent.linked_to_id==Workspace.id)", 
            "foreign_keys": "[CalendarEvent.linked_to_id]",
            "overlaps": "calendar_events,calendar_events"
        }
    )
    project: Optional[Project] = Relationship(
        back_populates="calendar_events",
        sa_relationship_kwargs={
            "primaryjoin": "and_(CalendarEvent.linked_to_type=='project', CalendarEvent.linked_to_id==Project.id)", 
            "foreign_keys": "[CalendarEvent.linked_to_id]",
            "overlaps": "calendar_events"
        }
    )
    task: Optional[Task] = Relationship(
        back_populates="calendar_events",
        sa_relationship_kwargs={
            "primaryjoin": "and_(CalendarEvent.linked_to_type=='task', CalendarEvent.linked_to_id==Task.id)", 
            "foreign_keys": "[CalendarEvent.linked_to_id]",
            "overlaps": "calendar_events"
        }
    )


class Reminder(SQLModel, table=True):
    __tablename__ = "reminders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    trigger_time: datetime
    message: Optional[str] = Field(default=None)
    linked_to_type: str = Field(max_length=50)  # "task", "project", or "workspace"
    linked_to_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships (polymorphic)
    workspace: Optional[Workspace] = Relationship(
        back_populates="reminders",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Reminder.linked_to_type=='workspace', Reminder.linked_to_id==Workspace.id)", 
            "foreign_keys": "[Reminder.linked_to_id]",
            "overlaps": "reminders,reminders"
        }
    )
    project: Optional[Project] = Relationship(
        back_populates="reminders",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Reminder.linked_to_type=='project', Reminder.linked_to_id==Project.id)", 
            "foreign_keys": "[Reminder.linked_to_id]",
            "overlaps": "reminders"
        }
    )
    task: Optional[Task] = Relationship(
        back_populates="reminders",
        sa_relationship_kwargs={
            "primaryjoin": "and_(Reminder.linked_to_type=='task', Reminder.linked_to_id==Task.id)", 
            "foreign_keys": "[Reminder.linked_to_id]",
            "overlaps": "reminders"
        }
    )


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(max_length=50)  # "reminder", "event", "sync_alert", etc.
    title: str = Field(max_length=255)
    content: Optional[str] = Field(default=None)
    target_id: Optional[int] = Field(default=None)
    seen: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    triggered_at: Optional[datetime] = Field(default=None)
    archived_at: Optional[datetime] = Field(default=None)


class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    action_type: str = Field(max_length=50)  # "create", "update", "delete", "reorder", etc.
    entity_type: str = Field(max_length=50)  # "task", "project", etc.
    entity_id: int
    data: str = Field(default="{}")  # JSON blob of change details (diff or snapshot)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    label: str = Field(max_length=100, unique=True)
    color: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    # Relationships
    tagged_items: List["TaggedItem"] = Relationship(back_populates="tag")


class TaggedItem(SQLModel, table=True):
    __tablename__ = "tagged_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tag_id: int = Field(foreign_key="tags.id")
    target_type: str = Field(max_length=50)  # "task", "project", or "workspace"
    target_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    tag: Optional[Tag] = Relationship(back_populates="tagged_items")
