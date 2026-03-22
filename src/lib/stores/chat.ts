import { writable, get } from "svelte/store";
import { sendChat, type Source } from "$lib/api/backend";
import { chatModel, embedModel } from "./settings";

export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export const messages = writable<Message[]>([]);
export const streaming = writable<boolean>(false);

let cancelFn: (() => void) | null = null;

export function sendMessage(text: string) {
  const userMsg: Message = { role: "user", content: text };
  messages.update((msgs) => [...msgs, userMsg]);

  const assistantMsg: Message = { role: "assistant", content: "" };
  messages.update((msgs) => [...msgs, assistantMsg]);
  streaming.set(true);

  const history = get(messages)
    .slice(0, -1)
    .map((m) => ({ role: m.role, content: m.content }));

  cancelFn = sendChat(
    text,
    get(chatModel),
    get(embedModel),
    history,
    (delta: string) => {
      messages.update((msgs) => {
        const last = msgs[msgs.length - 1];
        return [...msgs.slice(0, -1), { ...last, content: last.content + delta }];
      });
    },
    (sources: Source[]) => {
      messages.update((msgs) => {
        const last = msgs[msgs.length - 1];
        return [...msgs.slice(0, -1), { ...last, sources }];
      });
    },
    () => {
      streaming.set(false);
      cancelFn = null;
    },
    (err: Error) => {
      console.error("Chat error:", err);
      messages.update((msgs) => {
        const last = msgs[msgs.length - 1];
        return [
          ...msgs.slice(0, -1),
          { ...last, content: last.content || "Error: " + err.message },
        ];
      });
      streaming.set(false);
      cancelFn = null;
    }
  );
}

export function stopGeneration() {
  if (cancelFn) {
    cancelFn();
    cancelFn = null;
    streaming.set(false);
  }
}

export function clearChat() {
  if (cancelFn) cancelFn();
  messages.set([]);
  streaming.set(false);
}
