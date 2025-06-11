<script lang="ts">
	import { cn } from '$lib/utils.js';

	interface Props {
		value?: string;
		placeholder?: string;
		disabled?: boolean;
		readonly?: boolean;
		class?: string;
		type?: string;
	}

	let {
		value = $bindable(''),
		placeholder,
		disabled = false,
		readonly = false,
		type = 'text',
		class: className,
		...restProps
	}: Props = $props();
</script>

<input
	bind:value
	class={cn(
		'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
		className
	)}
	{type}
	{placeholder}
	{disabled}
	{readonly}
	{...restProps}
/>
