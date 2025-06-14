# Database Schemas (SQLModel tables)
from ._schemas import (
    MemoryCollection,
    MemoryDocument, 
    InteractionSession,
    InteractionPayload,
    InteractionFrom,
    # Clara models
    TaskStatus,
    Workspace,
    Project,
    Task,
    Note,
    CalendarEvent,
    Reminder,
    Notification,
    ActivityLog,
    Tag,
    TaggedItem,
)

# Pydantic Models
from .memory_collection_models import (
    MemoryCollectionBase,
    MemoryCollectionCreate,
    MemoryCollectionRead,
    MemoryCollectionUpdate,
    MemoryCollectionWithDocuments,
)

from .memory_document_models import (
    MemoryDocumentBase,
    MemoryDocumentCreate,
    MemoryDocumentRead,
    MemoryDocumentUpdate,
    MemoryDocumentWithCollection,
)

from .interaction_session_models import (
    InteractionSessionBase,
    InteractionSessionCreate,
    InteractionSessionRead,
    InteractionSessionUpdate,
    InteractionSessionWithPayloads,
)

from .interaction_payload_models import (
    InteractionPayloadBase,
    InteractionPayloadCreate,
    InteractionPayloadRead,
    InteractionPayloadUpdate,
    InteractionPayloadWithSession,
)

# Clara Pydantic Models
from .clara_models import (
    WorkspaceBase,
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
    ProjectBase,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskBase,
    TaskCreate,
    TaskRead,
    TaskUpdate,
    NoteBase,
    NoteCreate,
    NoteRead,
    NoteUpdate,
    CalendarEventBase,
    CalendarEventCreate,
    CalendarEventRead,
    CalendarEventUpdate,
    ReminderBase,
    ReminderCreate,
    ReminderRead,
    ReminderUpdate,
    TagBase,
    TagCreate,
    TagRead,
    TagUpdate,
    WorkspaceSnapshot,
    ProjectSnapshot,
    TaskSnapshot,
)

__all__ = [
    # Schemas
    "MemoryCollection",
    "MemoryDocument",
    "InteractionSession", 
    "InteractionPayload",
    "InteractionFrom",
    # Clara Schemas
    "TaskStatus",
    "Workspace",
    "Project",
    "Task",
    "Note",
    "CalendarEvent",
    "Reminder",
    "Notification",
    "ActivityLog",
    "Tag",
    "TaggedItem",
    
    # Memory Collection Models
    "MemoryCollectionBase",
    "MemoryCollectionCreate",
    "MemoryCollectionRead",
    "MemoryCollectionUpdate", 
    "MemoryCollectionWithDocuments",
    
    # Memory Document Models
    "MemoryDocumentBase",
    "MemoryDocumentCreate",
    "MemoryDocumentRead",
    "MemoryDocumentUpdate",
    "MemoryDocumentWithCollection",
    
    # Interaction Session Models
    "InteractionSessionBase",
    "InteractionSessionCreate", 
    "InteractionSessionRead",
    "InteractionSessionUpdate",
    "InteractionSessionWithPayloads",
    
    # Interaction Payload Models
    "InteractionPayloadBase",
    "InteractionPayloadCreate",
    "InteractionPayloadRead", 
    "InteractionPayloadUpdate",
    "InteractionPayloadWithSession",
    
    # Clara Models
    "WorkspaceBase",
    "WorkspaceCreate",
    "WorkspaceRead",
    "WorkspaceUpdate",
    "ProjectBase",
    "ProjectCreate",
    "ProjectRead",
    "ProjectUpdate",
    "TaskBase",
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
    "NoteBase",
    "NoteCreate",
    "NoteRead",
    "NoteUpdate",
    "CalendarEventBase",
    "CalendarEventCreate",
    "CalendarEventRead",
    "CalendarEventUpdate",
    "ReminderBase",
    "ReminderCreate",
    "ReminderRead",
    "ReminderUpdate",
    "TagBase",
    "TagCreate",
    "TagRead",
    "TagUpdate",
    "WorkspaceSnapshot",
    "ProjectSnapshot",
    "TaskSnapshot",
]
