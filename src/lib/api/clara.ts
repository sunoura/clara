import type { 
    Workspace, 
    Project, 
    Task, 
    WorkspaceCreate, 
    ProjectCreate, 
    TaskCreate, 
    TaskUpdate 
} from '$lib/types/clara';

const API_BASE = 'http://localhost:8000/api/clara';

class ClaraAPI {
    private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return response.json();
    }

    // Workspace operations
    async createWorkspace(data: WorkspaceCreate): Promise<Workspace> {
        return this.request('/workspaces/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getWorkspaces(): Promise<Workspace[]> {
        return this.request('/workspaces/');
    }

    async getWorkspace(id: number): Promise<Workspace> {
        return this.request(`/workspaces/${id}`);
    }

    async updateWorkspace(id: number, data: Partial<WorkspaceCreate>): Promise<Workspace> {
        return this.request(`/workspaces/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async archiveWorkspace(id: number): Promise<Workspace> {
        return this.request(`/workspaces/${id}`, {
            method: 'DELETE',
        });
    }

    // Project operations
    async createProject(data: ProjectCreate): Promise<Project> {
        return this.request('/projects/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getProject(id: number): Promise<Project> {
        return this.request(`/projects/${id}`);
    }

    async updateProject(id: number, data: Partial<ProjectCreate>): Promise<Project> {
        return this.request(`/projects/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async archiveProject(id: number): Promise<Project> {
        return this.request(`/projects/${id}`, {
            method: 'DELETE',
        });
    }

    // Task operations
    async createTask(data: TaskCreate): Promise<Task> {
        return this.request('/tasks/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getTask(id: number): Promise<Task> {
        return this.request(`/tasks/${id}`);
    }

    async updateTask(id: number, data: TaskUpdate): Promise<Task> {
        return this.request(`/tasks/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    async completeTask(id: number): Promise<Task> {
        return this.request(`/tasks/${id}/complete`, {
            method: 'POST',
        });
    }

    async archiveTask(id: number): Promise<Task> {
        return this.request(`/tasks/${id}`, {
            method: 'DELETE',
        });
    }

    // Snapshot operations - Core feature for fast JSON loading
    async getWorkspaceSnapshot(id: number): Promise<Workspace> {
        return this.request(`/workspaces/${id}/snapshot`);
    }

    async getAllWorkspacesSnapshot(): Promise<Workspace[]> {
        return this.request('/snapshots/');
    }
}

export const claraAPI = new ClaraAPI(); 