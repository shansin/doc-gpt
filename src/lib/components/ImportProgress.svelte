<script lang="ts">
  import { importProgress, importErrors, clearImportErrors, type ImportError } from "$lib/stores/documents";

  let progress: { type: string; filename: string; step: string; current: number; total: number } | null =
    $state(null);
  let errors: ImportError[] = $state([]);

  importProgress.subscribe((v) => (progress = v));
  importErrors.subscribe((v) => (errors = v));

  function getPct(p: typeof progress): number {
    if (!p || p.total <= 0) return 0;
    return Math.round((p.current / p.total) * 100);
  }
</script>

{#if progress}
  <div class="import-progress">
    <div class="progress-header">
      <span class="progress-count">{progress.current} / {progress.total}</span>
      <span class="progress-pct">{getPct(progress)}%</span>
    </div>
    <div class="progress-bar">
      <div
        class="progress-fill"
        style="width: {getPct(progress)}%"
      ></div>
    </div>
    <div class="progress-detail">
      <span class="filename" title={progress.filename}>
        {progress.filename.length > 28
          ? "..." + progress.filename.slice(-25)
          : progress.filename}
      </span>
      <span class="step" class:step-error={progress.type === "error"}>
        {progress.type === "error" ? "failed" : progress.step}
      </span>
    </div>
    {#if errors.length > 0}
      <div class="inline-errors">
        <span class="error-count">{errors.length} failed</span>
      </div>
    {/if}
  </div>
{/if}

{#if errors.length > 0 && !progress}
  <div class="error-summary">
    <div class="error-summary-header">
      <span>{errors.length} file{errors.length > 1 ? "s" : ""} failed</span>
      <button class="dismiss-btn" onclick={() => clearImportErrors()}>dismiss</button>
    </div>
    <div class="error-list">
      {#each errors as err}
        <div class="error-item" title={err.message}>
          <span class="error-filename">{err.filename}</span>
          <span class="error-message">{err.message.length > 50 ? err.message.slice(0, 47) + "..." : err.message}</span>
        </div>
      {/each}
    </div>
  </div>
{/if}

<style>
  .import-progress {
    padding: 10px 12px;
    background: var(--accent-subtle);
    border: 1px solid var(--accent-dim);
    border-radius: var(--radius-md);
    margin: 8px 0;
  }
  .progress-header {
    font-size: 12px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .progress-count {
    font-variant-numeric: tabular-nums;
  }
  .progress-pct {
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
    font-variant-numeric: tabular-nums;
  }
  .progress-bar {
    height: 4px;
    background: var(--hover-bg-stronger);
    border-radius: 2px;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 2px;
    transition: width 0.3s ease;
  }
  .progress-detail {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    font-size: 11px;
  }
  .filename {
    color: var(--subtext0);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 160px;
  }
  .step {
    color: var(--subtext0);
    font-style: italic;
    flex-shrink: 0;
  }
  .step-error {
    color: var(--red);
  }
  .inline-errors {
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid var(--hover-bg-stronger);
  }
  .error-count {
    font-size: 11px;
    font-weight: 500;
    color: var(--red);
  }
  .error-summary {
    padding: 10px 12px;
    background: rgba(243, 139, 168, 0.05);
    border: 1px solid rgba(243, 139, 168, 0.12);
    border-radius: var(--radius-md);
    margin: 8px 0;
  }
  .error-summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    font-weight: 600;
    color: var(--red);
    margin-bottom: 6px;
  }
  .dismiss-btn {
    background: none;
    border: none;
    color: var(--surface2);
    cursor: pointer;
    font-size: 11px;
    font-family: var(--font-sans);
    padding: 2px 6px;
    border-radius: 4px;
    transition: all var(--transition-fast);
  }
  .dismiss-btn:hover {
    color: var(--text);
    background: var(--hover-bg-stronger);
  }
  .error-list {
    max-height: 120px;
    overflow-y: auto;
  }
  .error-item {
    padding: 4px 0;
    font-size: 11px;
    border-bottom: 1px solid var(--hover-bg);
  }
  .error-item:last-child {
    border-bottom: none;
  }
  .error-filename {
    color: var(--text);
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .error-message {
    color: var(--surface2);
    font-size: 10px;
  }
</style>
