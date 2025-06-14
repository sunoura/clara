<script lang="ts">
	import { ChevronRight, ChevronDown, FolderOpen, Plus } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { cn } from '$lib/utils.js';
	import { showCreateForm } from '$lib/state/claraState.svelte.js';
	import TaskItem from './TaskItem.svelte';
	import type { Project, Task } from '$lib/types/clara';

	interface Props {
		project: Project;
		onSelectTask?: (task: Task) => void;
		onSelectProject?: (project: Project) => void;
	}

	let { project, onSelectTask, onSelectProject }: Props = $props();

	let expanded = $state(true);

	function toggleExpanded() {
		expanded = !expanded;
	}

	function handleProjectClick() {
		if (onSelectProject) {
			onSelectProject(project);
		}
	}

	function handleAddTask() {
		showCreateForm('task');
	}

	// Calculate project progress
	const allTasks = $derived(() => {
		function getAllTasks(tasks: Task[]): Task[] {
			return tasks.reduce((acc, task) => {
				acc.push(task);
				if (task.subtasks.length > 0) {
					acc.push(...getAllTasks(task.subtasks));
				}
				return acc;
			}, [] as Task[]);
		}
		return getAllTasks(project.tasks);
	});

	const completedTasks = $derived(() => allTasks().filter((t: Task) => t.status === 'done').length);
	const totalTasks = $derived(() => allTasks().length);
	const progressPercent = $derived(() =>
		totalTasks() > 0 ? Math.round((completedTasks() / totalTasks()) * 100) : 0
	);
</script>

<div class="border-b border-gray-200 dark:border-gray-700">
	<!-- Project header -->
	<div class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800/50">
		<!-- Expand/collapse button -->
		<Button variant="ghost" size="icon" class="h-6 w-6 p-0 shrink-0" onclick={toggleExpanded}>
			{#if expanded}
				<ChevronDown class="h-4 w-4" />
			{:else}
				<ChevronRight class="h-4 w-4" />
			{/if}
		</Button>

		<!-- Project icon -->
		<FolderOpen class="h-5 w-5 text-blue-500 shrink-0" />

		<!-- Project info -->
		<div class="flex-1 min-w-0" role="button" tabindex="0" onclick={handleProjectClick}>
			<div class="flex items-center gap-2">
				<span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
					{project.title}
				</span>

				<!-- Task count badge -->
				{#if totalTasks() > 0}
					<span
						class="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-0.5 rounded-full"
					>
						{completedTasks()}/{totalTasks()}
					</span>
				{/if}
			</div>

			<!-- Project description -->
			{#if project.description}
				<p class="text-xs text-gray-500 mt-1 truncate">
					{project.description}
				</p>
			{/if}

			<!-- Progress bar -->
			{#if totalTasks() > 0}
				<div class="mt-2">
					<div class="flex items-center justify-between text-xs text-gray-500 mb-1">
						<span>Progress</span>
						<span>{progressPercent()}%</span>
					</div>
					<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
						<div
							class="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
							style="width: {progressPercent()}%"
						></div>
					</div>
				</div>
			{/if}
		</div>

		<!-- Add task button -->
		<Button variant="ghost" size="icon" class="h-6 w-6 p-0 shrink-0" onclick={handleAddTask}>
			<Plus class="h-4 w-4" />
		</Button>
	</div>

	<!-- Project tasks -->
	{#if expanded}
		{#if project.tasks.length === 0}
			<div class="p-4 text-center text-gray-500 text-sm">No tasks yet. Click + to add one.</div>
		{:else}
			{#each project.tasks as task (task.id)}
				<TaskItem {task} onSelect={onSelectTask} />
			{/each}
		{/if}
	{/if}
</div>
