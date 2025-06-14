<script lang="ts">
	import { Plus, RefreshCw, Briefcase } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { cn } from '$lib/utils.js';
	import {
		claraState,
		loadWorkspaces,
		selectWorkspace,
		createWorkspace,
		createProject,
		createTask,
		showCreateForm,
		hideCreateForm
	} from '$lib/state/claraState.svelte.js';
	import ProjectItem from './ProjectItem.svelte';
	import TaskItem from './TaskItem.svelte';
	import type { Task, Project, Workspace } from '$lib/types/clara';

	// Form states
	let workspaceTitle = $state('');
	let projectTitle = $state('');
	let projectDescription = $state('');
	let taskTitle = $state('');

	// Load workspaces on mount
	$effect(() => {
		loadWorkspaces();
	});

	async function handleCreateWorkspace() {
		if (!workspaceTitle.trim()) return;

		try {
			await createWorkspace({ title: workspaceTitle.trim() });
			workspaceTitle = '';
		} catch (error) {
			console.error('Failed to create workspace:', error);
		}
	}

	async function handleCreateProject() {
		if (!projectTitle.trim() || !claraState.selectedWorkspace) return;

		try {
			await createProject({
				title: projectTitle.trim(),
				description: projectDescription.trim() || undefined,
				workspace_id: claraState.selectedWorkspace.id
			});
			projectTitle = '';
			projectDescription = '';
		} catch (error) {
			console.error('Failed to create project:', error);
		}
	}

	async function handleCreateTask() {
		if (!taskTitle.trim() || !claraState.selectedWorkspace) return;

		try {
			await createTask({
				title: taskTitle.trim(),
				workspace_id: claraState.selectedWorkspace.id
			});
			taskTitle = '';
		} catch (error) {
			console.error('Failed to create task:', error);
		}
	}

	function handleSelectTask(task: Task) {
		// For mobile, we could show task details in a modal or navigate
		console.log('Selected task:', task);
	}

	function handleSelectProject(project: Project) {
		// For mobile, we could show project details in a modal or navigate
		console.log('Selected project:', project);
	}

	function handleRefresh() {
		loadWorkspaces();
	}
</script>

<div class="flex flex-col h-full">
	<!-- Header -->
	<div class="p-4 border-b bg-background flex items-center gap-2 justify-between">
		<div class="flex items-center gap-2">
			<Briefcase class="h-5 w-5 text-blue-500" />
			<span class="font-semibold text-sm">Clara Tasks</span>
		</div>
		<div class="flex items-center gap-1">
			<Button
				variant="ghost"
				size="icon"
				class="h-8 w-8"
				onclick={handleRefresh}
				disabled={claraState.isLoading}
			>
				<RefreshCw class={cn('h-4 w-4', claraState.isLoading && 'animate-spin')} />
			</Button>
			<Button variant="outline" size="sm" onclick={() => showCreateForm('workspace')}>
				<Plus class="h-3 w-3 mr-1" />
				New
			</Button>
		</div>
	</div>

	<!-- Workspace selector -->
	{#if claraState.workspaces.length > 1}
		<div class="p-3 border-b bg-muted/30">
			<div class="flex gap-1 overflow-x-auto">
				{#each claraState.workspaces as workspace (workspace.id)}
					<Button
						variant={claraState.selectedWorkspace?.id === workspace.id ? 'default' : 'outline'}
						size="sm"
						class="text-xs shrink-0"
						onclick={() => selectWorkspace(workspace)}
					>
						{workspace.title}
					</Button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Create forms -->
	{#if claraState.showCreateForm === 'workspace'}
		<div class="p-4 border-b bg-card">
			<h4 class="text-sm font-medium mb-2">New Workspace</h4>
			<Input bind:value={workspaceTitle} placeholder="Workspace name..." class="mb-2" />
			<div class="flex gap-2">
				<Button
					onclick={handleCreateWorkspace}
					size="sm"
					disabled={!workspaceTitle.trim() || claraState.isLoading}
				>
					Create
				</Button>
				<Button onclick={hideCreateForm} variant="outline" size="sm">Cancel</Button>
			</div>
		</div>
	{/if}

	{#if claraState.showCreateForm === 'project'}
		<div class="p-4 border-b bg-card">
			<h4 class="text-sm font-medium mb-2">New Project</h4>
			<Input bind:value={projectTitle} placeholder="Project name..." class="mb-2" />
			<Input bind:value={projectDescription} placeholder="Description (optional)..." class="mb-2" />
			<div class="flex gap-2">
				<Button
					onclick={handleCreateProject}
					size="sm"
					disabled={!projectTitle.trim() || claraState.isLoading}
				>
					Create
				</Button>
				<Button onclick={hideCreateForm} variant="outline" size="sm">Cancel</Button>
			</div>
		</div>
	{/if}

	{#if claraState.showCreateForm === 'task'}
		<div class="p-4 border-b bg-card">
			<h4 class="text-sm font-medium mb-2">New Task</h4>
			<Input bind:value={taskTitle} placeholder="Task title..." class="mb-2" />
			<div class="flex gap-2">
				<Button
					onclick={handleCreateTask}
					size="sm"
					disabled={!taskTitle.trim() || claraState.isLoading}
				>
					Create
				</Button>
				<Button onclick={hideCreateForm} variant="outline" size="sm">Cancel</Button>
			</div>
		</div>
	{/if}

	<!-- Content -->
	<div class="flex-1 overflow-y-auto">
		{#if claraState.isLoading && claraState.workspaces.length === 0}
			<div class="p-4 text-sm text-muted-foreground text-center">Loading workspaces...</div>
		{:else if claraState.workspaces.length === 0}
			<div class="p-4 text-center">
				<div class="text-sm text-muted-foreground mb-4">
					No workspaces yet. Create one to get started.
				</div>
				<Button onclick={() => showCreateForm('workspace')} size="sm">Create Workspace</Button>
			</div>
		{:else if claraState.selectedWorkspace}
			<!-- Quick actions -->
			<div class="p-3 border-b bg-muted/20 flex gap-2">
				<Button
					variant="outline"
					size="sm"
					class="flex-1 text-xs"
					onclick={() => showCreateForm('project')}
				>
					<Plus class="h-3 w-3 mr-1" />
					Project
				</Button>
				<Button
					variant="outline"
					size="sm"
					class="flex-1 text-xs"
					onclick={() => showCreateForm('task')}
				>
					<Plus class="h-3 w-3 mr-1" />
					Task
				</Button>
			</div>

			<!-- Projects -->
			{#if claraState.selectedWorkspace.projects.length > 0}
				{#each claraState.selectedWorkspace.projects as project (project.id)}
					<ProjectItem
						{project}
						onSelectTask={handleSelectTask}
						onSelectProject={handleSelectProject}
					/>
				{/each}
			{/if}

			<!-- Workspace-level tasks -->
			{#if claraState.selectedWorkspace.tasks.length > 0}
				<div class="border-b border-gray-200 dark:border-gray-700">
					<div class="p-3 bg-gray-50 dark:bg-gray-800/30">
						<span class="text-sm font-medium text-gray-700 dark:text-gray-300">Quick Tasks</span>
					</div>
					{#each claraState.selectedWorkspace.tasks as task (task.id)}
						<TaskItem {task} onSelect={handleSelectTask} />
					{/each}
				</div>
			{/if}

			<!-- Empty state -->
			{#if claraState.selectedWorkspace.projects.length === 0 && claraState.selectedWorkspace.tasks.length === 0}
				<div class="p-4 text-center text-gray-500">
					<p class="text-sm mb-4">No projects or tasks yet.</p>
					<div class="space-y-2">
						<Button
							onclick={() => showCreateForm('project')}
							variant="outline"
							size="sm"
							class="w-full"
						>
							Create Project
						</Button>
						<Button
							onclick={() => showCreateForm('task')}
							variant="outline"
							size="sm"
							class="w-full"
						>
							Add Quick Task
						</Button>
					</div>
				</div>
			{/if}
		{/if}
	</div>

	<!-- Error state -->
	{#if claraState.error}
		<div class="p-4 text-sm text-destructive border-t">
			Error: {claraState.error}
		</div>
	{/if}
</div>
