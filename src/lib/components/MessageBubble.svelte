<script lang="ts">
  import type { Message } from "$lib/stores/chat";
  import { marked } from "marked";

  interface Props {
    message: Message;
  }
  let { message }: Props = $props();

  let showSources = $state(false);
  let copied = $state(false);

  marked.setOptions({
    breaks: true,
    gfm: true,
  });

  function renderMarkdown(text: string): string {
    return marked.parse(text) as string;
  }

  async function copyContent() {
    try {
      await navigator.clipboard.writeText(message.content);
      copied = true;
      setTimeout(() => (copied = false), 2000);
    } catch {
      // Fallback
    }
  }
</script>

<div class="message-row" class:user={message.role === "user"}>
  <div class="avatar" class:user={message.role === "user"}>
    {#if message.role === "user"}
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
      </svg>
    {:else}
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a4 4 0 0 1 4 4v1a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V6a4 4 0 0 1 4-4z" />
        <rect x="3" y="11" width="18" height="10" rx="2" />
        <circle cx="9" cy="16" r="1" />
        <circle cx="15" cy="16" r="1" />
      </svg>
    {/if}
  </div>
  <div class="bubble-wrap" class:user={message.role === "user"}>
    <div class="bubble" class:user={message.role === "user"}>
      {#if message.role === "user"}
        <div class="content">{message.content}</div>
      {:else}
        <div class="content markdown">{@html renderMarkdown(message.content)}</div>
      {/if}
      {#if message.sources && message.sources.length > 0}
        <div class="sources-section">
          <button class="sources-toggle" onclick={() => (showSources = !showSources)}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            {showSources ? "Hide" : "Show"} {message.sources.length} source{message.sources.length !== 1 ? "s" : ""}
            <svg class="toggle-chevron" class:open={showSources} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          {#if showSources}
            <div class="sources">
              {#each message.sources as source, i}
                <div class="source-card">
                  <div class="source-header">
                    <div class="source-left">
                      <span class="source-num">{i + 1}</span>
                      <span class="source-doc">{source.filename}</span>
                    </div>
                    <span class="source-score">{(source.score * 100).toFixed(0)}%</span>
                  </div>
                  <p class="source-text">{source.chunk_text}</p>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
    {#if message.content}
      <div class="bubble-actions" class:user={message.role === "user"}>
        <button class="action-btn" onclick={copyContent} title={copied ? "Copied!" : "Copy message"}>
          {#if copied}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6L9 17l-5-5" />
            </svg>
          {:else}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
          {/if}
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  .message-row {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    animation: fadeIn 0.25s ease-out;
    align-items: flex-start;
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .message-row.user {
    flex-direction: row-reverse;
  }
  .avatar {
    width: 34px;
    height: 34px;
    border-radius: var(--radius-md);
    background: var(--accent-dim);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
  }
  .avatar.user {
    background: rgba(59, 130, 246, 0.22);
    color: var(--lavender);
  }
  .bubble-wrap {
    max-width: 72%;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .bubble-wrap.user {
    align-items: flex-end;
  }
  .bubble {
    padding: 14px 18px;
    border-radius: var(--radius-lg);
    background: var(--base);
    border: 1px solid var(--surface0);
    color: var(--text);
    font-size: 14px;
    line-height: 1.65;
  }
  .bubble.user {
    background: var(--accent);
    border-color: var(--accent);
    color: var(--bubble-user-text);
    border-bottom-right-radius: 4px;
  }
  .bubble:not(.user) {
    border-bottom-left-radius: 4px;
  }
  .content {
    word-break: break-word;
  }
  .content:not(.markdown) {
    white-space: pre-wrap;
  }
  .bubble-actions {
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity var(--transition-fast);
    padding-left: 4px;
  }
  .bubble-actions.user {
    padding-left: 0;
    padding-right: 4px;
  }
  .message-row:hover .bubble-actions {
    opacity: 1;
  }
  .action-btn {
    background: none;
    border: none;
    color: var(--overlay0);
    cursor: pointer;
    padding: 4px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    transition: all var(--transition-fast);
  }
  .action-btn:hover {
    color: var(--text);
    background: var(--hover-bg-stronger);
  }

  /* Markdown content styles */
  .content.markdown :global(p) {
    margin: 0 0 10px;
  }
  .content.markdown :global(p:last-child) {
    margin-bottom: 0;
  }
  .content.markdown :global(code) {
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.88em;
    font-family: var(--font-mono);
  }
  .content.markdown :global(pre) {
    background: var(--crust);
    padding: 14px 16px;
    border-radius: var(--radius-sm);
    overflow-x: auto;
    margin: 10px 0;
    border: 1px solid var(--surface0);
  }
  .content.markdown :global(pre code) {
    background: none;
    padding: 0;
    font-size: 13px;
    line-height: 1.5;
  }
  .content.markdown :global(ul),
  .content.markdown :global(ol) {
    margin: 6px 0;
    padding-left: 20px;
  }
  .content.markdown :global(li) {
    margin-bottom: 3px;
  }
  .content.markdown :global(blockquote) {
    border-left: 3px solid var(--accent);
    padding-left: 14px;
    margin: 10px 0;
    color: var(--subtext0);
  }
  .content.markdown :global(strong) {
    font-weight: 600;
    color: var(--strong-text);
  }
  .content.markdown :global(a) {
    color: var(--blue);
    text-decoration: none;
  }
  .content.markdown :global(a:hover) {
    text-decoration: underline;
  }
  .content.markdown :global(h1),
  .content.markdown :global(h2),
  .content.markdown :global(h3) {
    margin: 14px 0 8px;
    color: var(--strong-text);
  }
  .content.markdown :global(table) {
    border-collapse: collapse;
    margin: 10px 0;
    width: 100%;
  }
  .content.markdown :global(th),
  .content.markdown :global(td) {
    border: 1px solid var(--surface0);
    padding: 8px 12px;
    font-size: 13px;
  }
  .content.markdown :global(th) {
    background: var(--accent-subtle);
    font-weight: 600;
  }

  /* Sources */
  .sources-section {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--surface0);
  }
  .sources-toggle {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    background: var(--accent-subtle);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-family: var(--font-sans);
    color: var(--accent);
    cursor: pointer;
    transition: all var(--transition-fast);
    font-weight: 500;
  }
  .sources-toggle:hover {
    background: var(--accent-dim);
  }
  .toggle-chevron {
    transition: transform var(--transition-fast);
  }
  .toggle-chevron.open {
    transform: rotate(180deg);
  }
  .sources {
    margin-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .source-card {
    background: var(--source-card-bg);
    border: 1px solid var(--surface0);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    transition: border-color var(--transition-fast);
  }
  .source-card:hover {
    border-color: var(--surface1);
  }
  .source-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }
  .source-left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
  }
  .source-num {
    font-size: 10px;
    font-weight: 700;
    color: var(--accent);
    background: var(--accent-subtle);
    width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .source-doc {
    font-weight: 600;
    font-size: 12px;
    color: var(--lavender);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .source-score {
    font-size: 10px;
    color: var(--overlay0);
    background: var(--hover-bg);
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 600;
    flex-shrink: 0;
  }
  .source-text {
    margin: 0;
    color: var(--subtext0);
    font-size: 12px;
    line-height: 1.5;
    max-height: 100px;
    overflow-y: auto;
  }
</style>
