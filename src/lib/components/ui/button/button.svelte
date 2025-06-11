<script lang="ts">
	import { buttonVariants, type Variant, type Size } from './index.js';
	import { cn } from '$lib/utils.js';
	import type { Snippet } from 'svelte';

	interface Props {
		variant?: Variant;
		size?: Size;
		class?: string;
		disabled?: boolean;
		type?: 'button' | 'submit' | 'reset';
		onclick?: (event: MouseEvent) => void;
		children: Snippet;
	}

	let {
		variant = 'default',
		size = 'default',
		class: className,
		disabled = false,
		type = 'button',
		onclick,
		children,
		...restProps
	}: Props = $props();
</script>

<button
	class={cn(buttonVariants({ variant, size }), className)}
	{disabled}
	{type}
	{onclick}
	{...restProps}
>
	{@render children()}
</button>
