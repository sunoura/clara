<script lang="ts">
	import { cn } from '$lib/utils.js';
	import type { ChatMessage } from '$lib/state/chatState.svelte.js';

	interface Props {
		message: ChatMessage;
	}

	let { message }: Props = $props();

	const isUser = message.from === 'user';
	const hasError = !message.ok || !!message.err;
</script>

<div class={cn('flex gap-3 p-4', isUser ? 'justify-end' : 'justify-start')}>
	<div class={cn('flex max-w-[70%] gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
		<!-- Avatar -->
		<div
			class={cn(
				'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-medium',
				isUser ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
			)}
		>
			{#if isUser}
				U
			{:else}
				AI
			{/if}
		</div>

		<!-- Message bubble -->
		<div
			class={cn(
				'rounded-lg px-3 py-2 text-sm',
				isUser ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground',
				hasError && 'border border-destructive'
			)}
		>
			<div class="whitespace-pre-wrap break-words">
				{message.content}
			</div>

			{#if hasError && message.err}
				<div class="mt-2 flex items-center gap-1 text-xs text-destructive">
					⚠️ {message.err}
				</div>
			{/if}
		</div>
	</div>
</div>
