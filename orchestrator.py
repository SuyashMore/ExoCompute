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
PORT_RANGE = list(range(9000, 9050))
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


MAX_RETRIES = 100
RETRY_DELAY = 0.5  # in seconds

@app.post("/submit_task")
async def submit_task(req: Request):
    data = await req.json()
    a, b = data.get("a"), data.get("b")

    for attempt in range(MAX_RETRIES):
        attempted_ports = set()

        while True:
            with lock:
                available_nodes = [
                    port for port, busy in busy_state.items()
                    if not busy and port not in attempted_ports
                ]

            if not available_nodes:
                break  # No more nodes left to try in this round

            for port in available_nodes:
                try:
                    async with httpx.AsyncClient(timeout=2.0) as client:
                        with lock:
                            busy_state[port] = True
                        r = await client.post(f"http://localhost:{port}/compute", json={"a": a, "b": b})
                        result = r.json().get("result")
                        with lock:
                            busy_state[port] = False
                        return {"result": result}
                except Exception as e:
                    print(f"[ORCH] Error with port {port}: {e}")
                    attempted_ports.add(port)
                    with lock:
                        busy_state[port] = False

        print(f"[ORCH] No available subscribers, retrying ({attempt+1}/{MAX_RETRIES})...")
        await asyncio.sleep(RETRY_DELAY)

    return JSONResponse(status_code=503, content={"error": "All retries failed: No available subscribers"})


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
