import { writable } from "svelte/store";

export interface ToastItem {
  id: number;
  message: string;
  type: "success" | "error" | "info";
}

let nextId = 0;

export const toasts = writable<ToastItem[]>([]);

export function addToast(
  message: string,
  type: "success" | "error" | "info" = "info",
  duration = 4000,
) {
  const id = nextId++;
  toasts.update((t) => [...t, { id, message, type }]);
  setTimeout(() => {
    toasts.update((t) => t.filter((item) => item.id !== id));
  }, duration);
}

export function dismissToast(id: number) {
  toasts.update((t) => t.filter((item) => item.id !== id));
}
