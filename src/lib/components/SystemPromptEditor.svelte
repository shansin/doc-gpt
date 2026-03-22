<script lang="ts">
  import {
    systemPrompt,
    isDefault,
    promptLoaded,
    loadSystemPrompt,
    saveSystemPrompt,
    resetToDefault,
  } from "$lib/stores/systemPrompt";

  interface Props {
    onClose: () => void;
  }
  let { onClose }: Props = $props();

  let draft = $state("");
  let loaded = $state(false);
  let isDefaultVal = $state(true);
  let saving = $state(false);
  let resetting = $state(false);

  systemPrompt.subscribe((v) => (draft = v));
  promptLoaded.subscribe((v) => (loaded = v));
  isDefault.subscribe((v) => (isDefaultVal = v));

  $effect(() => {
    if (!loaded) loadSystemPrompt();
  });

  async function handleSave() {
    saving = true;
    try {
      await saveSystemPrompt(draft);
      onClose();
    } catch (err) {
      console.error("Failed to save system prompt:", err);
    } finally {
      saving = false;
    }
  }

  async function handleReset() {
    resetting = true;
    try {
      await resetToDefault();
    } catch (err) {
      console.error("Failed to reset system prompt:", err);
    } finally {
      resetting = false;
    }
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="overlay" role="dialog" aria-modal="true" tabindex="-1"
  onclick={onClose}
  onkeydown={(e) => { if (e.key === 'Escape') onClose(); }}>
  <!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
  <div class="dialog" onclick={(e) => e.stopPropagation()}>
    <div class="dialog-header">
      <h2>System Prompt</h2>
      <button class="close-btn" onclick={onClose} title="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>

    {#if !loaded}
      <div class="loading">Loading...</div>
    {:else}
      <div class="editor-body">
        <p class="description">
          Customize the instructions given to the model when answering questions.
          The retrieved document context is appended automatically.
        </p>
        <textarea
          class="prompt-input"
          bind:value={draft}
          rows="12"
          spellcheck="false"
          placeholder="Enter system prompt..."
        ></textarea>

        {#if !isDefaultVal}
          <button class="reset-btn" onclick={handleReset} disabled={resetting}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="1 4 1 10 7 10" />
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
            </svg>
            {resetting ? "Resetting..." : "Reset to default"}
          </button>
        {/if}
      </div>

      <div class="dialog-actions">
        <button class="cancel-btn" onclick={onClose}>Cancel</button>
        <button class="save-btn" onclick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    animation: fadeIn 0.15s ease-out;
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  .dialog {
    background: var(--base);
    border: 1px solid var(--surface0);
    border-radius: var(--radius-lg);
    padding: 0;
    max-width: 600px;
    width: 90%;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
    overflow: hidden;
  }
  .dialog-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 20px 14px;
    border-bottom: 1px solid var(--surface0);
  }
  .dialog-header h2 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    margin: 0;
  }
  .close-btn {
    background: none;
    border: none;
    color: var(--overlay0);
    cursor: pointer;
    padding: 4px;
    border-radius: var(--radius-sm);
    display: flex;
    transition: all var(--transition-fast);
  }
  .close-btn:hover {
    color: var(--text);
    background: var(--hover-bg-stronger);
  }
  .loading {
    padding: 32px 20px;
    text-align: center;
    color: var(--overlay0);
    font-size: 14px;
  }
  .editor-body {
    padding: 16px 20px;
  }
  .description {
    font-size: 12px;
    color: var(--overlay0);
    margin: 0 0 12px;
    line-height: 1.5;
  }
  .prompt-input {
    width: 100%;
    padding: 12px;
    border: 1px solid var(--surface0);
    border-radius: var(--radius-md);
    background: var(--crust);
    color: var(--text);
    font-size: 13px;
    font-family: var(--font-mono, monospace);
    line-height: 1.6;
    resize: vertical;
    box-sizing: border-box;
    transition: border-color var(--transition-fast);
  }
  .prompt-input:focus {
    outline: none;
    border-color: var(--accent);
  }
  .prompt-input::placeholder {
    color: var(--overlay0);
  }
  .reset-btn {
    margin-top: 10px;
    padding: 6px 12px;
    background: none;
    border: 1px solid var(--surface0);
    border-radius: var(--radius-sm);
    color: var(--overlay1);
    font-size: 12px;
    font-family: var(--font-sans);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all var(--transition-fast);
  }
  .reset-btn:hover:not(:disabled) {
    color: var(--text);
    border-color: var(--surface1);
    background: var(--hover-bg-stronger);
  }
  .reset-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 16px 20px;
    border-top: 1px solid var(--surface0);
  }
  .cancel-btn {
    padding: 8px 16px;
    background: var(--surface0);
    border: none;
    border-radius: var(--radius-sm);
    color: var(--text);
    font-size: 13px;
    font-family: var(--font-sans);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
  }
  .cancel-btn:hover {
    background: var(--surface1);
  }
  .save-btn {
    padding: 8px 20px;
    background: var(--accent);
    border: none;
    border-radius: var(--radius-sm);
    color: var(--accent-fg);
    font-size: 13px;
    font-family: var(--font-sans);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
  }
  .save-btn:hover:not(:disabled) {
    background: var(--accent-hover);
  }
  .save-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
