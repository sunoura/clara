from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ._schemas import TaskStatus


# Base Models
class WorkspaceBase(BaseModel):
    title: str
    description: Optional[str] = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceRead(WorkspaceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None


class WorkspaceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    workspace_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class TaskBase(BaseModel):
    title: str
    status: TaskStatus = TaskStatus.TODO
    workspace_id: int
    project_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    project_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    due_date: Optional[datetime] = None


class NoteBase(BaseModel):
    content: str
    attached_to_type: str
    attached_to_id: int


class NoteCreate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: int
    created_at: datetime
    archived_at: Optional[datetime] = None


class NoteUpdate(BaseModel):
    content: Optional[str] = None


class CalendarEventBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    linked_to_type: str
    linked_to_id: int


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventRead(CalendarEventBase):
    id: int
    created_at: datetime
    archived_at: Optional[datetime] = None


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ReminderBase(BaseModel):
    trigger_time: datetime
    message: Optional[str] = None
    linked_to_type: str
    linked_to_id: int


class ReminderCreate(ReminderBase):
    pass


class ReminderRead(ReminderBase):
    id: int
    created_at: datetime
    archived_at: Optional[datetime] = None


class ReminderUpdate(BaseModel):
    trigger_time: Optional[datetime] = None
    message: Optional[str] = None


class TagBase(BaseModel):
    label: str
    color: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int
    created_at: datetime


class TagUpdate(BaseModel):
    label: Optional[str] = None
    color: Optional[str] = None


class TaskReorderRequest(BaseModel):
    task_ids: List[int]
    parent_task_id: Optional[int] = None
    workspace_id: Optional[int] = None


# Nested/Hierarchical Models for JSON Snapshot
class TaskSnapshot(BaseModel):
    id: int
    title: str
    status: TaskStatus
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    subtasks: List["TaskSnapshot"] = []
    notes: List[NoteRead] = []
    calendar_events: List[CalendarEventRead] = []
    reminders: List[ReminderRead] = []


class ProjectSnapshot(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskSnapshot] = []
    notes: List[NoteRead] = []
    calendar_events: List[CalendarEventRead] = []
    reminders: List[ReminderRead] = []


class WorkspaceSnapshot(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    projects: List[ProjectSnapshot] = []
    tasks: List[TaskSnapshot] = []  # Tasks directly under workspace
    notes: List[NoteRead] = []
    calendar_events: List[CalendarEventRead] = []
    reminders: List[ReminderRead] = []


# Update forward references
TaskSnapshot.model_rebuild() 