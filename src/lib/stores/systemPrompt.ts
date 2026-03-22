import { writable } from "svelte/store";
import {
  fetchSystemPrompt,
  updateSystemPrompt as apiUpdate,
  resetSystemPrompt as apiReset,
} from "$lib/api/backend";

export const systemPrompt = writable<string>("");
export const isDefault = writable<boolean>(true);
export const promptLoaded = writable<boolean>(false);

export async function loadSystemPrompt() {
  try {
    const data = await fetchSystemPrompt();
    systemPrompt.set(data.system_prompt);
    isDefault.set(data.is_default);
    promptLoaded.set(true);
  } catch (err) {
    console.error("Failed to load system prompt:", err);
  }
}

export async function saveSystemPrompt(prompt: string) {
  const data = await apiUpdate(prompt);
  systemPrompt.set(data.system_prompt);
  isDefault.set(data.is_default);
}

export async function resetToDefault() {
  const data = await apiReset();
  systemPrompt.set(data.system_prompt);
  isDefault.set(data.is_default);
}
