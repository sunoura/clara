import { claraAPI } from '$lib/api/clara';
import type { Workspace, WorkspaceCreate, ProjectCreate, TaskCreate, TaskUpdate } from '$lib/types/clara';

interface ClaraState {
    workspaces: Workspace[];
    selectedWorkspace: Workspace | null;
    isLoading: boolean;
    error: string | null;
    showCreateForm: 'workspace' | 'project' | 'task' | null;
}

const claraState: ClaraState = $state({
    workspaces: [],
    selectedWorkspace: null,
    isLoading: false,
    error: null,
    showCreateForm: null
});

// Mock data for development
const mockWorkspaces: Workspace[] = [
    {
        id: 1,
        title: "Personal",
        description: "Personal tasks and projects",
        created_at: "2025-06-14T10:00:00Z",
        updated_at: "2025-06-14T10:00:00Z",
        projects: [
            {
                id: 1,
                title: "Home Improvements",
                description: "Tasks related to home maintenance and improvements",
                created_at: "2025-06-14T10:00:00Z",
                updated_at: "2025-06-14T10:00:00Z",
                tasks: [
                    {
                        id: 1,
                        title: "Fix leaky faucet in kitchen",
                        status: "todo" as const,
                        due_date: "2025-06-21T10:00:00Z",
                        created_at: "2025-06-14T10:00:00Z",
                        updated_at: "2025-06-14T10:00:00Z",
                        subtasks: [],
                        notes: [],
                        calendar_events: [],
                        reminders: []
                    },
                    {
                        id: 2,
                        title: "Paint living room walls",
                        status: "in-progress" as const,
                        created_at: "2025-06-14T10:00:00Z",
                        updated_at: "2025-06-14T10:00:00Z",
                        subtasks: [
                            {
                                id: 3,
                                title: "Buy paint and supplies",
                                status: "done" as const,
                                created_at: "2025-06-14T10:00:00Z",
                                updated_at: "2025-06-14T10:00:00Z",
                                subtasks: [],
                                notes: [],
                                calendar_events: [],
                                reminders: []
                            },
                            {
                                id: 4,
                                title: "Prep walls and prime",
                                status: "in-progress" as const,
                                created_at: "2025-06-14T10:00:00Z",
                                updated_at: "2025-06-14T10:00:00Z",
                                subtasks: [],
                                notes: [],
                                calendar_events: [],
                                reminders: []
                            }
                        ],
                        notes: [],
                        calendar_events: [],
                        reminders: []
                    }
                ],
                notes: [],
                calendar_events: [],
                reminders: []
            },
            {
                id: 2,
                title: "Health & Fitness",
                description: "Personal health and fitness goals",
                created_at: "2025-06-14T10:00:00Z",
                updated_at: "2025-06-14T10:00:00Z",
                tasks: [
                    {
                        id: 5,
                        title: "Schedule annual physical exam",
                        status: "todo" as const,
                        due_date: "2025-06-28T10:00:00Z",
                        created_at: "2025-06-14T10:00:00Z",
                        updated_at: "2025-06-14T10:00:00Z",
                        subtasks: [],
                        notes: [],
                        calendar_events: [],
                        reminders: []
                    }
                ],
                notes: [],
                calendar_events: [],
                reminders: []
            }
        ],
        tasks: [
            {
                id: 6,
                title: "Buy groceries",
                status: "todo" as const,
                due_date: "2025-06-16T10:00:00Z",
                created_at: "2025-06-14T10:00:00Z",
                updated_at: "2025-06-14T10:00:00Z",
                subtasks: [],
                notes: [],
                calendar_events: [],
                reminders: []
            }
        ],
        notes: [],
        calendar_events: [],
        reminders: []
    },
    {
        id: 2,
        title: "Work",
        description: "Professional tasks and projects",
        created_at: "2025-06-14T10:00:00Z",
        updated_at: "2025-06-14T10:00:00Z",
        projects: [
            {
                id: 3,
                title: "Website Redesign",
                description: "Complete redesign of company website",
                created_at: "2025-06-14T10:00:00Z",
                updated_at: "2025-06-14T10:00:00Z",
                tasks: [
                    {
                        id: 7,
                        title: "Research competitor websites",
                        status: "done" as const,
                        created_at: "2025-06-14T10:00:00Z",
                        updated_at: "2025-06-14T10:00:00Z",
                        subtasks: [],
                        notes: [],
                        calendar_events: [],
                        reminders: []
                    },
                    {
                        id: 8,
                        title: "Create wireframes and mockups",
                        status: "in-progress" as const,
                        created_at: "2025-06-14T10:00:00Z",
                        updated_at: "2025-06-14T10:00:00Z",
                        subtasks: [
                            {
                                id: 9,
                                title: "Design homepage layout",
                                status: "todo" as const,
                                created_at: "2025-06-14T10:00:00Z",
                                updated_at: "2025-06-14T10:00:00Z",
                                subtasks: [],
                                notes: [],
                                calendar_events: [],
                                reminders: []
                            }
                        ],
                        notes: [],
                        calendar_events: [],
                        reminders: []
                    }
                ],
                notes: [],
                calendar_events: [],
                reminders: []
            }
        ],
        tasks: [
            {
                id: 10,
                title: "Review quarterly budget",
                status: "todo" as const,
                due_date: "2025-06-19T10:00:00Z",
                created_at: "2025-06-14T10:00:00Z",
                updated_at: "2025-06-14T10:00:00Z",
                subtasks: [],
                notes: [],
                calendar_events: [],
                reminders: []
            }
        ],
        notes: [],
        calendar_events: [],
        reminders: []
    }
];

// Load all workspaces with complete snapshots
export async function loadWorkspaces() {
    try {
        claraState.isLoading = true;
        claraState.error = null;
        
        try {
            const workspaces = await claraAPI.getAllWorkspacesSnapshot();
            claraState.workspaces = workspaces;
        } catch (apiError) {
            console.warn('API not available, using mock data:', apiError);
            // Fall back to mock data
            claraState.workspaces = mockWorkspaces;
        }
        
        // Select the first workspace if none selected
        if (claraState.workspaces.length > 0 && !claraState.selectedWorkspace) {
            claraState.selectedWorkspace = claraState.workspaces[0];
        }
    } catch (error) {
        claraState.error = error instanceof Error ? error.message : 'Failed to load workspaces';
        // Still show mock data even on error
        claraState.workspaces = mockWorkspaces;
        if (claraState.workspaces.length > 0 && !claraState.selectedWorkspace) {
            claraState.selectedWorkspace = claraState.workspaces[0];
        }
    } finally {
        claraState.isLoading = false;
    }
}

// Refresh the selected workspace
export async function refreshWorkspace() {
    if (!claraState.selectedWorkspace) return;
    
    try {
        claraState.isLoading = true;
        claraState.error = null;
        
        try {
            const updated = await claraAPI.getWorkspaceSnapshot(claraState.selectedWorkspace.id);
            
            // Update in the workspaces array
            const index = claraState.workspaces.findIndex(w => w.id === updated.id);
            if (index !== -1) {
                claraState.workspaces[index] = updated;
            }
            
            claraState.selectedWorkspace = updated;
        } catch (apiError) {
            console.warn('API not available, keeping current data:', apiError);
        }
    } catch (error) {
        claraState.error = error instanceof Error ? error.message : 'Failed to refresh workspace';
    } finally {
        claraState.isLoading = false;
    }
}

// Create workspace
export async function createWorkspace(data: WorkspaceCreate) {
    try {
        claraState.isLoading = true;
        claraState.error = null;
        
        try {
            const newWorkspace = await claraAPI.createWorkspace(data);
            
            // Reload workspaces to get full snapshot
            await loadWorkspaces();
            
            claraState.showCreateForm = null;
            return newWorkspace;
        } catch (apiError) {
            console.warn('API not available, creating mock workspace:', apiError);
            
            // Create mock workspace
            const mockWorkspace: Workspace = {
                id: Math.max(...claraState.workspaces.map(w => w.id)) + 1,
                title: data.title,
                description: data.description,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                projects: [],
                tasks: [],
                notes: [],
                calendar_events: [],
                reminders: []
            };
            
            claraState.workspaces.push(mockWorkspace);
            claraState.selectedWorkspace = mockWorkspace;
            claraState.showCreateForm = null;
            return mockWorkspace;
        }
    } catch (error) {
        claraState.error = error instanceof Error ? error.message : 'Failed to create workspace';
        throw error;
    } finally {
        claraState.isLoading = false;
    }
}

// Create project
export async function createProject(data: ProjectCreate) {
    try {
        claraState.isLoading = true;
        claraState.error = null;
        
        try {
            const newProject = await claraAPI.createProject(data);
            
            // Refresh workspace to get updated data
            await refreshWorkspace();
            
            claraState.showCreateForm = null;
            return newProject;
        } catch (apiError) {
            console.warn('API not available, creating mock project:', apiError);
            
            if (claraState.selectedWorkspace) {
                // Create mock project
                const mockProject = {
                    id: Math.max(...claraState.selectedWorkspace.projects.map(p => p.id), 0) + 1,
                    title: data.title,
                    description: data.description,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    tasks: [],
                    notes: [],
                    calendar_events: [],
                    reminders: []
                };
                
                claraState.selectedWorkspace.projects.push(mockProject);
                claraState.showCreateForm = null;
                return mockProject;
            }
        }
    } catch (error) {
        claraState.error = error instanceof Error ? error.message : 'Failed to create project';
        throw error;
    } finally {
        claraState.isLoading = false;
    }
}

// Create task
export async function createTask(data: TaskCreate) {
    try {
        claraState.isLoading = true;
        claraState.error = null;
        
        try {
            const newTask = await claraAPI.createTask(data);
            
            // Refresh workspace to get updated data
            await refreshWorkspace();
            
            claraState.showCreateForm = null;
            return newTask;
        } catch (apiError) {
            console.warn('API not available, creating mock task:', apiError);
            
            if (claraState.selectedWorkspace) {
                // Create mock task
                const mockTask = {
                    id: Math.max(...claraState.selectedWorkspace.tasks.map(t => t.id), 0) + 1,
                    title: data.title,
                    status: data.status || "todo" as const,
                    due_date: data.due_date,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                    subtasks: [],
                    notes: [],
                    calendar_events: [],
                    reminders: []
                };
                
                claraState.selectedWorkspace.tasks.push(mockTask);
                claraState.showCreateForm = null;
                return mockTask;
            }
        }
    } catch (error) {
        claraState.error = error instanceof Error ? error.message : 'Failed to create task';
        throw error;
    } finally {
        claraState.isLoading = false;
    }
}

// Update task
export async function updateTask(taskId: number, data: TaskUpdate) {
    try {
        claraState.isLoading = true;
        claraState.error = null;
        
        try {
            const updatedTask = await claraAPI.updateTask(taskId, data);
            
            // Refresh workspace to get updated data
            await refreshWorkspace();
            
            return updatedTask;
        } catch (apiError) {
            console.warn('API not available, updating mock task:', apiError);
            
            // Find and update the task in mock data
            if (claraState.selectedWorkspace) {
                function updateTaskInList(tasks: any[]): boolean {
                    for (const task of tasks) {
                        if (task.id === taskId) {
                            Object.assign(task, data);
                            task.updated_at = new Date().toISOString();
                            return true;
                        }
                        if (task.subtasks && updateTaskInList(task.subtasks)) {
                            return true;
                        }
                    }
                    return false;
                }
                
                // Update in workspace tasks
                updateTaskInList(claraState.selectedWorkspace.tasks);
                
                // Update in project tasks
                for (const project of claraState.selectedWorkspace.projects) {
                    updateTaskInList(project.tasks);
                }
            }
        }
    } catch (error) {
        claraState.error = error instanceof Error ? error.message : 'Failed to update task';
        throw error;
    } finally {
        claraState.isLoading = false;
    }
}

// Complete task
export async function completeTask(taskId: number) {
    try {
        claraState.isLoading = true;
        claraState.error = null;
        
        try {
            const completedTask = await claraAPI.completeTask(taskId);
            
            // Refresh workspace to get updated data
            await refreshWorkspace();
            
            return completedTask;
        } catch (apiError) {
            console.warn('API not available, completing mock task:', apiError);
            
            // Complete the task in mock data
            await updateTask(taskId, { status: 'done' });
        }
    } catch (error) {
        claraState.error = error instanceof Error ? error.message : 'Failed to complete task';
        throw error;
    } finally {
        claraState.isLoading = false;
    }
}

// Select workspace
export function selectWorkspace(workspace: Workspace) {
    claraState.selectedWorkspace = workspace;
}

// Show create form
export function showCreateForm(type: 'workspace' | 'project' | 'task') {
    claraState.showCreateForm = type;
}

// Hide create form
export function hideCreateForm() {
    claraState.showCreateForm = null;
}

export { claraState }; 