<script lang="ts">
  import { toasts, dismissToast, type ToastItem } from "$lib/stores/toast";

  let items: ToastItem[] = $state([]);
  toasts.subscribe((v) => (items = v));
</script>

{#if items.length > 0}
  <div class="toast-container">
    {#each items as toast (toast.id)}
      <div class="toast" class:success={toast.type === "success"} class:error={toast.type === "error"} class:info={toast.type === "info"}>
        <div class="toast-icon">
          {#if toast.type === "success"}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6L9 17l-5-5" />
            </svg>
          {:else if toast.type === "error"}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
          {:else}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
          {/if}
        </div>
        <span class="toast-message">{toast.message}</span>
        <button class="toast-dismiss" onclick={() => dismissToast(toast.id)} title="Dismiss">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .toast-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    display: flex;
    flex-direction: column-reverse;
    gap: 8px;
    z-index: 9999;
    pointer-events: none;
  }
  .toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-radius: var(--radius-md);
    background: var(--base);
    border: 1px solid var(--surface0);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    animation: slideIn 0.25s ease-out;
    pointer-events: auto;
    max-width: 400px;
  }
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(12px) scale(0.96); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }
  .toast.success .toast-icon { color: var(--green); }
  .toast.error .toast-icon { color: var(--red); }
  .toast.info .toast-icon { color: var(--blue); }
  .toast.success { border-color: rgba(166, 227, 161, 0.2); }
  .toast.error { border-color: rgba(243, 139, 168, 0.2); }
  .toast-icon {
    flex-shrink: 0;
    display: flex;
  }
  .toast-message {
    font-size: 13px;
    color: var(--text);
    line-height: 1.4;
  }
  .toast-dismiss {
    background: none;
    border: none;
    color: var(--overlay0);
    cursor: pointer;
    padding: 2px;
    border-radius: 4px;
    display: flex;
    flex-shrink: 0;
    transition: color var(--transition-fast);
  }
  .toast-dismiss:hover {
    color: var(--text);
  }
</style>
