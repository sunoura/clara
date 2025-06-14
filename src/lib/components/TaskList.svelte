<script lang="ts">
	import { Plus } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { taskState } from '$lib/state/taskState.svelte';

	interface Task {
		id: number;
		title: string;
		order: number;
		subtasks: Task[];
	}

	let showAddInput = $state(false);
	let newTaskTitle = $state('');
	let addingToTaskId = $state<number | null>(null);
	let showingInputForTask = $state<number | null>(null);
	let draggedInfo = $state<{ index: number; parentId?: number } | null>(null);

	function addTask(parentTask?: Task) {
		if (parentTask) {
			// Adding subtask - show input inside the task
			showingInputForTask = parentTask.id;
			addingToTaskId = parentTask.id;
			showAddInput = false;
		} else {
			// Adding root task - show input at top
			showAddInput = true;
			addingToTaskId = null;
			showingInputForTask = null;
		}
	}

	function addRootTask() {
		addTask();
	}

	function saveTask() {
		if (newTaskTitle.trim()) {
			const parentTask = addingToTaskId ? taskState.findTaskById(addingToTaskId) : undefined;
			taskState.addTask(newTaskTitle.trim(), parentTask || undefined);
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

	function handleDragStart(event: DragEvent, index: number, parentId?: number) {
		draggedInfo = { index, parentId };
		if (event.dataTransfer) {
			event.dataTransfer.effectAllowed = 'move';
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		if (event.dataTransfer) {
			event.dataTransfer.dropEffect = 'move';
		}
	}

	function handleDrop(event: DragEvent, dropIndex: number, parentId?: number) {
		event.preventDefault();
		if (draggedInfo && (draggedInfo.index !== dropIndex || draggedInfo.parentId !== parentId)) {
			const dragParent = draggedInfo.parentId
				? taskState.findTaskById(draggedInfo.parentId)
				: undefined;
			const dropParent = parentId ? taskState.findTaskById(parentId) : undefined;

			// Only allow reordering within the same parent for now
			if (draggedInfo.parentId === parentId) {
				taskState.reorderTasks(draggedInfo.index, dropIndex, dragParent || undefined);
			}
		}
		draggedInfo = null;
	}

	function handleDragEnd() {
		draggedInfo = null;
	}

	function getTaskNumber(index: number, parentNumbers: number[] = []): string {
		const currentNumber = index + 1;
		if (parentNumbers.length === 0) {
			return `${currentNumber}.`;
		}
		return `${parentNumbers.join('.')}.${currentNumber}`;
	}
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border p-6">
	<!-- Header with + button -->
	<div class="flex items-center justify-between mb-6">
		<h1 class="text-2xl font-bold text-gray-900 dark:text-white">Tasks</h1>
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
			<Input
				bind:value={newTaskTitle}
				placeholder="Enter task title..."
				{...{ onkeydown: handleKeydown }}
				class="w-full"
			/>
			<div class="flex gap-2 mt-2">
				<Button onclick={saveTask} size="sm" disabled={!newTaskTitle.trim()}>Save</Button>
				<Button onclick={cancelAdd} variant="outline" size="sm">Cancel</Button>
			</div>
		</div>
	{/if}

	<!-- Task list -->
	<div class="space-y-1">
		{#each taskState.tasks as task, index (task.id)}
			{@render taskItem(task, index, [])}
		{:else}
			<div class="text-center py-8 text-gray-500 dark:text-gray-400">
				<p>No tasks yet. Click the + button to add your first task.</p>
			</div>
		{/each}
	</div>

	{#snippet taskItem(task: Task, index: number, parentNumbers: number[])}
		<div class="space-y-1">
			<div
				class="group flex items-center gap-3 p-3 rounded-lg border bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors cursor-move"
				style="margin-left: {parentNumbers.length * 20}px"
				draggable="true"
				ondragstart={(e) =>
					handleDragStart(
						e,
						index,
						parentNumbers.length > 0 ? taskState.findTaskById(task.id)?.id : undefined
					)}
				ondragover={handleDragOver}
				ondrop={(e) =>
					handleDrop(
						e,
						index,
						parentNumbers.length > 0 ? taskState.findTaskById(task.id)?.id : undefined
					)}
				ondragend={handleDragEnd}
				class:opacity-50={draggedInfo?.index === index &&
					draggedInfo?.parentId ===
						(parentNumbers.length > 0 ? taskState.findTaskById(task.id)?.id : undefined)}
			>
				<span class="text-sm font-medium text-gray-500 dark:text-gray-400 min-w-[3rem]">
					{getTaskNumber(index, parentNumbers)}
				</span>
				<span class="flex-1 text-gray-900 dark:text-white">
					{task.title}
				</span>
				<Button
					onclick={(e) => {
						e.stopPropagation();
						addTask(task);
					}}
					size="sm"
					variant="ghost"
					class="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity"
				>
					<Plus class="h-3 w-3" />
				</Button>
			</div>

			<!-- Add subtask input - appears inside this task -->
			{#if showingInputForTask === task.id}
				<div
					class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 ml-4"
					style="margin-left: {(parentNumbers.length + 1) * 20}px"
				>
					<Input
						bind:value={newTaskTitle}
						placeholder="Enter subtask title..."
						{...{ onkeydown: handleKeydown }}
						class="w-full"
					/>
					<div class="flex gap-2 mt-2">
						<Button onclick={saveTask} size="sm" disabled={!newTaskTitle.trim()}>Save</Button>
						<Button onclick={cancelAdd} variant="outline" size="sm">Cancel</Button>
					</div>
				</div>
			{/if}

			<!-- Render subtasks -->
			{#each task.subtasks as subtask, subIndex (subtask.id)}
				{@render taskItem(subtask, subIndex, [...parentNumbers, index + 1])}
			{/each}
		</div>
	{/snippet}
</div>
