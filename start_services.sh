#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $APP_PID 2>/dev/null
    wait $BACKEND_PID $APP_PID 2>/dev/null
    echo "Services stopped."
}
trap cleanup EXIT INT TERM

# Read Docling GPU assignment from persisted settings (default: GPU 1)
SETTINGS_FILE="$HOME/.doc-gpt/settings.json"
if [ -z "${CUDA_VISIBLE_DEVICES:-}" ]; then
    DOCLING_GPU=1
    if [ -f "$SETTINGS_FILE" ]; then
        SAVED_GPU=$(python3 -c "import json; d=json.load(open('$SETTINGS_FILE')); print(d.get('docling_gpu', -1))" 2>/dev/null || echo "-1")
        if [ "$SAVED_GPU" != "-1" ]; then
            DOCLING_GPU="$SAVED_GPU"
        fi
    fi
    export CUDA_VISIBLE_DEVICES="$DOCLING_GPU"
fi

# Start backend (FastAPI via uvicorn)
echo "Starting backend (Docling on GPU $CUDA_VISIBLE_DEVICES)..."
cd "$SCRIPT_DIR/backend"
uv run python main.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:18420/api/models >/dev/null 2>&1; then
    echo "Backend is ready."
    break
  fi
  sleep 1
done

# Start app (Tauri desktop window + Vite dev server)
echo "Starting app..."
cd "$SCRIPT_DIR"
npm run tauri dev &
APP_PID=$!

echo "Backend PID: $BACKEND_PID (port 18420)"
echo "App PID: $APP_PID"
echo "Press Ctrl+C to stop all services."

wait
