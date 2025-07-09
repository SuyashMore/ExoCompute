import uvicorn
import signal
import sys
import threading
import time
import httpx
from fastapi import FastAPI, Request
import asyncio
from fastapi.responses import JSONResponse

app = FastAPI()

subscribers = {}
busy_state = {}
PORT_RANGE = list(range(9000, 9250))
lock = threading.Lock()

# -------------------------
# Graceful shutdown control
# -------------------------
shutdown_flag = False
health_thread = None

def health_check_loop():
    global shutdown_flag
    while not shutdown_flag:
        with lock:
            to_remove = []
            for port, last_seen in list(subscribers.items()):
                try:
                    import requests
                    r = requests.get(f"http://localhost:{port}/health", timeout=1)
                    is_busy = r.json().get("busy", False)
                    busy_state[port] = is_busy
                except:
                    print(f"[ORCH] Node on port {port} is down")
                    to_remove.append(port)
            for port in to_remove:
                del subscribers[port]
                busy_state.pop(port, None)
        time.sleep(3)

def handle_exit(sig, frame):
    global shutdown_flag
    shutdown_flag = True
    print("\n[ORCH] Shutting down orchestrator gracefully...")
    sys.exit(0)


# -------------------------
# Register Shutdown Hooks
# -------------------------
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# -------------------------
# API Endpoints
# -------------------------
@app.get("/get_port")
def get_port():
    with lock:
        for port in PORT_RANGE:
            if port not in subscribers:
                subscribers[port] = time.time()
                busy_state[port] = False
                print(f"[ORCH] Assigned port {port}")
                return {"port": port}
    return JSONResponse(status_code=503, content={"error": "No ports available"})


REDUNDANCY_FACTOR = 3
MAX_RETRIES = 100
RETRY_DELAY = 0.5  # seconds

@app.post("/submit_task")
async def submit_task(req: Request):
    data = await req.json()
    a, b = data.get("a"), data.get("b")

    for attempt in range(MAX_RETRIES):
        with lock:
            available_nodes = [
                port for port, busy in busy_state.items()
                if not busy
            ]

        if not available_nodes:
            print(f"[ORCH] No subscribers available (attempt {attempt+1})")
            await asyncio.sleep(RETRY_DELAY)
            continue

        selected_ports = available_nodes[:REDUNDANCY_FACTOR]

        # Pre-mark as busy
        with lock:
            for port in selected_ports:
                busy_state[port] = True

        tasks = [
            asyncio.create_task(dispatch_compute(port, a, b))
            for port in selected_ports
        ]

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()

        for task in done:
            result = task.result()
            if result is not None:
                return {"result": result}

        print(f"[ORCH] All redundancy nodes failed (attempt {attempt+1})")
        await asyncio.sleep(RETRY_DELAY)

    return JSONResponse(status_code=503, content={"error": "No available subscribers"})

async def dispatch_compute(port, a, b):
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.post(f"http://localhost:{port}/compute", json={"a": a, "b": b})
            if r.status_code == 200:
                return r.json().get("result")
    except Exception as e:
        print(f"[ORCH] Dispatch error on port {port}: {e}")
    finally:
        with lock:
            busy_state[port] = False


@app.post("/unregister")
def unregister_node(data: dict):
    port = data.get("port")
    with lock:
        if port in subscribers:
            del subscribers[port]
            busy_state.pop(port, None)
            print(f"[ORCH] Port {port} unregistered")
    return {"status": "ok"}

@app.post("/health_check")
def health_check_from_subscriber(data: dict):
    port = data.get("port")
    with lock:
        if port in subscribers:
            subscribers[port] = time.time()
    return {"status": "ok"}

# -------------------------
# Main Entrypoint
# -------------------------
if __name__ == "__main__":
    print("[ORCH] Starting orchestrator...")

    health_thread = threading.Thread(target=health_check_loop, daemon=True)
    health_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)
