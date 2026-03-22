# doc-gpt

A desktop app for chatting with your documents using local LLMs. Import a folder of documents, and doc-gpt will convert, chunk, embed, and store them in a local vector database so you can ask questions with full RAG (Retrieval-Augmented Generation) — all running on your machine.

## Features

- **Document ingestion** — drag in a folder of PDFs, Word docs, and other files. Docling handles conversion, then chunks are embedded and stored in a local Qdrant vector database.
- **RAG chat** — ask questions and get answers grounded in your documents, with source citations.
- **Streaming responses** — real-time token streaming via SSE.
- **Multi-GPU support** — assign Ollama and Docling to different GPUs to run inference and conversion in parallel.
- **Model selection** — pick any model served by your local Ollama instance for chat and embeddings.
- **Dark / light theme** — Catppuccin-based color scheme with a toggle.
- **Fully local** — no data leaves your machine.

## Architecture

| Layer | Tech |
|-------|------|
| Desktop shell | Tauri 2 (Rust) |
| Frontend | SvelteKit 2, TypeScript, Vite |
| Backend API | FastAPI, Uvicorn (Python 3.12+) |
| Document conversion | Docling (GPU-accelerated) |
| Embeddings & chat | Ollama |
| Vector store | Qdrant (local/embedded mode) |

## Prerequisites

- [Rust](https://rustup.rs/) (stable)
- [Node.js](https://nodejs.org/) >= 20
- [Python](https://www.python.org/) >= 3.12
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [Ollama](https://ollama.com/) running locally with at least one chat model and an embedding model pulled (defaults: `llama3.2` and `nomic-embed-text`)
- Linux: `libwebkit2gtk-4.1-dev`, `libappindicator3-dev`, `librsvg2-dev`, `patchelf`

## Getting Started

```bash
# Clone the repo
git clone https://github.com/shsin/doc-gpt.git
cd doc-gpt

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
uv sync
cd ..

# Pull default Ollama models
ollama pull llama3.2
ollama pull nomic-embed-text

# Start everything (backend + Tauri dev window)
./start_services.sh
```

`start_services.sh` launches the FastAPI backend on port 18420 and the Tauri dev app. Press `Ctrl+C` to stop both.

## Building for Production

```bash
npm run tauri build
```

Produces platform-specific installers in `src-tauri/target/release/bundle/`.

## Project Structure

```
doc-gpt/
├── src/                  # SvelteKit frontend
│   ├── lib/
│   │   ├── api/          # Backend API client
│   │   ├── components/   # Svelte components (ChatWindow, Sidebar, etc.)
│   │   └── stores/       # Svelte stores (chat, documents, settings, theme)
│   └── routes/           # SvelteKit pages
├── src-tauri/            # Tauri / Rust shell
├── backend/              # FastAPI backend
│   └── app/
│       ├── routers/      # API endpoints (chat, documents, models, settings)
│       └── services/     # Docling, chunker, embedder, RAG, vector store
├── start_services.sh     # Dev launcher (backend + app)
└── .github/workflows/    # CI builds (Linux, macOS, Windows)
```

## Configuration

Settings are persisted to `~/.doc-gpt/settings.json` and can be changed from the in-app settings panel:

- Chat and embedding model selection
- GPU assignments for Ollama and Docling
- Ollama base URL

## License

MIT
