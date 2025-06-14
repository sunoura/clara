import { claraAPI, type TaskSnapshot, type WorkspaceSnapshot } from '$lib/api/clara';

interface Task {
	id: number;
	title: string;
	order: number;
	status: 'todo' | 'in-progress' | 'done' | 'archived';
	subtasks: Task[];
}

class TaskState {
	tasks = $state<Task[]>([]);
	private nextId = 1;
	private isOnline = $state(false);
	private workspaceId = 1; // Default workspace ID

	constructor() {
		this.initializeData();
	}

	private async initializeData() {
		// Try to sync with backend first
		try {
			await this.syncWithBackend();
			this.isOnline = true;
			console.log('✅ Synced with Clara backend');
		} catch (error) {
			console.warn('⚠️ Backend unavailable, using localStorage:', error);
			this.isOnline = false;
			this.loadTasksFromLocalStorage();
		}
	}

	async addTask(title: string, parentTask?: Task) {
		const task: Task = {
			id: this.nextId++,
			title,
			order: parentTask && parentTask.subtasks ? parentTask.subtasks.length : this.tasks.length,
			status: 'todo',
			subtasks: []
		};
		
		if (parentTask) {
			// Ensure subtasks array exists
			if (!parentTask.subtasks) {
				parentTask.subtasks = [];
			}
			parentTask.subtasks.push(task);
		} else {
			this.tasks.push(task);
		}
		
		// Save to localStorage first (immediate feedback)
		this.saveTasks();
		
		// Try to save to backend
		if (this.isOnline && this.workspaceId) {
			try {
				await claraAPI.createTask({
					title: task.title,
					workspace_id: this.workspaceId,
					parent_task_id: parentTask?.id || undefined,
					status: 'todo'
				});
				console.log(`Task "${title}" saved to backend`);
			} catch (error) {
				console.error('Failed to save task to backend:', error);
				// Task is still saved locally, so don't remove it
			}
		}
	}

	async reorderTasks(fromIndex: number, toIndex: number, parentTask?: Task) {
		console.log('🔄 REORDER TASKS:', {
			fromIndex,
			toIndex,
			parentTaskId: parentTask?.id,
			parentTaskTitle: parentTask?.title,
			targetArrayLength: parentTask ? parentTask.subtasks.length : this.tasks.length
		});

		const targetArray = parentTask ? parentTask.subtasks : this.tasks;
		const originalTasks = JSON.parse(JSON.stringify(this.tasks));
		
		const newTasks = [...targetArray];
		const [movedTask] = newTasks.splice(fromIndex, 1);
		newTasks.splice(toIndex, 0, movedTask);
		
		console.log('📋 Task moved in array:', {
			movedTaskId: movedTask?.id,
			movedTaskTitle: movedTask?.title,
			newArrayLength: newTasks.length
		});
		
		// Update order values
		newTasks.forEach((task, index) => {
			task.order = index;
		});
		
		if (parentTask) {
			parentTask.subtasks = newTasks;
		} else {
			this.tasks = newTasks;
		}
		
		// Save to localStorage first (immediate feedback)
		this.saveTasks();
		console.log('💾 Reorder saved to localStorage');

		// Try to update backend - for now, we'll just update the moved task's order
		// In a more sophisticated system, we might batch update all affected tasks
		if (this.isOnline && movedTask) {
			try {
				console.log('🌐 Syncing reorder to backend...');
				await claraAPI.updateTask(movedTask.id, {
					// Note: The backend might not have an order field, 
					// but we're updating to trigger any backend reordering logic
					title: movedTask.title // Minimal update to sync
				});
				console.log(`✅ Task ${movedTask.id} reordered in backend`);
			} catch (error) {
				console.error('❌ Failed to reorder task in backend:', error);
				// Rollback to original state
				this.tasks = originalTasks;
				this.saveTasks();
				console.log('🔄 Rolled back reorder due to backend error');
				// Don't throw error for reordering - it's less critical than moving parents
			}
		}
	}

	findTaskById(id: number, tasks: Task[] = this.tasks): Task | null {
		// Only log for top-level calls to avoid spam
		const isTopLevel = tasks === this.tasks;
		if (isTopLevel) {
			console.log('🔍 FIND TASK BY ID:', { id, totalTasks: tasks.length });
		}

		for (const task of tasks) {
			if (task.id === id) {
				if (isTopLevel) {
					console.log('✅ Found task:', { id, title: task.title });
				}
				return task;
			}
			const found = this.findTaskById(id, task.subtasks);
			if (found) return found;
		}

		if (isTopLevel) {
			console.log('❌ Task not found:', { id });
		}
		return null;
	}

	private async syncWithBackend(): Promise<void> {
		// First, get all workspaces to see what exists
		const workspaces = await claraAPI.getAllWorkspacesSnapshot();
		
		if (workspaces.length === 0) {
			// No workspaces exist, create a default one
			console.log('No workspaces found, creating default workspace...');
			await this.createDefaultWorkspace();
			// Try again after creating workspace
			return this.syncWithBackend();
		}
		
		// Use the first available workspace
		const workspace = workspaces[0];
		this.workspaceId = workspace.id;
		
		// Convert backend tasks to frontend format
		const frontendTasks = this.convertBackendTasksToFrontend(workspace.tasks);
		
		// Update state
		this.tasks = frontendTasks;
		this.updateNextId();
		
		// Save to localStorage as backup
		this.saveTasks();
		
		console.log(`Loaded ${frontendTasks.length} tasks from workspace "${workspace.title}" (ID: ${workspace.id})`);
	}

	private async createDefaultWorkspace(): Promise<void> {
		try {
			const workspace = await claraAPI.createWorkspace({
				title: 'General Workspace',
				description: 'Default workspace for task management'
			});
			this.workspaceId = workspace.id;
			console.log(`Created default workspace: ${workspace.title} (ID: ${workspace.id})`);
		} catch (error) {
			console.error('Failed to create default workspace:', error);
			throw error;
		}
	}

	private convertBackendTasksToFrontend(backendTasks: TaskSnapshot[]): Task[] {
		return backendTasks.map((task, index) => ({
			id: task.id,
			title: task.title,
			status: (task.status as 'todo' | 'in-progress' | 'done' | 'archived') || 'todo',
			order: index,
			subtasks: this.convertBackendTasksToFrontend(task.subtasks)
		}));
	}

	private updateNextId() {
		// Find the highest ID in the task tree
		let maxId = 0;
		const findMaxId = (tasks: Task[]) => {
			for (const task of tasks) {
				if (task.id > maxId) maxId = task.id;
				findMaxId(task.subtasks);
			}
		};
		findMaxId(this.tasks);
		this.nextId = maxId + 1;
	}

	private loadTasksFromLocalStorage() {
		if (typeof window !== 'undefined') {
			const saved = localStorage.getItem('simple-tasks');
			if (saved) {
				try {
					const data = JSON.parse(saved);
					this.tasks = this.ensureSubtasks(data.tasks || []);
					this.nextId = data.nextId || 1;
					console.log(`Loaded ${this.tasks.length} tasks from localStorage`);
				} catch (e) {
					console.error('Failed to load tasks from localStorage:', e);
				}
			}
		}
	}

	// Public method to manually sync with backend
	async refreshFromBackend(): Promise<boolean> {
		try {
			await this.syncWithBackend();
			this.isOnline = true;
			return true;
		} catch (error) {
			console.error('Failed to sync with backend:', error);
			this.isOnline = false;
			return false;
		}
	}

	// Check if we're connected to backend
	get isConnectedToBackend(): boolean {
		return this.isOnline;
	}

	// Clear localStorage and force sync with backend
	async clearLocalStorageAndSync(): Promise<boolean> {
		if (typeof window !== 'undefined') {
			localStorage.removeItem('simple-tasks');
			console.log('🗑️ Cleared localStorage');
		}
		
		return await this.refreshFromBackend();
	}

	private ensureSubtasks(tasks: any[]): Task[] {
		return tasks.map(task => ({
			...task,
			subtasks: task.subtasks ? this.ensureSubtasks(task.subtasks) : []
		}));
	}

	async deleteTask(taskId: number) {
		// Remove from local state first (immediate feedback)
		this.tasks = this.removeTaskFromArray(this.tasks, taskId);
		this.saveTasks();
		
		// Try to delete from backend
		if (this.isOnline) {
			try {
				await claraAPI.deleteTask(taskId);
				console.log(`Task ${taskId} deleted from backend`);
			} catch (error) {
				console.error('Failed to delete task from backend:', error);
				// Task is already removed locally, so don't re-add it
			}
		}
	}

	private removeTaskFromArray(tasks: Task[], taskId: number): Task[] {
		return tasks.filter(task => {
			if (task.id === taskId) {
				return false;
			}
			task.subtasks = this.removeTaskFromArray(task.subtasks, taskId);
			return true;
		});
	}

	async moveTaskToParent(taskId: number, newParentId?: number, insertIndex?: number) {
		console.log('🚚 MOVE TASK TO PARENT:', {
			taskId,
			newParentId,
			insertIndex,
			timestamp: new Date().toISOString()
		});

		const task = this.findTaskById(taskId);
		if (!task) {
			console.warn(`❌ Task ${taskId} not found`);
			return;
		}

		console.log('📦 Found task to move:', {
			taskId: task.id,
			taskTitle: task.title,
			currentSubtasksCount: task.subtasks.length
		});

		// Prevent circular dependencies
		if (newParentId) {
			if (taskId === newParentId) {
				console.warn('🚫 Cannot move task to itself');
				return;
			}
			
			if (this.wouldCreateCircularDependency(taskId, newParentId)) {
				console.warn('🚫 Cannot move task: would create circular dependency');
				return;
			}
		}

		// Store original state for rollback
		const originalTasks = JSON.parse(JSON.stringify(this.tasks));
		console.log('💾 Stored original state for rollback');

		// Remove task from current location
		this.tasks = this.removeTaskFromArray(this.tasks, taskId);
		console.log('🗑️ Removed task from current location');

		if (newParentId) {
			// Add as subtask to new parent
			const newParent = this.findTaskById(newParentId);
			if (newParent) {
				console.log('🎯 Found new parent:', {
					parentId: newParent.id,
					parentTitle: newParent.title,
					currentSubtasksCount: newParent.subtasks.length,
					insertIndex
				});

				if (insertIndex !== undefined) {
					newParent.subtasks.splice(insertIndex, 0, task);
					console.log(`📍 Inserted task at index ${insertIndex}`);
				} else {
					newParent.subtasks.push(task);
					console.log('📍 Added task to end of subtasks');
				}
			} else {
				console.warn(`❌ New parent task ${newParentId} not found`);
				// Re-add task to original location if parent not found
				this.tasks.push(task);
				return;
			}
		} else {
			// Add to root level
			console.log('🌳 Moving to root level:', { insertIndex });
			if (insertIndex !== undefined) {
				this.tasks.splice(insertIndex, 0, task);
				console.log(`📍 Inserted at root index ${insertIndex}`);
			} else {
				this.tasks.push(task);
				console.log('📍 Added to end of root tasks');
			}
		}

		// Save to localStorage first (immediate feedback)
		this.saveTasks();
		console.log('💾 Move saved to localStorage');

		// Try to update backend
		if (this.isOnline) {
			try {
				console.log('🌐 Syncing move to backend...');
				await claraAPI.updateTask(taskId, {
					parent_task_id: newParentId || undefined
				});
				console.log(`✅ Task ${taskId} moved to parent ${newParentId || 'root'} in backend`);
			} catch (error) {
				console.error('❌ Failed to move task in backend:', error);
				// Rollback to original state
				this.tasks = originalTasks;
				this.saveTasks();
				console.log('🔄 Rolled back move due to backend error');
				throw error; // Re-throw to let UI handle the error
			}
		}
	}

	private wouldCreateCircularDependency(taskId: number, potentialParentId: number): boolean {
		// Check if the potential parent is actually a descendant of the task being moved
		const task = this.findTaskById(taskId);
		if (!task) return false;
		
		return this.isTaskDescendant(task, potentialParentId);
	}

	private isTaskDescendant(parentTask: Task, childTaskId: number): boolean {
		// Check if childTaskId exists anywhere in parentTask's subtask tree
		// Use iterative approach to prevent stack overflow on deep hierarchies
		if (!parentTask.subtasks || parentTask.subtasks.length === 0) {
			return false;
		}
		
		const toCheck = [...parentTask.subtasks];
		const visited = new Set<number>();
		
		while (toCheck.length > 0) {
			const current = toCheck.pop()!;
			
			// Prevent infinite loops
			if (visited.has(current.id)) {
				continue;
			}
			visited.add(current.id);
			
			if (current.id === childTaskId) {
				return true;
			}
			
			if (current.subtasks && current.subtasks.length > 0) {
				toCheck.push(...current.subtasks);
			}
		}
		
		return false;
	}

	saveTasks() {
		if (typeof window !== 'undefined') {
			localStorage.setItem('simple-tasks', JSON.stringify({
				tasks: this.tasks,
				nextId: this.nextId
			}));
		}
	}


}

export const taskState = new TaskState(); 