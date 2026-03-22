<script lang="ts">
  import ModelSelector from "./ModelSelector.svelte";
  import GpuSettings from "./GpuSettings.svelte";
  import SystemPromptEditor from "./SystemPromptEditor.svelte";
  import { documents } from "$lib/stores/documents";
  import { theme, toggleTheme, type Theme } from "$lib/stores/theme";

  interface Props {
    sidebarOpen: boolean;
    onToggleSidebar: () => void;
  }
  let { sidebarOpen, onToggleSidebar }: Props = $props();

  let docCount = $state(0);
  let currentTheme: Theme = $state("dark");
  let showGpuSettings = $state(false);
  let showSystemPrompt = $state(false);
  documents.subscribe((v) => (docCount = v.length));
  theme.subscribe((v) => (currentTheme = v));
</script>

<div class="settings-panel">
  <div class="left">
    {#if !sidebarOpen}
      <button class="sidebar-toggle" onclick={onToggleSidebar} title="Show sidebar (Ctrl+B)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <line x1="9" y1="3" x2="9" y2="21" />
        </svg>
      </button>
      <div class="divider"></div>
    {/if}
    <div class="brand-inline">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <path d="M9 15l2 2 4-4" />
      </svg>
      <span class="brand-name">doc-gpt</span>
    </div>
  </div>

  <div class="center">
    <ModelSelector />
  </div>

  <div class="right">
    {#if docCount > 0}
      <div class="doc-badge">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
        {docCount} indexed
      </div>
    {/if}
    <button class="icon-btn" onclick={() => (showSystemPrompt = true)} title="System prompt">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    </button>
    <button class="icon-btn" onclick={() => (showGpuSettings = true)} title="GPU settings">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="4" y="4" width="16" height="16" rx="2" />
        <rect x="9" y="9" width="6" height="6" />
        <line x1="9" y1="1" x2="9" y2="4" />
        <line x1="15" y1="1" x2="15" y2="4" />
        <line x1="9" y1="20" x2="9" y2="23" />
        <line x1="15" y1="20" x2="15" y2="23" />
        <line x1="20" y1="9" x2="23" y2="9" />
        <line x1="20" y1="14" x2="23" y2="14" />
        <line x1="1" y1="9" x2="4" y2="9" />
        <line x1="1" y1="14" x2="4" y2="14" />
      </svg>
    </button>
    <button class="theme-toggle" onclick={toggleTheme} title="Switch to {currentTheme === 'dark' ? 'light' : 'dark'} mode">
      {#if currentTheme === "dark"}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      {:else}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      {/if}
    </button>
  </div>
</div>

{#if showGpuSettings}
  <GpuSettings onClose={() => (showGpuSettings = false)} />
{/if}

{#if showSystemPrompt}
  <SystemPromptEditor onClose={() => (showSystemPrompt = false)} />
{/if}

<style>
  .settings-panel {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    background: var(--base);
    border-bottom: 1px solid var(--surface0);
    min-height: var(--header-height);
    gap: 16px;
  }
  .left {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }
  .sidebar-toggle {
    background: none;
    border: none;
    color: var(--overlay0);
    cursor: pointer;
    padding: 6px;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .sidebar-toggle:hover {
    color: var(--text);
    background: var(--hover-bg-stronger);
  }
  .divider {
    width: 1px;
    height: 20px;
    background: var(--surface0);
  }
  .brand-inline {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .brand-name {
    font-size: 14px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.3px;
  }
  .center {
    flex: 1;
    display: flex;
    justify-content: center;
  }
  .right {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .doc-badge {
    font-size: 11px;
    color: var(--accent);
    background: var(--accent-subtle);
    padding: 5px 10px;
    border-radius: 12px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .icon-btn {
    background: none;
    border: 1px solid var(--surface0);
    color: var(--overlay1);
    cursor: pointer;
    padding: 6px;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .icon-btn:hover {
    color: var(--text);
    background: var(--hover-bg-stronger);
    border-color: var(--surface1);
  }
  .theme-toggle {
    background: none;
    border: 1px solid var(--surface0);
    color: var(--overlay1);
    cursor: pointer;
    padding: 6px;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .theme-toggle:hover {
    color: var(--text);
    background: var(--hover-bg-stronger);
    border-color: var(--surface1);
  }
</style>
