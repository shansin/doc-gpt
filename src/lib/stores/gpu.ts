import { writable } from "svelte/store";
import {
  fetchGpuSettings,
  updateGpuSettings,
  type GpuInfo,
  type GpuSettingsResponse,
} from "$lib/api/backend";
import { addToast } from "./toast";

export const gpus = writable<GpuInfo[]>([]);
export const ollamaGpu = writable<number>(-1);
export const doclingGpu = writable<number>(-1);
export const gpuLoaded = writable<boolean>(false);

export async function loadGpuSettings() {
  try {
    const data = await fetchGpuSettings();
    gpus.set(data.gpus);
    ollamaGpu.set(data.ollama_gpu);
    doclingGpu.set(data.docling_gpu);
    gpuLoaded.set(true);
  } catch (err) {
    console.error("Failed to load GPU settings:", err);
  }
}

export async function saveGpuSettings(ollama: number, docling: number) {
  try {
    const data = await updateGpuSettings(ollama, docling);
    gpus.set(data.gpus);
    ollamaGpu.set(data.ollama_gpu);
    doclingGpu.set(data.docling_gpu);

    if (data.docling_requires_restart) {
      addToast("Docling GPU change will take effect after restart", "info", 6000);
    } else {
      addToast("GPU settings saved", "success");
    }
  } catch (err) {
    console.error("Failed to save GPU settings:", err);
    addToast("Failed to save GPU settings", "error");
  }
}
