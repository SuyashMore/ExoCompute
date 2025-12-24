from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from .manager import NodeManager
from .scheduler import TaskScheduler

node_manager = NodeManager()
scheduler = TaskScheduler(node_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[ORCH] Starting orchestrator...")
    node_manager.start_health_check()
    yield
    print("[ORCH] Stopping orchestrator...")
    node_manager.stop_health_check()

app = FastAPI(lifespan=lifespan)

# -------------------------
# API Endpoints
# -------------------------
@app.get("/get_port")
async def get_port():
    port = await node_manager.get_available_port()
    if port:
        return {"port": port}
    return JSONResponse(status_code=503, content={"error": "No ports available"})

@app.post("/submit_task")
async def submit_task(req: Request):
    payload = await req.json()
    try:
        result = await scheduler.submit_task(payload)
        return result
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": str(e)})

@app.post("/unregister")
async def unregister_node(data: dict):
    port = data.get("port")
    await node_manager.unregister_node(port)
    return {"status": "ok"}

@app.post("/health_check")
async def health_check_from_subscriber(data: dict):
    port = data.get("port")
    await node_manager.heartbeat(port)
    return {"status": "ok"}

def run_server(host="0.0.0.0", port=8000):
    uvicorn.run(app, host=host, port=port)
