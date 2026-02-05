import asyncio
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .handlers import route_request, execute_llm_plan
from .schemas import IngestRequest, IngestResponse, ScanRequest, ScanResponse, BusEvent, WorkflowRequest
from .tool_registry import TOOLKIT_MANIFEST

# Creates the DB file if it doesn't exist (global connection)
db_conn = sqlite3.connect("memory/sql/project_meta.db", check_same_thread=False)

app = FastAPI(
    title="Aletheia Content Intake Bus",
    description="Orchestrates PDF and Code ingestion workflows.",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    def broadcast(self, message: dict) -> None:
        """Best-effort, fire-and-forget broadcast."""
        for ws in list(self.active):
            try:
                asyncio.create_task(ws.send_json(message))
            except Exception:
                try:
                    self.active.remove(ws)
                except ValueError:
                    pass


manager = ConnectionManager()


@app.post("/choose-content", response_model=IngestResponse)
async def choose_content(request: IngestRequest):
    """Accept a content selection and route to the correct backend workflow."""
    try:
        result_message = route_request(request.selection, request.target_path, manager=manager)
        return IngestResponse(
            status="success",
            workflow_id=request.selection.name,
            message=result_message,
            target=request.target_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {exc}") from exc


async def _run_scan(request: ScanRequest):
    # offload to thread to avoid blocking the event loop
    return await asyncio.to_thread(route_request, request.selection, request.target_path, manager)


@app.post("/api/scan", response_model=ScanResponse)
async def api_scan(request: ScanRequest):
    """Start a scan based on selection and target_path; broadcasts bus events."""
    try:
        asyncio.create_task(_run_scan(request))
        return ScanResponse(
            status="queued",
            workflow_id=request.selection.name,
            message="scan queued",
            target=request.target_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {exc}") from exc


@app.get("/api/scans")
async def api_scans():
    """List recent scans (placeholder)."""
    return {"status": "ok", "message": "scans listing not yet implemented"}


@app.post("/api/workflow")
async def api_workflow(request: WorkflowRequest):
    """Execute an LLM-suggested workflow plan using registered tools."""
    try:
        result = await asyncio.to_thread(execute_llm_plan, request.model_dump(), manager, db_conn)
        return {"status": "completed", "results": result}
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {exc}") from exc


@app.get("/api/tools")
async def api_tools():
    """Return the available tools and their schemas for LLM planning."""
    return TOOLKIT_MANIFEST


@app.websocket("/ws/bus")
async def websocket_bus(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"event": "BUS_CONNECTED", "payload": {"message": "Connected to Backend Bus"}})
        while True:
            await websocket.receive_text()  # keep alive; ignore client messages
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
