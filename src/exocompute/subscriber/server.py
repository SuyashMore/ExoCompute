from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import signal
import sys
from contextlib import asynccontextmanager

from .core import SubscriberNode

node = SubscriberNode()

def handle_exit(sig, frame):
    print("\n[SUB] Caught shutdown signal, cleaning up...")
    node.unregister()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if node.assigned_port:
        node.start_heartbeat()
    yield
    node.stop_heartbeat()
    node.unregister()

app = FastAPI(lifespan=lifespan)

@app.post("/compute")
async def compute_handler(req: Request):
    try:
        body = await req.json()
        unit_type = body.get("unit")
        data = body.get("input")

        if not unit_type or not data:
            return JSONResponse(content={"error": "Missing 'unit' or 'input'"}, status_code=400)

        result = node.process_compute(unit_type, data)
        return JSONResponse(content=result)

    except ValueError as e:
         return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/health")
def health():
    return {"busy": node.busy}

def run_subscriber_server(assigned_port, subscriber_node):
    # We replace the global node with the one registered in the wrapper
    global node
    node = subscriber_node
    uvicorn.run(app, host="0.0.0.0", port=assigned_port)
