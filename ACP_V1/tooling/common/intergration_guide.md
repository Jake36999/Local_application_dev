Frontend-Backend Integration Guide

Workspace Packager V2.3

This guide details how to wire up the React Frontend (workspace_packager_ui.jsx) to the Python Backend (workspace_packager/app/main.py).

1. Backend Preparation (Python/FastAPI)

Before the frontend can talk to the backend, you need to expose the necessary endpoints and enable CORS (Cross-Origin Resource Sharing).

A. Enable CORS

In your workspace_packager/app/main.py, ensure you have the following setup to allow the React app (usually running on port 3000 or 5173) to send requests.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Adjust for your frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


B. Create Required Endpoints

You need three specific endpoints to match the UI's functionality:

Trigger Scan (POST /api/scan)

Get History (GET /api/scans)

Real-time Bus (WebSocket /ws/bus)

Add this structure to your handlers.py or main.py:

from fastapi import WebSocket, WebSocketDisconnect

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/bus")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for client "pings" or command triggers
            data = await websocket.receive_text() 
    except WebSocketDisconnect:
        manager.active_connections.remove(websocket)

@app.post("/api/scan")
async def start_scan(request: ScanRequest): # Define ScanRequest schema in schemas.py
    # 1. Start your background process
    # 2. Emit a bus event
    await manager.broadcast({
        "source": "CORE", 
        "type": "PROCESS_START", 
        "message": f"Scanning {request.path}"
    })
    return {"status": "started"}


2. Frontend Integration (React)

Open workspace_packager_ui.jsx and modify the state management to use real network calls instead of mock data.

A. Establish WebSocket Connection

Replace the // --- BUS SYSTEM SIMULATION --- section with a real WebSocket hook.

// Add inside App component
const ws = useRef(null);

useEffect(() => {
  // Connect to Backend WebSocket
  ws.current = new WebSocket("ws://localhost:8000/ws/bus");

  ws.current.onopen = () => {
    emitBusEvent('UI', 'SUCCESS', 'Connected to Backend Bus');
  };

  ws.current.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // 1. Add to Log
    setBusLogs(prev => [...prev, { ...data, id: Date.now(), timestamp: new Date().toISOString() }]);

    // 2. Handle Progress Updates automatically
    if (data.type === 'PROGRESS') {
      setProgress(data.payload.percent);
      setCurrentStep(data.message);
    }
    
    // 3. Handle Completion
    if (data.type === 'PROCESS_COMPLETE') {
      setIsScanning(false);
      setCompletedScans(prev => [data.payload.scanResult, ...prev]);
    }
  };

  return () => ws.current.close();
}, []);


B. Wire up "Run Scan" Button

Replace the handleStartScan function to POST data to your Python backend.

const handleStartScan = async () => {
  if (!scanPath) return;

  try {
    setIsScanning(true);
    
    // Call Python Backend
    const response = await fetch('http://localhost:8000/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: scanPath })
    });

    if (!response.ok) throw new Error('Failed to start scan');
    
    emitBusEvent('UI', 'SUCCESS', 'Scan command sent to core');
    
  } catch (error) {
    setIsScanning(false);
    emitBusEvent('UI', 'ERROR', 'Network Error', { details: error.message });
  }
};


3. The "Bus" Data Structure Protocol

To ensure the Frontend logs look correct, your Python backend should send JSON messages over the WebSocket in this specific format:

{
  "source": "CORE" | "WORKER" | "OCR_SERVICE",
  "type": "INFO" | "ERROR" | "PROGRESS" | "PROCESS_COMPLETE",
  "message": "Human readable string",
  "payload": {
    "percent": 45,             // For progress bars
    "details": "...",          // For errors
    "scanResult": { ... }      // For completion
  }
}


4. Checklist for Launch

[ ] Start Backend: Run uvicorn app.main:app --reload

[ ] Start Frontend: Run your React dev server (e.g., npm start or vite).

[ ] Verify Connection: Check the "Debug Tools" tab in the UI. You should see a "Connected to Backend Bus" message immediately upon load.

[ ] Test Scan: Enter a path and click Run. Watch the Python console logs to ensure the request was received, and watch the UI to see the progress bar update via WebSocket messages.