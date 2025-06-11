<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import ChatMessage from './ChatMessage.svelte';
	import ChatInput from './ChatInput.svelte';
	import { Trash2 } from 'lucide-svelte';
	import {
		chatState,
		createSession,
		loadRecentSessions,
		startNewSession,
		loadSession
	} from '$lib/state/chatState.svelte.js';
	import { cn } from '$lib/utils.js';

	let messagesContainer: HTMLDivElement | null = $state(null);
	let showNewSessionForm = $state(false);
	let newSessionTitle = $state('');

	// Auto-scroll to bottom when new messages arrive
	$effect(() => {
		if (messagesContainer && chatState.messages.length > 0) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	});

	// Load recent sessions on mount
	$effect(() => {
		loadRecentSessions();
	});

	async function handleNewSession() {
		if (!newSessionTitle.trim()) return;

		await createSession(newSessionTitle.trim());
		newSessionTitle = '';
		showNewSessionForm = false;
	}

	function handleStartNewSession() {
		startNewSession();
		showNewSessionForm = true;
	}

	async function handleLoadSession(sessionId: string) {
		await loadSession(sessionId);
		showNewSessionForm = false;
	}

	async function handleDeleteSession() {
		if (!chatState.currentSession) return;

		const confirmed = confirm(
			`Are you sure you want to delete "${chatState.currentSession.title}"?`
		);
		if (!confirmed) return;

		try {
			chatState.isLoading = true;
			chatState.error = null;

			const response = await fetch(`/api/interaction-sessions/${chatState.currentSession.id}`, {
				method: 'DELETE'
			});

			if (!response.ok) {
				throw new Error('Failed to delete session');
			}

			// Remove from local state
			chatState.sessions = chatState.sessions.filter(
				(session) => session.id !== chatState.currentSession?.id
			);

			// Clear current session and messages
			chatState.currentSession = null;
			chatState.messages = [];
		} catch (error) {
			chatState.error = error instanceof Error ? error.message : 'Failed to delete session';
		} finally {
			chatState.isLoading = false;
		}
	}
</script>

<div class="flex h-screen bg-white">
	<!-- Sidebar -->
	<div class="w-80 border-r bg-zinc-50 flex flex-col">
		<!-- Header -->
		<div class="p-4 border-b">
			<h1 class="text-lg font-semibold text-zinc-900">Chat Sessions</h1>
			<Button onclick={handleStartNewSession} variant="outline" class="w-full mt-2">
				+ New Chat
			</Button>
		</div>

		<!-- New session form -->
		{#if showNewSessionForm}
			<div class="p-4 border-b bg-white">
				<Input bind:value={newSessionTitle} placeholder="Session title..." class="mb-2" />
				<div class="flex gap-2">
					<Button onclick={handleNewSession} size="sm" disabled={!newSessionTitle.trim()}>
						Create
					</Button>
					<Button onclick={() => (showNewSessionForm = false)} variant="outline" size="sm">
						Cancel
					</Button>
				</div>
			</div>
		{/if}

		<!-- Sessions list -->
		<div class="flex-1 overflow-y-auto">
			{#if chatState.sessions.length === 0}
				<div class="p-4 text-sm text-zinc-500">No sessions yet. Create one to start chatting.</div>
			{:else}
				{#each chatState.sessions as session (session.id)}
					<button
						class={cn(
							'w-full text-left p-3 border-b hover:bg-white transition-colors',
							chatState.currentSession?.id === session.id && 'bg-white border-l-2 border-l-zinc-900'
						)}
						onclick={() => handleLoadSession(session.id)}
					>
						<div class="font-medium text-sm text-zinc-900 truncate">
							{session.title}
						</div>
						<div class="text-xs text-zinc-500 mt-1">
							{new Date(session.started_at).toLocaleDateString()}
						</div>
					</button>
				{/each}
			{/if}
		</div>

		<!-- Loading/Error state -->
		{#if chatState.isLoading}
			<div class="p-4 text-sm text-zinc-500">Loading...</div>
		{/if}

		{#if chatState.error}
			<div class="p-4 text-sm text-red-500">
				Error: {chatState.error}
			</div>
		{/if}
	</div>

	<!-- Main chat area -->
	<div class="flex-1 flex flex-col">
		{#if chatState.currentSession}
			<!-- Chat header -->
			<div class="p-4 border-b bg-white flex items-center justify-between">
				<div class="flex-1">
					<h2 class="font-semibold text-zinc-900">
						{chatState.currentSession.title}
					</h2>
					{#if chatState.currentSession.context_summary}
						<p class="text-sm text-zinc-500 mt-1">
							{chatState.currentSession.context_summary}
						</p>
					{/if}
				</div>
				<Button
					onclick={handleDeleteSession}
					variant="ghost"
					size="icon"
					disabled={chatState.isLoading}
				>
					<Trash2 class="h-4 w-4" />
				</Button>
			</div>

			<!-- Messages -->
			<div bind:this={messagesContainer} class="flex-1 overflow-y-auto">
				{#if chatState.messages.length === 0}
					<div class="flex items-center justify-center h-full text-zinc-500">
						Start a conversation by typing a message below
					</div>
				{:else}
					{#each chatState.messages as message (message.id)}
						<ChatMessage {message} />
					{/each}
				{/if}
			</div>

			<!-- Chat input -->
			<ChatInput />
		{:else}
			<!-- Welcome screen -->
			<div class="flex-1 flex items-center justify-center">
				<div class="text-center">
					<h2 class="text-xl font-semibold text-zinc-900 mb-2">Welcome to Chat</h2>
					<p class="text-zinc-500 mb-4">
						Select a session from the sidebar or create a new one to start chatting
					</p>
					<Button onclick={handleStartNewSession}>Start New Chat</Button>
				</div>
			</div>
		{/if}
	</div>
</div>
