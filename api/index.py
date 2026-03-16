"""
VoiceCare.ai AI Growth Engine — FastAPI backend for Vercel.

Serves the frontend and streams `python run.py strategy` output
to the browser via Server-Sent Events (SSE).
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, Response

# ── Paths ─────────────────────────────────────────────────────────────────────

# api/index.py lives inside api/, so parent.parent = project root
PROJECT_ROOT = str(Path(__file__).parent.parent)
sys.path.insert(0, PROJECT_ROOT)

from run import run_strategy_logic

# On Vercel the filesystem is read-only except /tmp/.
# Locally we write to {PROJECT_ROOT}/data/ (unchanged default behaviour).
IS_VERCEL = bool(os.environ.get("VERCEL"))
VOICECARE_DATA_DIR = "/tmp/voicecare" if IS_VERCEL else None
DASHBOARD_PATH = (
    os.path.join(VOICECARE_DATA_DIR, "data", "dashboard.html")
    if VOICECARE_DATA_DIR
    else os.path.join(PROJECT_ROOT, "data", "dashboard.html")
)

FRONTEND = Path(PROJECT_ROOT) / "public" / "index.html"

# Strip ANSI escape codes produced by Rich / Click
_ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="VoiceCare.ai Growth Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/")
async def root():
    """Serve the branded frontend."""
    if FRONTEND.exists():
        return HTMLResponse(FRONTEND.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>VoiceCare.ai AI Growth Engine</h1>")


@app.get("/api/run-strategy")
async def run_strategy():
    """
    Stream `python run.py strategy` stdout/stderr to the client
    as Server-Sent Events (SSE).  Each event is a JSON object:
        { "log": "<line>", "type": "info|success|error|warning|step" }
    A final event carries `{ "status": "complete", "dashboard_ready": true|false }`.
    """

    async def _event_stream():
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["FORCE_COLOR"] = "0"
        env["NO_COLOR"] = "1"
        env["TERM"] = "dumb"
        if VOICECARE_DATA_DIR:
            env["VOICECARE_DATA_DIR"] = VOICECARE_DATA_DIR

        yield _sse({"log": ">>> Initializing VoiceCare.ai AI Growth Engine…", "type": "info"})

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_strategy_logic)

        ready = os.path.exists(DASHBOARD_PATH)
        yield _sse(
            {
                "status": "complete",
                "dashboard_ready": ready,
                "log": (
                    ">>> Strategy complete! Dashboard is ready."
                    if ready
                    else ">>> Strategy complete. (Dashboard file not found — check logs.)"
                ),
                "type": "success" if ready else "warning",
            }
        )

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/dashboard")
async def get_dashboard():
    """Serve the generated dashboard HTML in the browser."""
    if os.path.exists(DASHBOARD_PATH):
        return HTMLResponse(Path(DASHBOARD_PATH).read_text(encoding="utf-8"))
    return HTMLResponse(
        "<html><body style='background:#0f172a;color:#e2e8f0;"
        "font-family:sans-serif;display:flex;align-items:center;"
        "justify-content:center;height:100vh'>"
        "<div style='text-align:center'><h2>Dashboard not ready</h2>"
        "<p style=\"color:#64748b\">Run the strategy first.</p></div></body></html>",
        status_code=404,
    )


@app.get("/api/download")
async def download_dashboard():
    """Download the dashboard as a self-contained HTML file."""
    if os.path.exists(DASHBOARD_PATH):
        return FileResponse(
            DASHBOARD_PATH,
            media_type="text/html",
            filename="voicecare-ai-growth-report.html",
        )
    return Response(content="Dashboard not ready. Run strategy first.", status_code=404)


@app.get("/api/logo")
async def get_logo():
    """Serve the VoiceCare.ai logo."""
    logo_path = os.path.join(PROJECT_ROOT, "data", "logo.avif")
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/avif")
    return Response(status_code=404)


@app.get("/api/status")
async def status():
    """Quick health-check — tells the client whether the dashboard is ready."""
    return {
        "dashboard_ready": os.path.exists(DASHBOARD_PATH),
        "is_vercel": IS_VERCEL,
        "data_dir": VOICECARE_DATA_DIR or os.path.join(PROJECT_ROOT, "data"),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _classify(line: str) -> str:
    lo = line.lower()
    if any(k in lo for k in ("error", "fail", "exception", "traceback")):
        return "error"
    if any(k in lo for k in ("warning", "warn")):
        return "warning"
    if any(k in lo for k in ("complete", "done", "saved", "dashboard", "success", "✓", "→")):
        return "success"
    if line.startswith("[") and "/5]" in line:
        return "step"
    if line.startswith("=") or line.startswith("-"):
        return "dim"
    return "info"


# ── Local dev entry-point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
