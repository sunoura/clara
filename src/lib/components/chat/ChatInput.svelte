<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { sendMessage, chatState } from '$lib/state/chatState.svelte.js';

	let textareaElement: HTMLTextAreaElement;

	async function handleSubmit() {
		const content = chatState.inputValue.trim();
		if (!content || chatState.isLoading) return;

		await sendMessage(content);

		// Reset textarea height
		if (textareaElement) {
			textareaElement.style.height = 'auto';
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSubmit();
		}
	}

	function adjustTextareaHeight() {
		if (textareaElement) {
			textareaElement.style.height = 'auto';
			textareaElement.style.height = Math.min(textareaElement.scrollHeight, 200) + 'px';
		}
	}

	$effect(() => {
		adjustTextareaHeight();
	});
</script>

<div class="border-t bg-white p-4">
	<form
		onsubmit={(e) => {
			e.preventDefault();
			handleSubmit();
		}}
		class="flex gap-2"
	>
		<div class="flex-1">
			<textarea
				bind:this={textareaElement}
				bind:value={chatState.inputValue}
				placeholder="Type your message..."
				disabled={chatState.isLoading}
				rows={1}
				class="flex min-h-[40px] w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
				onkeydown={handleKeydown}
			></textarea>
		</div>
		<Button
			type="submit"
			disabled={!chatState.inputValue.trim() || chatState.isLoading}
			size="icon"
			class="h-10 w-10 shrink-0"
		>
			{#if chatState.isLoading}
				⏳
			{:else}
				→
			{/if}
		</Button>
	</form>
</div>
