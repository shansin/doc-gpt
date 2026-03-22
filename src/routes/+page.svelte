<script lang="ts">
  import { onMount } from "svelte";
  import Sidebar from "$lib/components/Sidebar.svelte";
  import ChatWindow from "$lib/components/ChatWindow.svelte";
  import SettingsPanel from "$lib/components/SettingsPanel.svelte";
  import Toast from "$lib/components/Toast.svelte";
  import { loadModels } from "$lib/stores/settings";
  import { loadDocuments } from "$lib/stores/documents";
  import "$lib/stores/theme"; // ensure theme is applied on load

  let sidebarOpen = $state(true);

  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }

  onMount(() => {
    loadModels();
    loadDocuments();

    function handleKeydown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === "b") {
        e.preventDefault();
        toggleSidebar();
      }
    }
    window.addEventListener("keydown", handleKeydown);
    return () => window.removeEventListener("keydown", handleKeydown);
  });
</script>

<div class="app-layout">
  <Sidebar open={sidebarOpen} onToggle={toggleSidebar} />
  <main class="main-area">
    <SettingsPanel {sidebarOpen} onToggleSidebar={toggleSidebar} />
    <ChatWindow />
  </main>
</div>
<Toast />

<style>
  /* ========== Dark theme (default) ========== */
  :global(:root),
  :global([data-theme="dark"]) {
    color-scheme: dark;

    /* Base palette (Catppuccin Mocha) */
    --crust: #11111b;
    --mantle: #181825;
    --base: #1e1e2e;
    --surface0: #313244;
    --surface1: #45475a;
    --surface2: #585b70;
    --overlay0: #6c7086;
    --overlay1: #7f849c;
    --subtext0: #a6adc8;
    --subtext1: #bac2de;
    --text: #cdd6f4;

    /* Accent */
    --accent: #3b82f6;
    --accent-hover: #2563eb;
    --accent-dim: rgba(59, 130, 246, 0.15);
    --accent-subtle: rgba(59, 130, 246, 0.08);
    --accent-fg: #ffffff;
    --lavender: #93c5fd;

    /* Semantic */
    --red: #f38ba8;
    --red-dim: rgba(243, 139, 168, 0.12);
    --green: #a6e3a1;
    --green-dim: rgba(166, 227, 161, 0.12);
    --blue: #89b4fa;
    --yellow: #f9e2af;
    --peach: #fab387;
    --mauve: #cba6f7;

    /* Misc */
    --selection-bg: rgba(59, 130, 246, 0.35);
    --scroll-thumb: rgba(205, 214, 244, 0.08);
    --scroll-thumb-hover: rgba(205, 214, 244, 0.15);
    --hover-bg: rgba(255, 255, 255, 0.04);
    --hover-bg-stronger: rgba(255, 255, 255, 0.05);
    --bubble-user-bg: var(--accent);
    --bubble-user-text: #ffffff;
    --strong-text: #ffffff;
    --code-bg: rgba(0, 0, 0, 0.3);
    --source-card-bg: rgba(0, 0, 0, 0.15);
  }

  /* ========== Light theme (Catppuccin Latte) ========== */
  :global([data-theme="light"]) {
    color-scheme: light;

    --crust: #dce0e8;
    --mantle: #e6e9ef;
    --base: #eff1f5;
    --surface0: #ccd0da;
    --surface1: #bcc0cc;
    --surface2: #acb0be;
    --overlay0: #9ca0b0;
    --overlay1: #8c8fa1;
    --subtext0: #6c6f85;
    --subtext1: #5c5f77;
    --text: #4c4f69;

    --accent: #3b82f6;
    --accent-hover: #2563eb;
    --accent-dim: rgba(59, 130, 246, 0.15);
    --accent-subtle: rgba(59, 130, 246, 0.07);
    --accent-fg: #ffffff;
    --lavender: #7287fd;

    --red: #d20f39;
    --red-dim: rgba(210, 15, 57, 0.1);
    --green: #40a02b;
    --green-dim: rgba(64, 160, 43, 0.1);
    --blue: #1e66f5;
    --yellow: #df8e1d;
    --peach: #fe640b;
    --mauve: #8839ef;

    --selection-bg: rgba(59, 130, 246, 0.25);
    --scroll-thumb: rgba(76, 79, 105, 0.12);
    --scroll-thumb-hover: rgba(76, 79, 105, 0.22);
    --hover-bg: rgba(0, 0, 0, 0.04);
    --hover-bg-stronger: rgba(0, 0, 0, 0.06);
    --bubble-user-bg: var(--accent);
    --bubble-user-text: #ffffff;
    --strong-text: #1e1e2e;
    --code-bg: rgba(0, 0, 0, 0.06);
    --source-card-bg: rgba(0, 0, 0, 0.03);
  }

  /* ========== Layout */
  :global(:root) {
    --sidebar-width: 300px;
    --header-height: 52px;
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-xl: 18px;

    --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-mono: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;

    --transition-fast: 0.15s ease;
    --transition-normal: 0.2s ease;
    --transition-slow: 0.3s ease;
  }

  :global(body) {
    margin: 0;
    padding: 0;
    font-family: var(--font-sans);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: var(--crust);
    color: var(--text);
    line-height: 1.5;
  }

  :global(*) {
    box-sizing: border-box;
  }

  :global(::selection) {
    background: var(--selection-bg);
  }

  :global(::-webkit-scrollbar) {
    width: 6px;
  }
  :global(::-webkit-scrollbar-track) {
    background: transparent;
  }
  :global(::-webkit-scrollbar-thumb) {
    background: var(--scroll-thumb);
    border-radius: 3px;
  }
  :global(::-webkit-scrollbar-thumb:hover) {
    background: var(--scroll-thumb-hover);
  }

  .app-layout {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }

  .main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    background: var(--mantle);
  }
</style>
