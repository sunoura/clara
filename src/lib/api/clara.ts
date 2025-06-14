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

export interface WorkspaceSnapshot {
	id: number;
	title: string;
	description?: string;
	created_at: string;
	updated_at: string;
	projects: ProjectSnapshot[];
	tasks: TaskSnapshot[];
	notes: any[];
	calendar_events: any[];
	reminders: any[];
}

export interface ProjectSnapshot {
	id: number;
	title: string;
	description?: string;
	created_at: string;
	updated_at: string;
	tasks: TaskSnapshot[];
	notes: any[];
	calendar_events: any[];
	reminders: any[];
}

export interface TaskSnapshot {
	id: number;
	title: string;
	status: string;
	due_date?: string;
	created_at: string;
	updated_at: string;
	subtasks: TaskSnapshot[];
	notes: any[];
	calendar_events: any[];
	reminders: any[];
}



class ClaraAPI {
	private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
		const url = `${API_BASE}${endpoint}`;
		const response = await fetch(url, {
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
	async getAllWorkspacesSnapshot(): Promise<WorkspaceSnapshot[]> {
		return this.request<WorkspaceSnapshot[]>('/snapshots/');
	}

	async getWorkspaceSnapshot(workspaceId: number): Promise<WorkspaceSnapshot> {
		return this.request<WorkspaceSnapshot>(`/workspaces/${workspaceId}/snapshot`);
	}

	// Task operations
	async createTask(task: TaskCreate): Promise<any> {
		return this.request('/tasks/', {
			method: 'POST',
			body: JSON.stringify(task),
		});
	}

	async updateTask(taskId: number, task: TaskUpdate): Promise<any> {
		return this.request(`/tasks/${taskId}`, {
			method: 'PUT',
			body: JSON.stringify(task),
		});
	}

	async deleteTask(taskId: number): Promise<any> {
		return this.request(`/tasks/${taskId}`, {
			method: 'DELETE',
		});
	}

	// Health check
	async checkConnection(): Promise<boolean> {
		try {
			await this.getAllWorkspacesSnapshot();
			return true;
		} catch (error) {
			console.warn('Clara API connection failed:', error);
			return false;
		}
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
	async getTask(id: number): Promise<Task> {
		return this.request(`/tasks/${id}`);
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
}

export const claraAPI = new ClaraAPI(); 