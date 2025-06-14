<script lang="ts">
	import { Plus } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { taskState } from '$lib/state/taskState.svelte';

	function focusInput(element: HTMLInputElement) {
		element.focus();
		element.select();
	}

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
	let draggedInfo = $state<{ index: number; parentId?: number; task: Task } | null>(null);
	let dropIndicator = $state<{ index: number; parentId?: number } | null>(null);
	let editingTaskId = $state<number | null>(null);
	let editingTitle = $state('');
	let dragPreview = $state<{ x: number; y: number; task: Task } | null>(null);
	let isDragging = $state(false);

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

	function handleDragStart(event: DragEvent, index: number, task: Task, parentId?: number) {
		draggedInfo = { index, parentId, task };
		isDragging = true;

		if (event.dataTransfer) {
			event.dataTransfer.effectAllowed = 'move';
			// Create invisible drag image
			const dragImage = document.createElement('div');
			dragImage.style.opacity = '0';
			document.body.appendChild(dragImage);
			event.dataTransfer.setDragImage(dragImage, 0, 0);
			setTimeout(() => document.body.removeChild(dragImage), 0);
		}

		// Start tracking mouse position for drag preview
		updateDragPreview(event.clientX, event.clientY);
		document.addEventListener('dragover', handleDocumentDragOver);
	}

	function handleDocumentDragOver(event: MouseEvent) {
		if (draggedInfo && isDragging) {
			updateDragPreview(event.clientX, event.clientY);
		}
	}

	function updateDragPreview(x: number, y: number) {
		if (draggedInfo) {
			dragPreview = { x: x + 10, y: y + 10, task: draggedInfo.task };
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		if (event.dataTransfer) {
			event.dataTransfer.dropEffect = 'move';
		}
	}

	function handleDragEnter(index: number, parentId?: number) {
		// Show drop indicator
		if (draggedInfo && draggedInfo.parentId === parentId) {
			dropIndicator = { index, parentId };
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
		dropIndicator = null;
		dragPreview = null;
		isDragging = false;
		document.removeEventListener('dragover', handleDocumentDragOver);
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

	function saveEdit() {
		if (editingTaskId && editingTitle.trim()) {
			const task = taskState.findTaskById(editingTaskId);
			if (task) {
				task.title = editingTitle.trim();
				taskState.saveTasks();
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

	function deleteTask(task: Task) {
		taskState.deleteTask(task.id);
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

	<!-- Task list as cards -->
	<div class="space-y-4">
		{#each taskState.tasks as task, index (task.id)}
			<div class="bg-white dark:bg-gray-700 rounded-lg border shadow-sm p-4">
				{@render taskCard(task, index, [])}
			</div>
		{/each}

		<!-- Drop zone at end of root list -->
		<div
			class="h-4 -my-2"
			ondragover={handleDragOver}
			ondragenter={() => handleDragEnter(taskState.tasks.length)}
			ondrop={(e) => handleDrop(e, taskState.tasks.length)}
		></div>

		<!-- Drop indicator at end of root list -->
		{#if dropIndicator?.index === taskState.tasks.length && !dropIndicator?.parentId}
			<div class="h-0.5 bg-blue-500 rounded-full opacity-75 transition-all duration-200"></div>
		{/if}

		{#if taskState.tasks.length === 0}
			<div class="text-center py-8 text-gray-500 dark:text-gray-400">
				<p>No tasks yet. Click the + button to add your first task.</p>
			</div>
		{/if}
	</div>

	{#snippet taskCard(task: Task, index: number, parentNumbers: number[])}
		<div class="space-y-3">
			<!-- Main task -->
			<div
				class="group flex items-center gap-3"
				class:opacity-30={isDragging && draggedInfo?.task.id === task.id}
				draggable="true"
				ondragstart={(e) => handleDragStart(e, index, task, undefined)}
				ondragover={handleDragOver}
				ondragenter={() => handleDragEnter(index, undefined)}
				ondrop={(e) => handleDrop(e, index, undefined)}
				ondragend={handleDragEnd}
			>
				<span class="text-sm font-medium text-gray-500 dark:text-gray-400 min-w-[3rem]">
					{getTaskNumber(index, parentNumbers)}
				</span>

				{#if editingTaskId === task.id}
					<input
						bind:value={editingTitle}
						class="flex-1 bg-white dark:bg-gray-800 border border-blue-300 dark:border-blue-600 rounded px-2 py-1 outline-none focus:border-blue-500"
						onkeydown={handleEditKeydown}
						onblur={saveEdit}
						use:focusInput
					/>
				{:else}
					<span
						class="flex-1 text-gray-900 dark:text-white cursor-text hover:bg-gray-100 dark:hover:bg-gray-600 rounded px-2 py-1 transition-colors"
						onclick={() => startEditing(task)}
					>
						{task.title}
					</span>
				{/if}

				<div class="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
					<Button
						onclick={(e) => {
							e.stopPropagation();
							addTask(task);
						}}
						size="sm"
						variant="ghost"
						class="h-6 w-6 p-0"
					>
						<Plus class="h-3 w-3" />
					</Button>
					<button
						class="h-6 w-6 flex items-center justify-center text-red-600 hover:text-red-800 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
						onclick={(e) => {
							e.stopPropagation();
							deleteTask(task);
						}}
					>
						🗑️
					</button>
				</div>
			</div>

			<!-- Add subtask input -->
			{#if showingInputForTask === task.id}
				<div
					class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
					style="margin-left: {(parentNumbers.length + 1) * 20}px"
				>
					<div class="flex items-center gap-2 mb-2">
						<span class="text-sm font-medium text-gray-500 dark:text-gray-400 min-w-[3rem]">
							{getTaskNumber(task.subtasks.length, [...parentNumbers, index + 1])}
						</span>
						<input
							bind:value={newTaskTitle}
							placeholder="Enter subtask title..."
							onkeydown={handleKeydown}
							class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
							use:focusInput
						/>
					</div>
					<div class="flex gap-2">
						<Button onclick={saveTask} size="sm" disabled={!newTaskTitle.trim()}>Save</Button>
						<Button onclick={cancelAdd} variant="outline" size="sm">Cancel</Button>
					</div>
				</div>
			{/if}

			<!-- Render subtasks -->
			{#if task.subtasks.length > 0}
				<div class="space-y-2" style="margin-left: 20px">
					{#each task.subtasks as subtask, subIndex (subtask.id)}
						{@render taskItem(subtask, subIndex, [...parentNumbers, index + 1], task)}
					{/each}
				</div>
			{/if}
		</div>
	{/snippet}

	{#snippet taskItem(task: Task, index: number, parentNumbers: number[], parentTask: Task)}
		<div class="space-y-2">
			<!-- Drop indicator above -->
			{#if dropIndicator?.index === index && dropIndicator?.parentId === parentTask.id}
				<div
					class="h-0.5 bg-blue-500 rounded-full opacity-75 transition-all duration-200"
					style="margin-left: {(parentNumbers.length - 1) * 20}px"
				></div>
			{/if}

			<div
				class="group flex items-center gap-3 py-2"
				class:opacity-30={isDragging && draggedInfo?.task.id === task.id}
				style="margin-left: {(parentNumbers.length - 1) * 20}px"
				draggable="true"
				ondragstart={(e) => handleDragStart(e, index, task, parentTask.id)}
				ondragover={handleDragOver}
				ondragenter={() => handleDragEnter(index, parentTask.id)}
				ondrop={(e) => handleDrop(e, index, parentTask.id)}
				ondragend={handleDragEnd}
			>
				<span class="text-sm font-medium text-gray-500 dark:text-gray-400 min-w-[3rem]">
					{getTaskNumber(index, parentNumbers)}
				</span>

				{#if editingTaskId === task.id}
					<input
						bind:value={editingTitle}
						class="flex-1 bg-white dark:bg-gray-800 border border-blue-300 dark:border-blue-600 rounded px-2 py-1 outline-none focus:border-blue-500"
						onkeydown={handleEditKeydown}
						onblur={saveEdit}
						use:focusInput
					/>
				{:else}
					<span
						class="flex-1 text-gray-900 dark:text-white cursor-text hover:bg-gray-100 dark:hover:bg-gray-600 rounded px-2 py-1 transition-colors"
						onclick={() => startEditing(task)}
					>
						{task.title}
					</span>
				{/if}

				<div class="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
					<Button
						onclick={(e) => {
							e.stopPropagation();
							addTask(task);
						}}
						size="sm"
						variant="ghost"
						class="h-6 w-6 p-0"
					>
						<Plus class="h-3 w-3" />
					</Button>
					<button
						class="h-6 w-6 flex items-center justify-center text-red-600 hover:text-red-800 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
						onclick={(e) => {
							e.stopPropagation();
							deleteTask(task);
						}}
					>
						🗑️
					</button>
				</div>
			</div>

			<!-- Add subtask input -->
			{#if showingInputForTask === task.id}
				<div
					class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
					style="margin-left: {parentNumbers.length * 20}px"
				>
					<div class="flex items-center gap-2 mb-2">
						<span class="text-sm font-medium text-gray-500 dark:text-gray-400 min-w-[3rem]">
							{getTaskNumber(task.subtasks.length, [...parentNumbers, index + 1])}
						</span>
						<input
							bind:value={newTaskTitle}
							placeholder="Enter subtask title..."
							onkeydown={handleKeydown}
							class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
							use:focusInput
						/>
					</div>
					<div class="flex gap-2">
						<Button onclick={saveTask} size="sm" disabled={!newTaskTitle.trim()}>Save</Button>
						<Button onclick={cancelAdd} variant="outline" size="sm">Cancel</Button>
					</div>
				</div>
			{/if}

			<!-- Render subtasks -->
			{#if task.subtasks.length > 0}
				<div class="space-y-2">
					{#each task.subtasks as subtask, subIndex (subtask.id)}
						{@render taskItem(subtask, subIndex, [...parentNumbers, index + 1], task)}
					{/each}
				</div>
			{/if}

			<!-- Drop zone at end of subtask list -->
			<div
				class="h-4 -my-2"
				style="margin-left: {parentNumbers.length * 20}px"
				ondragover={handleDragOver}
				ondragenter={() => handleDragEnter(task.subtasks.length, task.id)}
				ondrop={(e) => handleDrop(e, task.subtasks.length, task.id)}
			></div>

			<!-- Drop indicator at end of subtask list -->
			{#if dropIndicator?.index === task.subtasks.length && dropIndicator?.parentId === task.id}
				<div
					class="h-0.5 bg-blue-500 rounded-full opacity-75 transition-all duration-200"
					style="margin-left: {parentNumbers.length * 20}px"
				></div>
			{/if}
		</div>
	{/snippet}

	<!-- Drag Preview -->
	{#if dragPreview}
		<div
			class="fixed pointer-events-none z-50 bg-white dark:bg-gray-700 rounded-lg border shadow-lg p-3 transform -translate-x-1/2 -translate-y-1/2"
			style="left: {dragPreview.x}px; top: {dragPreview.y}px;"
		>
			<div class="flex items-center gap-2">
				<span class="text-sm font-medium text-gray-500 dark:text-gray-400">
					{draggedInfo ? getTaskNumber(draggedInfo.index, []) : ''}
				</span>
				<span class="text-gray-900 dark:text-white">
					{dragPreview.task.title}
				</span>
			</div>
		</div>
	{/if}
</div>
