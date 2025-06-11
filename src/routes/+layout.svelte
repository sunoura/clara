<script lang="ts">
	import '../app.css';
	import { ModeWatcher } from 'mode-watcher';

	let { children } = $props();
</script>

<div class="h-screen w-screen relative">
	{@render children()}
	<ModeWatcher />
</div>
