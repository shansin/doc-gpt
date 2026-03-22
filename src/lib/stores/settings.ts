import { get, writable } from "svelte/store";
import { fetchModels } from "$lib/api/backend";

export const chatModel = writable<string>("llama3.2");
export const embedModel = writable<string>("nomic-embed-text");
export const availableModels = writable<{ name: string; size: number }[]>([]);

/**
 * Find the best match for `current` among `names`.
 * Exact match → base-name match (before ':') → first in list.
 */
function resolveModel(current: string, names: string[]): string | null {
  if (names.length === 0) return null;
  if (names.includes(current)) return current;
  const base = current.split(":")[0];
  const match = names.find((n) => n.split(":")[0] === base);
  return match ?? names[0];
}

export async function loadModels(retries = 5, delayMs = 1000) {
  for (let i = 0; i < retries; i++) {
    try {
      const data = await fetchModels();
      const models: { name: string; size: number }[] = data.models;
      availableModels.set(models);

      // Sync selected models to actual available names
      const chatNames = models.filter((m) => !m.name.includes("embed")).map((m) => m.name);
      const embedNames = models.filter((m) => m.name.includes("embed")).map((m) => m.name);

      const resolvedChat = resolveModel(get(chatModel), chatNames);
      if (resolvedChat) chatModel.set(resolvedChat);

      const resolvedEmbed = resolveModel(get(embedModel), embedNames);
      if (resolvedEmbed) embedModel.set(resolvedEmbed);

      return;
    } catch (err) {
      console.error(`Failed to load models (attempt ${i + 1}/${retries}):`, err);
      if (i < retries - 1) await new Promise((r) => setTimeout(r, delayMs));
    }
  }
}
