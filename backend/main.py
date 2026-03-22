import multiprocessing

# Use "spawn" so worker processes don't inherit the listening socket.
# Must be called before any ProcessPoolExecutor is created.
multiprocessing.set_start_method("spawn", force=True)

from app import create_app
import uvicorn

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=18420, reload=True)
