<script lang="ts">
  import { open } from "@tauri-apps/plugin-dialog";
  import {
    documents,
    importing,
    importErrors,
    loadDocuments,
    removeDocument,
    removeAllDocuments,
    startIngest,
    cancelIngest,
    type ImportError,
  } from "$lib/stores/documents";
  import ImportProgress from "./ImportProgress.svelte";
  import type { DocumentInfo } from "$lib/api/backend";

  interface Props {
    open: boolean;
    onToggle: () => void;
  }
  let { open: isOpen, onToggle }: Props = $props();

  let docList: DocumentInfo[] = $state([]);
  let isImporting = $state(false);
  let errors: ImportError[] = $state([]);
  let searchQuery = $state("");
  let showClearConfirm = $state(false);

  documents.subscribe((v) => (docList = v));
  importing.subscribe((v) => (isImporting = v));
  importErrors.subscribe((v) => (errors = v));

  let filteredDocs = $derived(
    searchQuery.trim()
      ? docList.filter((d) =>
          d.filename.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : docList
  );

  async function handleImport() {
    const selected = await open({ directory: true, multiple: false });
    if (selected) {
      startIngest(selected as string);
    }
  }

  function handleClearAll() {
    if (docList.length > 5) {
      showClearConfirm = true;
    } else {
      removeAllDocuments();
    }
  }

  function confirmClearAll() {
    removeAllDocuments();
    showClearConfirm = false;
  }

  function getFileIcon(filename: string): string {
    const ext = filename.split(".").pop()?.toLowerCase() || "";
    if (["pdf"].includes(ext)) return "PDF";
    if (["doc", "docx"].includes(ext)) return "DOC";
    if (["xls", "xlsx"].includes(ext)) return "XLS";
    if (["ppt", "pptx"].includes(ext)) return "PPT";
    if (["png", "jpg", "jpeg", "tiff", "bmp"].includes(ext)) return "IMG";
    if (["md"].includes(ext)) return "MD";
    if (["txt"].includes(ext)) return "TXT";
    if (["html"].includes(ext)) return "HTM";
    return "DOC";
  }

  function getIconColor(tag: string): string {
    const colors: Record<string, string> = {
      PDF: "var(--red)",
      DOC: "var(--blue)",
      XLS: "var(--green)",
      PPT: "var(--peach)",
      IMG: "var(--mauve)",
      MD: "var(--subtext0)",
      TXT: "var(--subtext0)",
      HTM: "var(--yellow)",
    };
    return colors[tag] || "var(--subtext0)";
  }
</script>

<aside class="sidebar" class:collapsed={!isOpen}>
  <div class="sidebar-header">
    <div class="brand">
      <div class="brand-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
      </div>
      <span class="brand-text">Documents</span>
    </div>
    <button class="collapse-btn" onclick={onToggle} title="Toggle sidebar (Ctrl+B)">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <line x1="9" y1="3" x2="9" y2="21" />
      </svg>
    </button>
  </div>

  <div class="sidebar-actions">
    {#if isImporting}
      <div class="import-btn-group">
        <button class="import-btn importing" disabled>
          <span class="spinner"></span>
          Importing...
        </button>
        <button class="cancel-import-btn" onclick={cancelIngest} title="Cancel import">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    {:else}
      <button class="import-btn" onclick={handleImport}>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
          <line x1="12" y1="11" x2="12" y2="17" />
          <line x1="9" y1="14" x2="15" y2="14" />
        </svg>
        Import Folder
      </button>
    {/if}
  </div>

  {#if isImporting || errors.length > 0}
    <div class="progress-section">
      <ImportProgress />
    </div>
  {/if}

  {#if docList.length > 3}
    <div class="search-section">
      <div class="search-box">
        <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          class="search-input"
          placeholder="Filter documents..."
          bind:value={searchQuery}
        />
        {#if searchQuery}
          <button class="search-clear" onclick={() => (searchQuery = "")} title="Clear search">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        {/if}
      </div>
    </div>
  {/if}

  <div class="doc-list">
    {#if docList.length === 0 && !isImporting}
      <div class="empty">
        <div class="empty-icon-wrap">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <p class="empty-title">No documents yet</p>
        <span class="empty-sub">Import a folder to get started</span>
      </div>
    {:else}
      {#if docList.length > 0}
        <div class="list-header">
          <span class="list-count">
            {#if searchQuery && filteredDocs.length !== docList.length}
              {filteredDocs.length} of {docList.length} files
            {:else}
              {docList.length} file{docList.length !== 1 ? "s" : ""}
            {/if}
          </span>
          <button
            class="clear-all-btn"
            onclick={handleClearAll}
            disabled={isImporting}
          >
            Clear All
          </button>
        </div>
      {/if}
      {#each filteredDocs as doc}
        {@const tag = getFileIcon(doc.filename)}
        <div class="doc-item">
          <div class="file-badge" style="color: {getIconColor(tag)}">
            {tag}
          </div>
          <div class="doc-info">
            <span class="doc-name" title={doc.filename}>{doc.filename}</span>
            <span class="doc-meta">{doc.chunk_count} chunk{doc.chunk_count !== 1 ? "s" : ""}</span>
          </div>
          <button
            class="delete-btn"
            onclick={() => removeDocument(doc.id)}
            title="Remove document"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      {/each}
      {#if searchQuery && filteredDocs.length === 0}
        <div class="empty no-results">
          <span class="empty-sub">No matching documents</span>
        </div>
      {/if}
    {/if}
  </div>
</aside>

{#if showClearConfirm}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="confirm-overlay" role="dialog" aria-modal="true" tabindex="-1"
    onclick={() => (showClearConfirm = false)}
    onkeydown={(e) => { if (e.key === 'Escape') showClearConfirm = false; }}>
    <!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
    <div class="confirm-dialog" onclick={(e) => e.stopPropagation()}>
      <p class="confirm-title">Remove all documents?</p>
      <p class="confirm-sub">This will delete {docList.length} documents and their embeddings from the vector store.</p>
      <div class="confirm-actions">
        <button class="confirm-cancel" onclick={() => (showClearConfirm = false)}>Cancel</button>
        <button class="confirm-delete" onclick={confirmClearAll}>Remove All</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .sidebar {
    width: var(--sidebar-width);
    min-width: var(--sidebar-width);
    background: var(--base);
    color: var(--text);
    display: flex;
    flex-direction: column;
    height: 100vh;
    border-right: 1px solid var(--surface0);
    transition: width var(--transition-slow), min-width var(--transition-slow), opacity var(--transition-slow);
    overflow: hidden;
  }
  .sidebar.collapsed {
    width: 0;
    min-width: 0;
    border-right: none;
    opacity: 0;
    pointer-events: none;
  }
  .sidebar-header {
    padding: 14px 16px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--surface0);
    min-height: var(--header-height);
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .brand-icon {
    width: 30px;
    height: 30px;
    border-radius: var(--radius-sm);
    background: var(--accent-dim);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .brand-text {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.2px;
  }
  .collapse-btn {
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
  .collapse-btn:hover {
    color: var(--text);
    background: var(--hover-bg-stronger);
  }
  .sidebar-actions {
    padding: 12px 14px;
  }
  .import-btn-group {
    display: flex;
    gap: 6px;
  }
  .import-btn {
    width: 100%;
    padding: 10px 14px;
    background: var(--accent);
    color: var(--accent-fg);
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-size: 13px;
    font-weight: 550;
    font-family: var(--font-sans);
    transition: all var(--transition-normal);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  .import-btn:hover:not(:disabled) {
    background: var(--accent-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(124, 111, 224, 0.25);
  }
  .import-btn:active:not(:disabled) {
    transform: translateY(0);
  }
  .import-btn:disabled,
  .import-btn.importing {
    opacity: 0.65;
    cursor: not-allowed;
    flex: 1;
  }
  .cancel-import-btn {
    padding: 0 12px;
    background: var(--red-dim);
    border: 1px solid rgba(243, 139, 168, 0.2);
    border-radius: var(--radius-md);
    color: var(--red);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }
  .cancel-import-btn:hover {
    background: var(--red);
    color: white;
    border-color: var(--red);
  }
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: var(--accent-fg);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .progress-section {
    padding: 0 12px;
  }
  .search-section {
    padding: 0 14px 6px;
  }
  .search-box {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 10px;
    background: var(--crust);
    border: 1px solid var(--surface0);
    border-radius: var(--radius-sm);
    transition: border-color var(--transition-fast);
  }
  .search-box:focus-within {
    border-color: var(--accent);
  }
  .search-icon {
    color: var(--overlay0);
    flex-shrink: 0;
  }
  .search-input {
    flex: 1;
    background: none;
    border: none;
    outline: none;
    color: var(--text);
    font-size: 12px;
    font-family: var(--font-sans);
    padding: 0;
    min-width: 0;
  }
  .search-input::placeholder {
    color: var(--surface2);
  }
  .search-clear {
    background: none;
    border: none;
    color: var(--overlay0);
    cursor: pointer;
    padding: 2px;
    display: flex;
    align-items: center;
    border-radius: 3px;
    transition: color var(--transition-fast);
  }
  .search-clear:hover {
    color: var(--text);
  }
  .doc-list {
    flex: 1;
    overflow-y: auto;
    padding: 4px 8px 8px;
  }
  .empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    color: var(--surface2);
    padding: 36px 16px 24px;
  }
  .empty.no-results {
    padding: 20px 16px;
  }
  .empty-icon-wrap {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: var(--hover-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
    color: var(--overlay0);
  }
  .empty-title {
    font-size: 13px;
    font-weight: 500;
    margin: 0 0 4px;
    color: var(--overlay0);
  }
  .empty-sub {
    font-size: 12px;
    color: var(--surface2);
  }
  .list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px 8px;
  }
  .list-count {
    font-size: 11px;
    color: var(--surface2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }
  .clear-all-btn {
    background: none;
    border: none;
    color: var(--surface2);
    cursor: pointer;
    font-size: 11px;
    font-family: var(--font-sans);
    padding: 2px 8px;
    border-radius: 4px;
    transition: all var(--transition-fast);
  }
  .clear-all-btn:hover:not(:disabled) {
    color: var(--red);
    background: var(--red-dim);
  }
  .clear-all-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .doc-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 8px;
    border-radius: var(--radius-sm);
    margin-bottom: 1px;
    transition: background var(--transition-fast);
  }
  .doc-item:hover {
    background: var(--hover-bg);
  }
  .doc-item:hover .delete-btn {
    opacity: 1;
  }
  .file-badge {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.3px;
    background: var(--hover-bg);
    padding: 3px 5px;
    border-radius: 4px;
    flex-shrink: 0;
    min-width: 28px;
    text-align: center;
  }
  .doc-info {
    flex: 1;
    min-width: 0;
  }
  .doc-name {
    display: block;
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text);
  }
  .doc-meta {
    font-size: 11px;
    color: var(--surface2);
  }
  .delete-btn {
    background: none;
    border: none;
    color: var(--surface2);
    cursor: pointer;
    padding: 4px;
    border-radius: var(--radius-sm);
    line-height: 1;
    transition: all var(--transition-fast);
    opacity: 0;
    flex-shrink: 0;
  }
  .delete-btn:hover {
    background: var(--red-dim);
    color: var(--red);
  }

  /* Confirmation dialog */
  .confirm-overlay {
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
  .confirm-dialog {
    background: var(--base);
    border: 1px solid var(--surface0);
    border-radius: var(--radius-lg);
    padding: 24px;
    max-width: 360px;
    width: 90%;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
  }
  .confirm-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 6px;
  }
  .confirm-sub {
    font-size: 13px;
    color: var(--overlay0);
    margin: 0 0 20px;
    line-height: 1.5;
  }
  .confirm-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
  .confirm-cancel {
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
  .confirm-cancel:hover {
    background: var(--surface1);
  }
  .confirm-delete {
    padding: 8px 16px;
    background: var(--red);
    border: none;
    border-radius: var(--radius-sm);
    color: white;
    font-size: 13px;
    font-family: var(--font-sans);
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
  }
  .confirm-delete:hover {
    filter: brightness(1.1);
  }
</style>
