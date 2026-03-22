import { writable } from "svelte/store";

export type Theme = "dark" | "light";

const STORAGE_KEY = "doc-gpt-theme";

function getInitialTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") return stored;
  return "dark";
}

export const theme = writable<Theme>(getInitialTheme());

export function toggleTheme() {
  theme.update((t) => {
    const next = t === "dark" ? "light" : "dark";
    applyTheme(next);
    return next;
  });
}

export function setTheme(t: Theme) {
  theme.set(t);
  applyTheme(t);
}

function applyTheme(t: Theme) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, t);
  document.documentElement.setAttribute("data-theme", t);
}

// Apply on load
if (typeof window !== "undefined") {
  applyTheme(getInitialTheme());
}
