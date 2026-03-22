<script lang="ts">
  import {
    gpus,
    ollamaGpu,
    doclingGpu,
    gpuLoaded,
    loadGpuSettings,
    saveGpuSettings,
  } from "$lib/stores/gpu";
  import type { GpuInfo } from "$lib/api/backend";

  interface Props {
    onClose: () => void;
  }
  let { onClose }: Props = $props();

  let gpuList: GpuInfo[] = $state([]);
  let loaded = $state(false);
  let ollamaVal = $state(-1);
  let doclingVal = $state(-1);
  let saving = $state(false);

  gpus.subscribe((v) => (gpuList = v));
  gpuLoaded.subscribe((v) => (loaded = v));
  ollamaGpu.subscribe((v) => (ollamaVal = v));
  doclingGpu.subscribe((v) => (doclingVal = v));

  // Load on mount if not already loaded
  $effect(() => {
    if (!loaded) loadGpuSettings();
  });

  function onOllamaChange(e: Event) {
    ollamaVal = parseInt((e.target as HTMLSelectElement).value);
  }
  function onDoclingChange(e: Event) {
    doclingVal = parseInt((e.target as HTMLSelectElement).value);
  }

  async function handleSave() {
    saving = true;
    await saveGpuSettings(ollamaVal, doclingVal);
    saving = false;
    onClose();
  }

  function formatVram(mb: number): string {
    return mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${mb} MB`;
  }

  function usagePct(gpu: GpuInfo): number {
    return Math.round((gpu.vram_used_mb / gpu.vram_total_mb) * 100);
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="overlay" role="dialog" aria-modal="true" tabindex="-1"
  onclick={onClose}
  onkeydown={(e) => { if (e.key === 'Escape') onClose(); }}>
  <!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
  <div class="dialog" onclick={(e) => e.stopPropagation()}>
    <div class="dialog-header">
      <h2>GPU Configuration</h2>
      <button class="close-btn" onclick={onClose} title="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>

    {#if !loaded}
      <div class="loading">Loading GPU info...</div>
    {:else if gpuList.length === 0}
      <div class="no-gpus">
        <p>No GPUs detected. Document conversion and inference will run on CPU.</p>
      </div>
    {:else}
      <div class="gpu-cards">
        {#each gpuList as gpu}
          <div class="gpu-card">
            <div class="gpu-header">
              <span class="gpu-index">GPU {gpu.index}</span>
              <span class="gpu-name">{gpu.name}</span>
            </div>
            <div class="gpu-vram">
              <div class="vram-bar">
                <div class="vram-fill" style="width: {usagePct(gpu)}%"></div>
              </div>
              <div class="vram-labels">
                <span>{formatVram(gpu.vram_used_mb)} used</span>
                <span>{formatVram(gpu.vram_total_mb)} total</span>
              </div>
            </div>
          </div>
        {/each}
      </div>

      <div class="assignments">
        <div class="assign-row">
          <div class="assign-info">
            <span class="assign-label">Ollama</span>
            <span class="assign-desc">Chat inference & embeddings</span>
          </div>
          <select value={ollamaVal} onchange={onOllamaChange}>
            <option value={-1}>Auto (all GPUs)</option>
            {#each gpuList as gpu}
              <option value={gpu.index}>GPU {gpu.index} - {gpu.name}</option>
            {/each}
          </select>
        </div>

        <div class="assign-row">
          <div class="assign-info">
            <span class="assign-label">Docling / RapidOCR</span>
            <span class="assign-desc">Document conversion & OCR</span>
          </div>
          <select value={doclingVal} onchange={onDoclingChange}>
            <option value={-1}>Auto (GPU 0)</option>
            {#each gpuList as gpu}
              <option value={gpu.index}>GPU {gpu.index} - {gpu.name}</option>
            {/each}
          </select>
        </div>
      </div>

      {#if ollamaVal >= 0 && doclingVal >= 0 && ollamaVal === doclingVal}
        <div class="warning">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <span>Both services on the same GPU may cause out-of-memory errors during import</span>
        </div>
      {/if}

      <div class="hint">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <span>Ollama GPU changes apply immediately. Docling GPU changes require a restart.</span>
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
    max-width: 480px;
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
  .loading, .no-gpus {
    padding: 32px 20px;
    text-align: center;
    color: var(--overlay0);
    font-size: 14px;
  }

  /* GPU cards */
  .gpu-cards {
    padding: 16px 20px 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .gpu-card {
    padding: 12px 14px;
    background: var(--crust);
    border: 1px solid var(--surface0);
    border-radius: var(--radius-md);
  }
  .gpu-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }
  .gpu-index {
    font-size: 10px;
    font-weight: 700;
    color: var(--accent);
    background: var(--accent-subtle);
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .gpu-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text);
  }
  .vram-bar {
    height: 6px;
    background: var(--surface0);
    border-radius: 3px;
    overflow: hidden;
  }
  .vram-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 3px;
    transition: width 0.3s ease;
  }
  .vram-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    font-size: 11px;
    color: var(--overlay0);
  }

  /* Assignments */
  .assignments {
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .assign-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .assign-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }
  .assign-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
  }
  .assign-desc {
    font-size: 11px;
    color: var(--overlay0);
  }
  .assign-row select {
    padding: 6px 10px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--surface0);
    background: var(--crust);
    color: var(--text);
    font-size: 12px;
    font-family: var(--font-sans);
    cursor: pointer;
    transition: border-color var(--transition-fast);
    flex-shrink: 0;
  }
  .assign-row select:hover {
    border-color: var(--surface1);
  }
  .assign-row select:focus {
    outline: none;
    border-color: var(--accent);
  }

  /* Warning */
  .warning {
    margin: 0 20px;
    padding: 10px 14px;
    background: rgba(243, 139, 168, 0.08);
    border: 1px solid rgba(243, 139, 168, 0.15);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12px;
    color: var(--red);
    line-height: 1.4;
  }
  .warning svg {
    flex-shrink: 0;
    margin-top: 1px;
  }

  /* Hint */
  .hint {
    margin: 12px 20px 0;
    padding: 10px 14px;
    background: var(--accent-subtle);
    border: 1px solid var(--accent-dim);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 11px;
    color: var(--overlay0);
    line-height: 1.4;
  }
  .hint svg {
    flex-shrink: 0;
    margin-top: 1px;
    color: var(--accent);
  }

  /* Actions */
  .dialog-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 16px 20px;
    border-top: 1px solid var(--surface0);
    margin-top: 16px;
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
