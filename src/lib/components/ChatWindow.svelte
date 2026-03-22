<script lang="ts">
  import { messages, streaming, sendMessage, clearChat, stopGeneration, type Message } from "$lib/stores/chat";
  import { documents, startIngest } from "$lib/stores/documents";
  import MessageBubble from "./MessageBubble.svelte";

  let messageList: Message[] = $state([]);
  let isStreaming = $state(false);
  let inputText = $state("");
  let chatContainer: HTMLDivElement | undefined = $state();
  let textareaEl: HTMLTextAreaElement | undefined = $state();
  let docCount = $state(0);
  let showClearConfirm = $state(false);
  let dragOver = $state(false);

  messages.subscribe((v) => (messageList = v));
  streaming.subscribe((v) => (isStreaming = v));
  documents.subscribe((v) => (docCount = v.length));

  $effect(() => {
    if (messageList.length && chatContainer) {
      requestAnimationFrame(() => {
        chatContainer!.scrollTop = chatContainer!.scrollHeight;
      });
    }
  });

  function autoResize() {
    if (!textareaEl) return;
    textareaEl.style.height = "auto";
    textareaEl.style.height = Math.min(textareaEl.scrollHeight, 160) + "px";
  }

  function handleSubmit(e: Event) {
    e.preventDefault();
    const text = inputText.trim();
    if (!text || isStreaming) return;
    inputText = "";
    if (textareaEl) {
      textareaEl.style.height = "auto";
    }
    sendMessage(text);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  function handleClearChat() {
    if (messageList.length > 2) {
      showClearConfirm = true;
    } else {
      clearChat();
    }
  }

  function confirmClear() {
    clearChat();
    showClearConfirm = false;
  }

  // Drag & drop handling
  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    if (docCount === 0 && messageList.length === 0) {
      dragOver = true;
    }
  }
  function handleDragLeave(e: DragEvent) {
    // Only trigger if leaving the container (not entering a child)
    const rect = chatContainer?.getBoundingClientRect();
    if (rect && e.clientX >= rect.left && e.clientX <= rect.right &&
        e.clientY >= rect.top && e.clientY <= rect.bottom) return;
    dragOver = false;
  }
  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragOver = false;
    const items = e.dataTransfer?.items;
    if (items && items.length > 0) {
      const item = items[0];
      if (item.kind === "file") {
        const entry = item.webkitGetAsEntry?.();
        if (entry && entry.isDirectory) {
          // Tauri drag & drop provides file paths in dataTransfer
          const file = e.dataTransfer?.files[0];
          if (file && (file as any).path) {
            startIngest((file as any).path);
          }
        }
      }
    }
  }

  const suggestions = [
    "Summarize my most recent tax return",
    "What is my rental property address?",
    "Compare my W-2 income across years",
  ];

  function useSuggestion(text: string) {
    inputText = text;
    textareaEl?.focus();
  }
</script>

<div class="chat-window">
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="chat-messages" bind:this={chatContainer}
    ondragover={handleDragOver} ondragleave={handleDragLeave} ondrop={handleDrop}>
    {#if messageList.length === 0}
      <div class="empty-state" class:drag-over={dragOver}>
        {#if dragOver}
          <div class="drop-zone">
            <div class="drop-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                <line x1="12" y1="11" x2="12" y2="17" />
                <line x1="9" y1="14" x2="15" y2="14" />
              </svg>
            </div>
            <p class="drop-text">Drop folder to import</p>
          </div>
        {:else}
          <div class="empty-hero">
            <div class="empty-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <h1 class="empty-title">Chat with your documents</h1>
            <p class="empty-sub">Ask questions about your imported files and get AI-powered answers with source references.</p>
          </div>

          {#if docCount === 0}
            <div class="empty-cta">
              <div class="cta-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                  <line x1="12" y1="11" x2="12" y2="17" />
                  <line x1="9" y1="14" x2="15" y2="14" />
                </svg>
              </div>
              <span>Import a folder from the sidebar to get started</span>
            </div>
          {:else}
            <div class="suggestions">
              <p class="suggestions-label">Try asking</p>
              <div class="suggestion-list">
                {#each suggestions as suggestion}
                  <button class="suggestion-chip" onclick={() => useSuggestion(suggestion)}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="9 18 15 12 9 6" />
                    </svg>
                    {suggestion}
                  </button>
                {/each}
              </div>
            </div>
          {/if}
        {/if}
      </div>
    {:else}
      <div class="messages-inner">
        {#each messageList as message}
          <MessageBubble {message} />
        {/each}
        {#if isStreaming}
          <div class="thinking">
            <div class="thinking-label">Thinking</div>
            <div class="thinking-dots">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <div class="input-wrapper">
    <div class="input-inner">
      <form class="input-area" onsubmit={handleSubmit}>
        {#if messageList.length > 0 && !isStreaming}
          <button type="button" class="clear-btn" onclick={handleClearChat} title="Clear chat">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          </button>
        {/if}
        <textarea
          class="chat-input"
          placeholder="Ask about your documents..."
          bind:value={inputText}
          bind:this={textareaEl}
          oninput={autoResize}
          onkeydown={handleKeydown}
          rows="1"
          disabled={isStreaming}
        ></textarea>
        {#if isStreaming}
          <button type="button" class="stop-btn" onclick={stopGeneration} title="Stop generating">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          </button>
        {:else}
          <button type="submit" class="send-btn" disabled={!inputText.trim()} title="Send message">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        {/if}
      </form>
      <div class="input-hint">
        <kbd>Enter</kbd> to send &middot; <kbd>Shift+Enter</kbd> for new line
      </div>
    </div>
  </div>
</div>

{#if showClearConfirm}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="confirm-overlay" role="dialog" aria-modal="true" tabindex="-1"
    onclick={() => (showClearConfirm = false)}
    onkeydown={(e) => { if (e.key === 'Escape') showClearConfirm = false; }}>
    <!-- svelte-ignore a11y_no_static_element_interactions a11y_click_events_have_key_events -->
    <div class="confirm-dialog" onclick={(e) => e.stopPropagation()}>
      <p class="confirm-title">Clear chat history?</p>
      <p class="confirm-sub">This will remove all messages in this conversation.</p>
      <div class="confirm-actions">
        <button class="confirm-cancel" onclick={() => (showClearConfirm = false)}>Cancel</button>
        <button class="confirm-delete" onclick={confirmClear}>Clear</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .chat-window {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    background: var(--mantle);
  }
  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px 32px 12px;
  }
  .messages-inner {
    max-width: 820px;
    margin: 0 auto;
  }

  /* Empty state */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 0;
    padding: 32px;
    transition: all var(--transition-normal);
  }
  .empty-state.drag-over {
    background: var(--accent-subtle);
  }
  .drop-zone {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 48px;
    border: 2px dashed var(--accent);
    border-radius: var(--radius-xl);
    color: var(--accent);
    animation: pulse 1.5s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 0.7; }
    50% { opacity: 1; }
  }
  .drop-icon {
    width: 72px;
    height: 72px;
    border-radius: 20px;
    background: var(--accent-dim);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .drop-text {
    font-size: 16px;
    font-weight: 600;
    margin: 0;
  }
  .empty-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    max-width: 420px;
  }
  .empty-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: var(--accent-dim);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
  }
  .empty-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
    margin: 0;
    letter-spacing: -0.5px;
  }
  .empty-sub {
    font-size: 14px;
    color: var(--overlay0);
    margin: 8px 0 0;
    line-height: 1.5;
  }
  .empty-cta {
    margin-top: 28px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 20px;
    background: var(--accent-subtle);
    border: 1px solid var(--accent-dim);
    border-radius: var(--radius-md);
    color: var(--accent);
    font-size: 13px;
    font-weight: 500;
  }
  .cta-icon {
    flex-shrink: 0;
    opacity: 0.8;
  }
  .suggestions {
    margin-top: 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  .suggestions-label {
    font-size: 12px;
    color: var(--overlay0);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    margin: 0;
  }
  .suggestion-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
    max-width: 380px;
  }
  .suggestion-chip {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    background: var(--base);
    border: 1px solid var(--surface0);
    border-radius: var(--radius-md);
    color: var(--subtext0);
    font-size: 13px;
    font-family: var(--font-sans);
    cursor: pointer;
    text-align: left;
    transition: all var(--transition-fast);
  }
  .suggestion-chip:hover {
    border-color: var(--accent);
    color: var(--text);
    background: var(--accent-subtle);
  }
  .suggestion-chip svg {
    flex-shrink: 0;
    color: var(--overlay0);
  }
  .suggestion-chip:hover svg {
    color: var(--accent);
  }

  /* Thinking indicator */
  .thinking {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    margin-left: 42px;
  }
  .thinking-label {
    font-size: 12px;
    color: var(--overlay0);
    font-weight: 500;
  }
  .thinking-dots {
    display: flex;
    gap: 4px;
  }
  .dot {
    width: 6px;
    height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: bounce 1.2s ease-in-out infinite;
  }
  .dot:nth-child(2) { animation-delay: 0.15s; }
  .dot:nth-child(3) { animation-delay: 0.3s; }
  @keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.3; }
    30% { transform: translateY(-5px); opacity: 1; }
  }

  /* Input area */
  .input-wrapper {
    padding: 0 24px 16px;
    background: var(--mantle);
  }
  .input-inner {
    max-width: 820px;
    margin: 0 auto;
  }
  .input-area {
    display: flex;
    align-items: flex-end;
    gap: 8px;
    padding: 10px 14px;
    background: var(--base);
    border: 1px solid var(--surface0);
    border-radius: var(--radius-xl);
    transition: border-color var(--transition-normal), box-shadow var(--transition-normal);
  }
  .input-area:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-subtle);
  }
  .chat-input {
    flex: 1;
    padding: 4px 4px;
    border: none;
    background: transparent;
    color: var(--text);
    font-size: 14px;
    font-family: var(--font-sans);
    resize: none;
    outline: none;
    line-height: 1.5;
    max-height: 160px;
  }
  .chat-input::placeholder {
    color: var(--surface2);
  }
  .chat-input:disabled {
    opacity: 0.5;
  }
  .send-btn {
    padding: 8px;
    background: var(--accent);
    color: var(--accent-fg);
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-normal);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .send-btn:hover:not(:disabled) {
    background: var(--accent-hover);
    transform: scale(1.05);
  }
  .send-btn:disabled {
    opacity: 0.25;
    cursor: not-allowed;
  }
  .stop-btn {
    padding: 8px;
    background: var(--red-dim);
    color: var(--red);
    border: 1px solid rgba(243, 139, 168, 0.2);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-normal);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    animation: fadeIn 0.2s ease-out;
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
  }
  .stop-btn:hover {
    background: var(--red);
    color: white;
    border-color: var(--red);
  }
  .clear-btn {
    padding: 8px;
    background: none;
    border: none;
    color: var(--surface2);
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .clear-btn:hover {
    background: var(--red-dim);
    color: var(--red);
  }
  .input-hint {
    text-align: center;
    font-size: 11px;
    color: var(--surface1);
    padding-top: 8px;
  }
  .input-hint kbd {
    background: var(--hover-bg);
    padding: 1px 5px;
    border-radius: 3px;
    font-family: var(--font-sans);
    font-size: 10px;
    border: 1px solid var(--hover-bg-stronger);
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
