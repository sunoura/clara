<script lang="ts">
	import { Check, ChevronRight, ChevronDown, Circle, Clock } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { cn } from '$lib/utils.js';
	import { completeTask } from '$lib/state/claraState.svelte.js';
	import type { Task } from '$lib/types/clara';

	interface Props {
		task: Task;
		level?: number;
		onSelect?: (task: Task) => void;
	}

	let { task, level = 0, onSelect }: Props = $props();

	let expanded = $state(false);
	let isCompleting = $state(false);

	const statusColors = {
		todo: 'text-gray-500',
		'in-progress': 'text-blue-500',
		done: 'text-green-500',
		archived: 'text-gray-400'
	};

	const statusIcons = {
		todo: Circle,
		'in-progress': Clock,
		done: Check,
		archived: Circle
	};

	function getStatusIcon(status: string) {
		return statusIcons[status as keyof typeof statusIcons] || Circle;
	}

	function formatDueDate(dateStr: string) {
		const date = new Date(dateStr);
		const now = new Date();
		const diffTime = date.getTime() - now.getTime();
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

		if (diffDays === 0) return 'Today';
		if (diffDays === 1) return 'Tomorrow';
		if (diffDays === -1) return 'Yesterday';
		if (diffDays > 0) return `${diffDays}d`;
		return `${Math.abs(diffDays)}d ago`;
	}

	async function handleComplete() {
		if (task.status === 'done' || isCompleting) return;

		isCompleting = true;
		try {
			await completeTask(task.id);
		} catch (error) {
			console.error('Failed to complete task:', error);
		} finally {
			isCompleting = false;
		}
	}

	function handleClick() {
		if (onSelect) {
			onSelect(task);
		}
	}

	function toggleExpanded() {
		expanded = !expanded;
	}
</script>

<div class="border-b border-gray-100 dark:border-gray-800" style="padding-left: {level * 16}px">
	<!-- Main task row -->
	<div
		class="flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 active:bg-gray-100 dark:active:bg-gray-700 transition-colors"
	>
		<!-- Expand/collapse button for subtasks -->
		{#if task.subtasks.length > 0}
			<Button variant="ghost" size="icon" class="h-6 w-6 p-0 shrink-0" onclick={toggleExpanded}>
				{#if expanded}
					<ChevronDown class="h-4 w-4" />
				{:else}
					<ChevronRight class="h-4 w-4" />
				{/if}
			</Button>
		{:else}
			<div class="w-6 h-6 shrink-0"></div>
		{/if}

		<!-- Status icon/complete button -->
		<Button
			variant="ghost"
			size="icon"
			class="h-6 w-6 p-0 shrink-0 {statusColors[task.status]}"
			onclick={handleComplete}
			disabled={isCompleting || task.status === 'done'}
		>
			{#if isCompleting}
				<div
					class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
				></div>
			{:else}
				<svelte:component this={getStatusIcon(task.status)} class="h-4 w-4" />
			{/if}
		</Button>

		<!-- Task content -->
		<div class="flex-1 min-w-0" role="button" tabindex="0" onclick={handleClick}>
			<div class="flex items-center gap-2">
				<span
					class={cn('text-sm font-medium', task.status === 'done' && 'line-through text-gray-500')}
				>
					{task.title}
				</span>

				<!-- Task count badge -->
				{#if task.subtasks.length > 0}
					<span class="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded-full">
						{task.subtasks.filter((t) => t.status === 'done').length}/{task.subtasks.length}
					</span>
				{/if}
			</div>

			<!-- Due date -->
			{#if task.due_date}
				<div class="flex items-center gap-1 mt-1">
					<Clock class="h-3 w-3 text-gray-400" />
					<span
						class={cn(
							'text-xs',
							new Date(task.due_date) < new Date() && task.status !== 'done'
								? 'text-red-500'
								: 'text-gray-500'
						)}
					>
						{formatDueDate(task.due_date)}
					</span>
				</div>
			{/if}
		</div>
	</div>

	<!-- Subtasks -->
	{#if expanded && task.subtasks.length > 0}
		{#each task.subtasks as subtask (subtask.id)}
			<svelte:self task={subtask} level={level + 1} {onSelect} />
		{/each}
	{/if}
</div>
