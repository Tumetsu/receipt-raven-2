"""Serve the built frontend (single-page app) from the backend.

In the Docker image the Vite build lands in `/app/static`. In development the
directory does not exist and Vite's dev server serves the frontend instead.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


def mount_spa(app: FastAPI, static_dir: Path, api_prefix: str) -> None:
    """Serve `static_dir` and fall back to `index.html` for client-side routes.

    Call this after every API router is registered: the catch-all route would
    otherwise shadow them.
    """
    if not static_dir.exists():
        return

    static_dir = static_dir.resolve()
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="static_assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        # An unknown API path is a client bug; answering it with HTML hides that.
        if full_path.startswith(api_prefix.strip("/") + "/"):
            raise HTTPException(status_code=404, detail="Not found")
        file_path = (static_dir / full_path).resolve()
        # Reject path traversal out of the static directory.
        if not file_path.is_relative_to(static_dir):
            raise HTTPException(status_code=404, detail="Not found")
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")
