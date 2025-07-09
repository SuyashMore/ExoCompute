import argparse
import subprocess
import threading
import requests
import time
import signal
import sys
from fastapi import FastAPI, Request
import uvicorn
from lib import add_numbers as add

# ---------------------
# GLOBALS
# ---------------------
orchestrator_url = "http://localhost:8000"
busy = False
assigned_port = None
shutdown_flag = False
heartbeat_thread = None

# ---------------------
# FASTAPI SETUP
# ---------------------
app = FastAPI()

@app.post("/compute")
async def compute(request: Request):
    global busy
    data = await request.json()
    a, b = data.get("a"), data.get("b")
    print(f"[SUB] Received compute: add({a}, {b})")
    busy = True
    result = add(a, b)
    busy = False
    return {"result": result}

@app.get("/health")
def health():
    print(f"[SUB] Health check received. Busy: {busy}")
    return {"status": "ok", "busy": busy}


# ---------------------
# REGISTRATION
# ---------------------
def register_with_orchestrator():
    try:
        r = requests.get(f"{orchestrator_url}/get_port")
        port = r.json().get("port")
        print(f"[SUB] Got assigned port: {port}")
        return port
    except Exception as e:
        print(f"[SUB] Registration failed: {e}")
        return None

def unregister():
    if assigned_port:
        try:
            requests.post(f"{orchestrator_url}/unregister", json={"port": assigned_port})
            print(f"[SUB] Unregistered from orchestrator (port {assigned_port})")
        except Exception as e:
            print(f"[SUB] Failed to unregister: {e}")


# ---------------------
# HEARTBEAT
# ---------------------
def heartbeat():
    while not shutdown_flag:
        try:
            requests.post(f"{orchestrator_url}/health_check", json={"port": assigned_port})
        except Exception as e:
            print(f"[SUB] Heartbeat failed: {e}")
        time.sleep(5)


# ---------------------
# CLEAN SHUTDOWN HANDLER
# ---------------------
def handle_exit(signum, frame):
    global shutdown_flag
    shutdown_flag = True
    print("\n[SUB] Caught shutdown signal, cleaning up...")
    unregister()
    sys.exit(0)


# ---------------------
# MAIN SUBSCRIBER LAUNCH
# ---------------------
def start_subscriber():
    global assigned_port, heartbeat_thread
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    assigned_port = register_with_orchestrator()
    if not assigned_port:
        print("[SUB] No port assigned. Exiting.")
        return

    heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
    heartbeat_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=assigned_port)


# ---------------------
# MULTI-LAUNCH
# ---------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    if args.count == 1:
        start_subscriber()
    else:
        processes = []
        for _ in range(args.count):
            proc = subprocess.Popen(["python", "sub.py"])
            processes.append(proc)

        def multi_kill(sig, frame):
            print("\n[SPAWN] Shutting down all subprocesses...")
            for p in processes:
                p.terminate()
            sys.exit(0)

        signal.signal(signal.SIGINT, multi_kill)
        signal.signal(signal.SIGTERM, multi_kill)

        while True:
            time.sleep(1)
