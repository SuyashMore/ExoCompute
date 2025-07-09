import uvicorn
import signal
import sys
import threading
import time
import httpx
from fastapi import FastAPI, Request
import asyncio
from fastapi.responses import JSONResponse
import requests

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

RETRY_LIMIT = 100
RETRY_DELAY = 0.1  # seconds
REDUNDANCY_FACTOR = 2  # how many subs we ask at once

@app.post("/submit_task")
async def submit_task(req: Request):
    import requests

    payload = await req.json()
    attempted_ports = set()

    for attempt in range(RETRY_LIMIT):
        ports_to_try = []

        with lock:
            available_nodes = [
                port for port, busy in busy_state.items()
                if not busy and port not in attempted_ports
            ]
            if not available_nodes:
                print(f"[ORCH] No available nodes, sleeping...")
            else:
                for port in available_nodes[:REDUNDANCY_FACTOR]:
                    busy_state[port] = True  # Mark as busy immediately
                    ports_to_try.append(port)

        if not ports_to_try:
            await asyncio.sleep(RETRY_DELAY)
            continue

        tasks = []

        for port in ports_to_try:
            def send_to_port(p=port):  # capture port value
                try:
                    print(f"[ORCH] Sending task to port {p}")
                    resp = requests.post(f"http://localhost:{p}/compute", json=payload, timeout=2.0)
                    print(f"[ORCH] Response from port {p}: {resp.text}")
                    return p, resp.json()
                except Exception as e:
                    print(f"[ORCH] Error with port {p}: {e}")
                    return p, None
                finally:
                    with lock:
                        busy_state[p] = False

            tasks.append(asyncio.create_task(asyncio.to_thread(send_to_port)))

        done, _ = await asyncio.wait(tasks)

        for d in done:
            port_used, result = await d
            attempted_ports.add(port_used)
            if result and "result" in result:
                print(f"[ORCH] Success from {port_used}")
                return {"result": result["result"]}

        print(f"[ORCH] Attempt {attempt + 1}/{RETRY_LIMIT} failed. Retrying...")
        await asyncio.sleep(RETRY_DELAY)

    return JSONResponse(status_code=503, content={"error": "No available subscribers or all failed"})

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
