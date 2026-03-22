import { writable, get } from "svelte/store";
import {
  fetchDocuments,
  deleteDocument,
  deleteAllDocuments,
  ingestFolder,
  type DocumentInfo,
  type ProgressEvent,
} from "$lib/api/backend";
import { embedModel } from "./settings";
import { addToast } from "./toast";

export interface ImportError {
  filename: string;
  message: string;
}

export const documents = writable<DocumentInfo[]>([]);
export const importing = writable<boolean>(false);
export const importProgress = writable<ProgressEvent | null>(null);
export const importErrors = writable<ImportError[]>([]);

let cancelIngestFn: (() => void) | null = null;

export async function loadDocuments() {
  try {
    const data = await fetchDocuments();
    documents.set(data.documents);
  } catch (err) {
    console.error("Failed to load documents:", err);
  }
}

export async function removeDocument(id: string) {
  try {
    await deleteDocument(id);
    documents.update((docs) => docs.filter((d) => d.id !== id));
  } catch (err) {
    console.error("Failed to delete document:", err);
  }
}

export async function removeAllDocuments() {
  try {
    await deleteAllDocuments();
    documents.set([]);
  } catch (err) {
    console.error("Failed to delete all documents:", err);
  }
}

export function clearImportErrors() {
  importErrors.set([]);
}

export function cancelIngest() {
  if (cancelIngestFn) {
    cancelIngestFn();
    cancelIngestFn = null;
    importing.set(false);
    importProgress.set(null);
    addToast("Import cancelled", "info");
    loadDocuments();
  }
}

export function startIngest(folderPath: string) {
  importing.set(true);
  importProgress.set(null);
  importErrors.set([]);

  cancelIngestFn = ingestFolder(
    folderPath,
    get(embedModel),
    (event: ProgressEvent) => {
      if (event.type === "error") {
        importErrors.update((errs) => [
          ...errs,
          { filename: event.filename, message: event.message || "Unknown error" },
        ]);
      }
      importProgress.set(event);
    },
    () => {
      importing.set(false);
      importProgress.set(null);
      cancelIngestFn = null;
      const errors = get(importErrors);
      if (errors.length > 0) {
        addToast(`Import complete with ${errors.length} failed file${errors.length > 1 ? "s" : ""}`, "error");
      } else {
        addToast("All documents imported successfully", "success");
      }
      loadDocuments();
    },
    (err: Error) => {
      console.error("Ingest error:", err);
      importing.set(false);
      importProgress.set(null);
      cancelIngestFn = null;
      addToast("Import failed: " + err.message, "error");
    }
  );
}
