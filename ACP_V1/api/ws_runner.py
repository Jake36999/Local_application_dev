import asyncio
import os
import sys
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pathlib import Path

router = APIRouter()
SCRIPTS_DIR = Path("../../scripts").resolve()
PYTHON_EXE = sys.executable

@router.websocket("/ws/run-script")
async def websocket_run_script(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        script_name = data.get("name")
        args = data.get("args", [])
        script_path = SCRIPTS_DIR / script_name
        if not script_path.exists():
            await websocket.send_json({"type": "error", "message": f"Script not found: {script_name}"})
            await websocket.close()
            return
        await websocket.send_json({"type": "log", "line": f"🚀 Launching {script_name}..."})
        process = await asyncio.create_subprocess_exec(
            PYTHON_EXE, "-u", str(script_path), *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(SCRIPTS_DIR),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        async def read_stream(stream, channel):
            while True:
                line = await stream.readline()
                if not line: break
                text = line.decode().strip()
                if text:
                    await websocket.send_json({"type": channel, "line": text})
        await asyncio.gather(
            read_stream(process.stdout, "log"),
            read_stream(process.stderr, "error")
        )
        await process.wait()
        status = "✅ Success" if process.returncode == 0 else f"❌ Failed (Code {process.returncode})"
        await websocket.send_json({"type": "status", "message": status, "code": process.returncode})
    except WebSocketDisconnect:
        if 'process' in locals() and process.returncode is None:
            try: process.terminate()
            except: pass
    except Exception as e:
        try: await websocket.send_json({"type": "error", "message": str(e)})
        except: pass
