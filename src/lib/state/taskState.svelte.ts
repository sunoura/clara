interface Task {
	id: number;
	title: string;
	order: number;
	subtasks: Task[];
}

class TaskState {
	tasks = $state<Task[]>([]);
	private nextId = 1;

	constructor() {
		this.loadTasks();
	}

	addTask(title: string, parentTask?: Task) {
		const task: Task = {
			id: this.nextId++,
			title,
			order: parentTask && parentTask.subtasks ? parentTask.subtasks.length : this.tasks.length,
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
		this.saveTasks();
	}

	reorderTasks(fromIndex: number, toIndex: number, parentTask?: Task) {
		const targetArray = parentTask ? parentTask.subtasks : this.tasks;
		const newTasks = [...targetArray];
		const [movedTask] = newTasks.splice(fromIndex, 1);
		newTasks.splice(toIndex, 0, movedTask);
		
		// Update order values
		newTasks.forEach((task, index) => {
			task.order = index;
		});
		
		if (parentTask) {
			parentTask.subtasks = newTasks;
		} else {
			this.tasks = newTasks;
		}
		this.saveTasks();
	}

	findTaskById(id: number, tasks: Task[] = this.tasks): Task | null {
		for (const task of tasks) {
			if (task.id === id) return task;
			const found = this.findTaskById(id, task.subtasks);
			if (found) return found;
		}
		return null;
	}

	private loadTasks() {
		if (typeof window !== 'undefined') {
			const saved = localStorage.getItem('simple-tasks');
			if (saved) {
				try {
					const data = JSON.parse(saved);
					this.tasks = this.ensureSubtasks(data.tasks || []);
					this.nextId = data.nextId || 1;
				} catch (e) {
					console.error('Failed to load tasks:', e);
				}
			}
		}
	}

	private ensureSubtasks(tasks: any[]): Task[] {
		return tasks.map(task => ({
			...task,
			subtasks: task.subtasks ? this.ensureSubtasks(task.subtasks) : []
		}));
	}

	private saveTasks() {
		if (typeof window !== 'undefined') {
			localStorage.setItem('simple-tasks', JSON.stringify({
				tasks: this.tasks,
				nextId: this.nextId
			}));
		}
	}
}

export const taskState = new TaskState(); 