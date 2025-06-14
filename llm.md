# Clara: Reference Document

## Overview

Clara is a polymorphic task management system designed for responsiveness, clarity, and LLM-driven workflows. The core interface is structured around a nested list view, with the primary data represented as a hierarchical JSON snapshot of workspaces, projects, and tasks. The backend acts as an integrity checker that validates and syncs state.

## Core Principles

* **Tasks are temporary action items**: They appear, get acted upon, and disappear.
* **Projects hold context and scope**: They accumulate related tasks over time.
* **Workspaces contain everything**: The top-level containers for organizing work.

Every item (task, project, workspace) can have:

* Notes

* Calendar events

* Reminders

* The frontend loads a nested snapshot (raw JSON) for fast performance.

* The backend checks data validity, handles syncing, and fetches additional detail.

* The system is designed to tolerate occasional sync conflicts through UI feedback and recoverability.

## Core Data Structure

A single nested tree:

```plaintext
Workspace
 ├── Project
 │    ├── Task
 │    └── Task
 ├── Task
 └── Project
      └── Task
```

This tree is stored and synced as a JSON structure and displayed in a drag/drop capable UI.

---

## Features

### Task Management

* Nested structure: Workspace → Projects → Tasks (or Tasks directly under Workspace)
* Tasks can be added to Inbox, a Project, another Task, or directly into a Workspace
* Reorder any item via drag and drop
* Flat text-only list views for printing or focus
* Fast UI load via JSON snapshot
* Backend integrity checker validates and persists structure
* UI indicates sync status, failed saves, or conflicts
* Basic search and filter functionality across items
* Items can include notes, calendar events, and reminders

### Calendar View

* Tasks and projects can have one or more linked calendar events
* Events are visualized across standard calendar views (day/week/month)

### Today View

* Tasks, projects, and events can be scheduled to appear in a "Today" focus view
* Helps prioritize current actions across workspaces

### Logbook

* Chronological activity log of all actions (create, edit, reorder, complete, delete)
* Foundation for undo/redo, journaling, or timeline-style playback

### Notifications View

* Triggered reminders, sync alerts, or calendar events
* Managed view of unseen or recent notifications

---

## Agent Notes

* Treat frontend snapshot as the source of current UI state
* Use backend only for validation, persistence, and fetching additional details
* Structure operations as modifications to a nested tree of workspace > project > task
* Sync-related failures should suggest retry logic or surface fallback states
* Avoid operating directly on raw DB models; always work via tree context

---

## Tables & Fields

### 1. workspaces

* `id`: Unique identifier
* `title`: Name of the workspace
* `description`: Optional description
* `created_at`: Timestamp
* `updated_at`: Timestamp
* `archived_at`: Optional timestamp when the workspace was archived

### 2. projects

* `id`: Unique identifier
* `workspace_id`: Reference to the parent workspace
* `title`: Name of the project
* `description`: Optional details
* `created_at`: Timestamp
* `updated_at`: Timestamp
* `archived_at`: Optional timestamp when the project was archived

### 3. tasks

* `id`: Unique identifier
* `title`: Name of the task
* `status`: e.g. "todo", "in-progress", "done", "archived"
* `workspace_id`: Reference to parent workspace
* `project_id`: Reference to parent project (nullable)
* `parent_task_id`: Reference to parent task (nullable, for subtasks)
* `due_date`: Optional timestamp
* `created_at`: Timestamp
* `updated_at`: Timestamp
* `archived_at`: Optional timestamp when the task was archived

### 4. notes

* `id`: Unique identifier
* `content`: Text content
* `attached_to_type`: "task", "project", or "workspace"
* `attached_to_id`: ID of the item it’s attached to
* `created_at`: Timestamp
* `archived_at`: Optional timestamp when the note was archived

### 5. calendar\_events

* `id`: Unique identifier
* `title`: Short label
* `start_time`: Start timestamp
* `end_time`: End timestamp
* `linked_to_type`: "task", "project", or "workspace"
* `linked_to_id`: ID of the item
* `created_at`: Timestamp
* `archived_at`: Optional timestamp when the event was archived

### 6. reminders

* `id`: Unique identifier
* `trigger_time`: When the reminder should fire
* `message`: Optional text message or label
* `linked_to_type`: "task", "project", or "workspace"
* `linked_to_id`: ID of the item
* `created_at`: Timestamp
* `archived_at`: Optional timestamp when the reminder was archived

### 7. notifications

* `id`: Unique identifier
* `type`: "reminder", "event", "sync\_alert", etc.
* `title`: Title of the notification
* `content`: Body message (optional)
* `target_id`: Optional ID of related task/project/etc.
* `seen`: Boolean flag
* `created_at`: Timestamp
* `triggered_at`: Timestamp (when it was displayed)
* `archived_at`: Optional timestamp when the notification was archived

### 8. activity\_log

* `id`: Unique identifier
* `action_type`: "create", "update", "delete", "reorder", etc.
* `entity_type`: "task", "project", etc.
* `entity_id`: ID of the modified item
* `data`: JSON blob of change details (diff or snapshot)
* `created_at`: Timestamp
* `archived_at`: Optional timestamp when the log entry was archived
