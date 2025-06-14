export type TaskStatus = "todo" | "in-progress" | "done" | "archived";

export interface BaseItem {
    id: number;
    created_at: string;
    updated_at: string;
}

export interface Note extends BaseItem {
    content: string;
    attached_to_type: string;
    attached_to_id: number;
    archived_at?: string;
}

export interface CalendarEvent extends BaseItem {
    title: string;
    start_time: string;
    end_time: string;
    linked_to_type: string;
    linked_to_id: number;
    archived_at?: string;
}

export interface Reminder extends BaseItem {
    trigger_time: string;
    message?: string;
    linked_to_type: string;
    linked_to_id: number;
    archived_at?: string;
}

export interface Task extends BaseItem {
    title: string;
    status: TaskStatus;
    due_date?: string;
    subtasks: Task[];
    notes: Note[];
    calendar_events: CalendarEvent[];
    reminders: Reminder[];
}

export interface Project extends BaseItem {
    title: string;
    description?: string;
    tasks: Task[];
    notes: Note[];
    calendar_events: CalendarEvent[];
    reminders: Reminder[];
}

export interface Workspace extends BaseItem {
    title: string;
    description?: string;
    projects: Project[];
    tasks: Task[]; // Tasks directly under workspace
    notes: Note[];
    calendar_events: CalendarEvent[];
    reminders: Reminder[];
}

// Form types
export interface WorkspaceCreate {
    title: string;
    description?: string;
}

export interface ProjectCreate {
    title: string;
    description?: string;
    workspace_id: number;
}

export interface TaskCreate {
    title: string;
    status?: TaskStatus;
    workspace_id: number;
    project_id?: number;
    parent_task_id?: number;
    due_date?: string;
}

export interface TaskUpdate {
    title?: string;
    status?: TaskStatus;
    project_id?: number;
    parent_task_id?: number;
    due_date?: string;
}

// Drag and drop types
export interface DragItem {
    type: 'task' | 'project';
    id: number;
    workspaceId: number;
    projectId?: number;
    parentTaskId?: number;
}

export interface DropTarget {
    type: 'workspace' | 'project' | 'task';
    id: number;
    workspaceId: number;
} 