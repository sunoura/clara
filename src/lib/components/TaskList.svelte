<script lang="ts">
	import { Plus, Trash2, Check } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { taskState } from '$lib/state/taskState.svelte';
	import { claraAPI } from '$lib/api/clara';

	function focusInput(element: HTMLInputElement) {
		element.focus();
		element.select();
	}

	interface Task {
		id: number;
		title: string;
		order: number;
		status: 'todo' | 'in-progress' | 'done' | 'archived';
		subtasks: Task[];
	}

	let showAddInput = $state(false);
	let newTaskTitle = $state('');
	let addingToTaskId = $state<number | null>(null);
	let showingInputForTask = $state<number | null>(null);
	let editingTaskId = $state<number | null>(null);
	let editingTitle = $state('');

	// Simple drag and drop state - based on the example
	let mouseYCoordinate = $state<number | null>(null);
	let distanceTopGrabbedVsPointer = $state<number | null>(null);
	let draggingTask = $state<Task | null>(null);
	let draggingTaskId = $state<number | null>(null);
	let draggingTaskIndex = $state<number | null>(null);
	let draggingFromParent = $state<Task | null>(null);
	let hoveredTaskIndex = $state<number | null>(null);
	let hoveredParent = $state<Task | null>(null);

	// Individual hover states for each task
	let hoveredTaskId = $state<number | null>(null);

	// Reactive swapping logic
	$effect(() => {
		if (
			draggingTaskIndex !== null &&
			hoveredTaskIndex !== null &&
			draggingTaskIndex !== hoveredTaskIndex &&
			draggingFromParent === hoveredParent // Only swap within same parent
		) {
			console.log('🔄 Swapping tasks:', {
				from: draggingTaskIndex,
				to: hoveredTaskIndex,
				parent: hoveredParent?.id || 'root'
			});

			const targetArray = hoveredParent ? hoveredParent.subtasks : taskState.tasks;

			// Swap items
			[targetArray[draggingTaskIndex], targetArray[hoveredTaskIndex]] = [
				targetArray[hoveredTaskIndex],
				targetArray[draggingTaskIndex]
			];

			// Update dragging index to follow the item
			draggingTaskIndex = hoveredTaskIndex;

			// Save to localStorage immediately
			taskState.saveTasks();

			// Try to sync with backend
			syncReorderToBackend();
		}
	});

	async function syncReorderToBackend() {
		if (!taskState.isConnectedToBackend) return;

		try {
			// Get the current order of tasks in the target parent
			const targetArray = hoveredParent ? hoveredParent.subtasks : taskState.tasks;
			const taskIds = targetArray.map((task) => task.id);

			console.log('🌐 Syncing reorder to backend:', {
				taskIds,
				parentId: hoveredParent?.id || null,
				isRoot: !hoveredParent
			});

			// Call the reorder API
			const response = await fetch('/api/clara/tasks/reorder', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					task_ids: taskIds,
					parent_task_id: hoveredParent?.id || null,
					workspace_id: hoveredParent ? null : 1 // Default workspace ID
				})
			});

			if (response.ok) {
				console.log('✅ Reorder synced to backend');
			} else {
				console.error('❌ Failed to sync reorder to backend:', await response.text());
			}
		} catch (error) {
			console.error('❌ Failed to sync reorder to backend:', error);
		}
	}

	function addTask(parentTask?: Task) {
		if (parentTask) {
			showingInputForTask = parentTask.id;
			addingToTaskId = parentTask.id;
			showAddInput = false;
		} else {
			showAddInput = true;
			addingToTaskId = null;
			showingInputForTask = null;
		}
	}

	function addRootTask() {
		addTask();
	}

	async function saveTask() {
		if (newTaskTitle.trim()) {
			const parentTask = addingToTaskId ? taskState.findTaskById(addingToTaskId) : undefined;
			await taskState.addTask(newTaskTitle.trim(), parentTask || undefined);
			newTaskTitle = '';
		}
		showAddInput = false;
		addingToTaskId = null;
		showingInputForTask = null;
	}

	function cancelAdd() {
		newTaskTitle = '';
		showAddInput = false;
		addingToTaskId = null;
		showingInputForTask = null;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			saveTask();
		} else if (event.key === 'Escape') {
			cancelAdd();
		}
	}

	function getTaskNumber(index: number, parentNumbers: number[] = []): string {
		const currentNumber = index + 1;
		if (parentNumbers.length === 0) {
			return `${currentNumber}.`;
		}
		return `${parentNumbers.join('.')}.${currentNumber}`;
	}

	function startEditing(task: Task) {
		editingTaskId = task.id;
		editingTitle = task.title;
	}

	async function saveEdit() {
		if (editingTaskId && editingTitle.trim()) {
			const task = taskState.findTaskById(editingTaskId);
			if (task) {
				const oldTitle = task.title;
				task.title = editingTitle.trim();
				taskState.saveTasks();

				// Try to update backend
				if (taskState.isConnectedToBackend) {
					try {
						await claraAPI.updateTask(editingTaskId, {
							title: editingTitle.trim()
						});
						console.log(`Task ${editingTaskId} title updated in backend`);
					} catch (error) {
						console.error('Failed to update task title in backend:', error);
						// Rollback title change
						task.title = oldTitle;
						taskState.saveTasks();
						alert('Failed to update task title. Please try again.');
					}
				}
			}
		}
		editingTaskId = null;
		editingTitle = '';
	}

	function cancelEdit() {
		editingTaskId = null;
		editingTitle = '';
	}

	function handleEditKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			saveEdit();
		} else if (event.key === 'Escape') {
			cancelEdit();
		}
	}

	async function deleteTask(task: Task) {
		await taskState.deleteTask(task.id);
	}

	async function toggleTaskComplete(task: Task) {
		try {
			const newStatus = task.status === 'done' ? 'todo' : 'done';
			// Update locally first
			task.status = newStatus;
			taskState.saveTasks();

			// Try to update backend
			if (taskState.isConnectedToBackend) {
				try {
					await claraAPI.updateTask(task.id, { status: newStatus });
					console.log(`Task ${task.id} status updated to ${newStatus} in backend`);
				} catch (error) {
					console.error('Failed to update task status in backend:', error);
					// Rollback status change
					task.status = task.status === 'done' ? 'todo' : 'done';
					taskState.saveTasks();
					alert('Failed to update task status. Please try again.');
				}
			}
		} catch (error) {
			console.error('Failed to toggle task completion:', error);
		}
	}

	async function refreshFromBackend() {
		const success = await taskState.refreshFromBackend();
		if (success) {
			console.log('✅ Successfully synced with backend');
		} else {
			console.log('❌ Failed to sync with backend');
		}
	}

	async function clearAndSync() {
		const success = await taskState.clearLocalStorageAndSync();
		if (success) {
			console.log('✅ Cleared localStorage and synced with backend');
		} else {
			console.log('❌ Failed to clear and sync');
		}
	}

	// Drag and drop handlers
	function handleDragStart(event: DragEvent, task: Task, index: number, parentTask?: Task) {
		console.log('🚀 DRAG START:', {
			taskId: task.id,
			title: task.title,
			index,
			parentId: parentTask?.id
		});

		mouseYCoordinate = event.clientY;
		draggingTask = task;
		draggingTaskIndex = index;
		draggingTaskId = task.id;
		draggingFromParent = parentTask || null;

		const target = event.target as HTMLElement;
		distanceTopGrabbedVsPointer = target.getBoundingClientRect().y - event.clientY;

		event.dataTransfer!.effectAllowed = 'move';
	}

	function handleDrag(event: DragEvent) {
		mouseYCoordinate = event.clientY;
	}

	function handleDragOver(event: DragEvent, index: number, parentTask?: Task) {
		event.preventDefault();
		hoveredTaskIndex = index;
		hoveredParent = parentTask || null;
	}

	function handleDragEnd() {
		console.log('🏁 DRAG END - cleaning up');

		// Clean up all drag state
		mouseYCoordinate = null;
		distanceTopGrabbedVsPointer = null;
		draggingTask = null;
		draggingTaskId = null;
		draggingTaskIndex = null;
		draggingFromParent = null;
		hoveredTaskIndex = null;
		hoveredParent = null;
		hoveredTaskId = null;
	}
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border p-6">
	<!-- Header with + button and connection status -->
	<div class="flex items-center justify-between mb-6">
		<div class="flex items-center gap-3">
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">Tasks</h1>
			<div class="flex items-center gap-2">
				<div class="flex items-center gap-1">
					<div
						class="w-2 h-2 rounded-full {taskState.isConnectedToBackend
							? 'bg-green-500'
							: 'bg-yellow-500'}"
						title={taskState.isConnectedToBackend ? 'Connected to backend' : 'Using local storage'}
					></div>
					<span class="text-xs text-gray-500">
						{taskState.isConnectedToBackend ? 'Online' : 'Offline'}
					</span>
				</div>
				<button
					onclick={refreshFromBackend}
					class="text-xs text-blue-600 hover:text-blue-800 underline"
					title="Sync with backend"
				>
					Sync
				</button>
				<button
					onclick={clearAndSync}
					class="text-xs text-red-600 hover:text-red-800 underline"
					title="Clear local data and sync with backend"
				>
					Reset
				</button>
			</div>
		</div>
		{#if !showAddInput}
			<Button onclick={addRootTask} size="sm" class="h-8 w-8 p-0">
				<Plus class="h-4 w-4" />
			</Button>
		{/if}
	</div>

	<!-- Add task input -->
	{#if showAddInput}
		<div
			class="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
		>
			<input
				bind:value={newTaskTitle}
				placeholder="Enter task title..."
				onkeydown={handleKeydown}
				class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
				use:focusInput
			/>
			<div class="flex gap-2 mt-2">
				<Button onclick={saveTask} size="sm" disabled={!newTaskTitle.trim()}>Save</Button>
				<Button onclick={cancelAdd} variant="outline" size="sm">Cancel</Button>
			</div>
		</div>
	{/if}

	<!-- Drag ghost -->
	{#if mouseYCoordinate && draggingTask}
		<div
			class="fixed pointer-events-none z-50 bg-white dark:bg-gray-700 rounded-lg border-2 border-blue-400 shadow-xl p-3 opacity-80"
			style="top: {mouseYCoordinate + (distanceTopGrabbedVsPointer || 0)}px; left: 20px;"
		>
			<div class="flex items-center gap-2">
				<span class="text-sm font-medium text-gray-500 dark:text-gray-400">
					{draggingTaskIndex !== null ? getTaskNumber(draggingTaskIndex, []) : ''}
				</span>
				<span class="text-gray-900 dark:text-white font-medium">
					{draggingTask.title}
				</span>
			</div>
		</div>
	{/if}

	<!-- Task list -->
	<div class="space-y-4">
		{#each taskState.tasks as task, index (task.id)}
			<div
				class="bg-white dark:bg-gray-700 rounded-lg border shadow-sm p-4 transition-all duration-200"
				class:opacity-30={draggingTaskId === task.id}
			>
				{@render taskCard(task, index, [])}
			</div>
		{/each}
	</div>
</div>

{#snippet taskCard(task: Task, index: number, parentNumbers: number[], parentTask?: Task)}
	<div
		class="group"
		onmouseenter={() => (hoveredTaskId = task.id)}
		onmouseleave={() => (hoveredTaskId = null)}
	>
		<div
			class="flex items-center gap-3 cursor-move"
			draggable="true"
			ondragstart={(e) => handleDragStart(e, task, index, parentTask)}
			ondrag={handleDrag}
			ondragover={(e) => handleDragOver(e, index, parentTask)}
			ondragend={handleDragEnd}
		>
			<!-- Drag handle -->
			<div
				class="text-gray-400 hover:text-gray-600 opacity-0 transition-opacity"
				class:opacity-100={hoveredTaskId === task.id}
			>
				⋮⋮
			</div>

			<!-- Task number -->
			<span class="text-sm text-gray-500 font-mono min-w-[2rem]">
				{getTaskNumber(index, parentNumbers)}
			</span>

			<!-- Task content -->
			<div class="flex-1">
				{#if editingTaskId === task.id}
					<input
						bind:value={editingTitle}
						onkeydown={handleEditKeydown}
						class="flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
						use:focusInput
					/>
				{:else}
					<button
						onclick={() => startEditing(task)}
						class="text-left text-gray-900 dark:text-white hover:text-blue-600 transition-colors"
						class:opacity-50={task.status === 'done'}
						class:italic={task.status === 'done'}
						class:line-through={task.status === 'done'}
					>
						{task.title}
					</button>
				{/if}
			</div>

			<!-- Action buttons -->
			<div
				class="flex items-center gap-1 opacity-0 transition-opacity"
				class:opacity-100={hoveredTaskId === task.id}
			>
				{#if editingTaskId === task.id}
					<Button onclick={saveEdit} size="sm" class="h-6 px-2 text-xs">Save</Button>
					<Button onclick={cancelEdit} variant="outline" size="sm" class="h-6 px-2 text-xs"
						>Cancel</Button
					>
				{:else}
					<Button
						onclick={() => toggleTaskComplete(task)}
						variant="ghost"
						size="sm"
						class="h-6 w-6 p-0"
					>
						<Check class="h-3 w-3 {task.status === 'done' ? 'text-green-600' : ''}" />
					</Button>
					<Button onclick={() => addTask(task)} variant="ghost" size="sm" class="h-6 w-6 p-0">
						<Plus class="h-3 w-3" />
					</Button>
					<Button onclick={() => deleteTask(task)} variant="ghost" size="sm" class="h-6 w-6 p-0">
						<Trash2 class="h-3 w-3" />
					</Button>
				{/if}
			</div>
		</div>

		<!-- Add subtask input -->
		{#if showingInputForTask === task.id}
			<div
				class="mt-3 ml-8 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
			>
				<input
					bind:value={newTaskTitle}
					placeholder="Enter subtask title..."
					onkeydown={handleKeydown}
					class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
					use:focusInput
				/>
				<div class="flex gap-2 mt-2">
					<Button onclick={saveTask} size="sm" disabled={!newTaskTitle.trim()}>Save</Button>
					<Button onclick={cancelAdd} variant="outline" size="sm">Cancel</Button>
				</div>
			</div>
		{/if}

		<!-- Subtasks -->
		{#if task.subtasks && task.subtasks.length > 0}
			<div class="mt-3 space-y-3">
				{#each task.subtasks as subtask, subIndex (subtask.id)}
					<div
						class="bg-gray-50 dark:bg-gray-600 rounded-lg border p-3 transition-all duration-200"
						class:opacity-30={draggingTaskId === subtask.id}
					>
						{@render taskCard(subtask, subIndex, [...parentNumbers, index + 1], task)}
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/snippet}
