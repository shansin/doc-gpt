<script lang="ts">
  import { chatModel, embedModel, availableModels } from "$lib/stores/settings";

  let models: { name: string; size: number }[] = $state([]);
  let chatValue = $state("");
  let embedValue = $state("");

  availableModels.subscribe((v) => (models = v));
  chatModel.subscribe((v) => (chatValue = v));
  embedModel.subscribe((v) => (embedValue = v));

  let chatModels = $derived(models.filter((m) => !m.name.includes("embed")));
  let embedModels = $derived(models.filter((m) => m.name.includes("embed")));

  function onChatChange(e: Event) {
    chatModel.set((e.target as HTMLSelectElement).value);
  }

  function onEmbedChange(e: Event) {
    embedModel.set((e.target as HTMLSelectElement).value);
  }

  function formatSize(bytes: number): string {
    const gb = bytes / 1e9;
    return gb >= 1 ? `${gb.toFixed(1)}GB` : `${(bytes / 1e6).toFixed(0)}MB`;
  }
</script>

<div class="model-selector">
  <label>
    <span class="label-text">Chat</span>
    <select value={chatValue} onchange={onChatChange}>
      {#each chatModels as model}
        <option value={model.name} selected={model.name === chatValue}>
          {model.name} ({formatSize(model.size)})
        </option>
      {/each}
      {#if chatModels.length === 0}
        <option value={chatValue}>{chatValue}</option>
      {/if}
    </select>
  </label>
  <label>
    <span class="label-text">Embed</span>
    <select value={embedValue} onchange={onEmbedChange}>
      {#each embedModels as model}
        <option value={model.name} selected={model.name === embedValue}>
          {model.name} ({formatSize(model.size)})
        </option>
      {/each}
      {#if embedModels.length === 0}
        <option value={embedValue}>{embedValue}</option>
      {/if}
    </select>
  </label>
</div>

<style>
  .model-selector {
    display: flex;
    gap: 16px;
    align-items: center;
  }
  label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--subtext0);
  }
  .label-text {
    font-weight: 600;
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 0.6px;
    color: var(--overlay0);
  }
  select {
    padding: 5px 10px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--surface0);
    background: var(--crust);
    color: var(--text);
    font-size: 12px;
    font-family: var(--font-sans);
    cursor: pointer;
    transition: border-color var(--transition-fast);
  }
  select:hover {
    border-color: var(--surface1);
  }
  select:focus {
    outline: none;
    border-color: var(--accent);
  }
</style>
