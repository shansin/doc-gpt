const BASE_URL = "http://localhost:18420";

export interface DocumentInfo {
  id: string;
  filename: string;
  chunk_count: number;
  ingested_at: string;
}

export interface Source {
  filename: string;
  chunk_text: string;
  score: number;
}

export interface ProgressEvent {
  type: "progress" | "error";
  filename: string;
  step: string;
  message?: string;
  current: number;
  total: number;
}

export interface GpuInfo {
  index: number;
  name: string;
  vram_total_mb: number;
  vram_used_mb: number;
  vram_free_mb: number;
}

export interface GpuSettingsResponse {
  gpus: GpuInfo[];
  ollama_gpu: number;
  docling_gpu: number;
  docling_requires_restart: boolean;
}

export async function fetchGpuSettings(): Promise<GpuSettingsResponse> {
  const res = await fetch(`${BASE_URL}/api/gpu-settings`);
  if (!res.ok) throw new Error(`Failed to fetch GPU settings: ${res.statusText}`);
  return res.json();
}

export async function updateGpuSettings(
  ollama_gpu: number,
  docling_gpu: number,
): Promise<GpuSettingsResponse> {
  const res = await fetch(`${BASE_URL}/api/gpu-settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ollama_gpu, docling_gpu }),
  });
  if (!res.ok) throw new Error(`Failed to update GPU settings: ${res.statusText}`);
  return res.json();
}

// ── System prompt ─────────────────────────────────────────────────

export interface SystemPromptResponse {
  system_prompt: string;
  is_default: boolean;
}

export async function fetchSystemPrompt(): Promise<SystemPromptResponse> {
  const res = await fetch(`${BASE_URL}/api/system-prompt`);
  if (!res.ok) throw new Error(`Failed to fetch system prompt: ${res.statusText}`);
  return res.json();
}

export async function updateSystemPrompt(systemPrompt: string): Promise<SystemPromptResponse> {
  const res = await fetch(`${BASE_URL}/api/system-prompt`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ system_prompt: systemPrompt }),
  });
  if (!res.ok) throw new Error(`Failed to update system prompt: ${res.statusText}`);
  return res.json();
}

export async function resetSystemPrompt(): Promise<SystemPromptResponse> {
  const res = await fetch(`${BASE_URL}/api/system-prompt`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Failed to reset system prompt: ${res.statusText}`);
  return res.json();
}

// ── Models ────────────────────────────────────────────────────────

export async function fetchModels(): Promise<{ models: { name: string; size: number }[] }> {
  const res = await fetch(`${BASE_URL}/api/models`);
  if (!res.ok) throw new Error(`Failed to fetch models: ${res.statusText}`);
  return res.json();
}

export async function fetchDocuments(): Promise<{ documents: DocumentInfo[] }> {
  const res = await fetch(`${BASE_URL}/api/documents`);
  if (!res.ok) throw new Error(`Failed to fetch documents: ${res.statusText}`);
  return res.json();
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/documents/${docId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Failed to delete document: ${res.statusText}`);
}

export async function deleteAllDocuments(): Promise<void> {
  const res = await fetch(`${BASE_URL}/api/documents`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Failed to delete all documents: ${res.statusText}`);
}

export function ingestFolder(
  folderPath: string,
  embedModel: string,
  onProgress: (event: ProgressEvent) => void,
  onDone: () => void,
  onError: (err: Error) => void
): () => void {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${BASE_URL}/api/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder_path: folderPath, embed_model: embedModel }),
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`Ingest failed: ${res.statusText}`);
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            const data = trimmed.slice(6);
            if (data === "[DONE]") {
              onDone();
              return;
            }
            try {
              const parsed = JSON.parse(data);
              onProgress(parsed as ProgressEvent);
            } catch {
              // skip unparseable lines
            }
          }
        }
      }
      onDone();
    } catch (err: any) {
      if (err.name !== "AbortError") onError(err);
    }
  })();

  return () => controller.abort();
}

export function sendChat(
  message: string,
  chatModel: string,
  embedModel: string,
  history: { role: string; content: string }[],
  onDelta: (text: string) => void,
  onSources: (sources: Source[]) => void,
  onDone: () => void,
  onError: (err: Error) => void
): () => void {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          chat_model: chatModel,
          embed_model: embedModel,
          history,
        }),
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`Chat failed: ${res.statusText}`);
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data: ")) {
            const data = trimmed.slice(6);
            if (data === "[DONE]") {
              onDone();
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.error) {
                onError(new Error(parsed.error));
                return;
              }
              if (parsed.type === "delta" && parsed.content) onDelta(parsed.content);
              if (parsed.type === "sources" && parsed.sources) onSources(parsed.sources);
            } catch {
              // skip unparseable lines
            }
          }
        }
      }
      onDone();
    } catch (err: any) {
      if (err.name !== "AbortError") onError(err);
    }
  })();

  return () => controller.abort();
}
