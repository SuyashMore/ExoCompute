import argparse
import subprocess
import threading
import requests
import time
import signal
import sys
from fastapi import FastAPI, Request
import uvicorn
from importlib import import_module
from libs.base import ComputeUnit
from fastapi.responses import JSONResponse

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
async def compute_handler(req: Request):
    global is_busy
    is_busy = True
    print("[SUB] Received /compute request")
    try:
        body = await req.json()
        print(f"[SUB] Request JSON: {body}")

        unit_type = body.get("unit")
        data = body.get("input")

        if not unit_type or not data:
            print(f"[SUB] Missing 'unit' or 'input' in payload: unit={unit_type}, input={data}")
            return JSONResponse(content={"error": "Missing 'unit' or 'input'"}, status_code=400)

        try:
            module = import_module(f"libs.{unit_type.lower()}")
            unit_class: type[ComputeUnit] = getattr(module, unit_type)
            print(f"[SUB] Successfully imported: libs.{unit_type.lower()} and found class {unit_type}")
        except Exception as e:
            print(f"[SUB] Import failed for unit '{unit_type}': {e}")
            return JSONResponse(content={"error": f"Invalid compute unit '{unit_type}': {e}"}, status_code=400)

        try:
            input_obj = unit_class.Input(**data)
            print(f"[SUB] Successfully parsed input: {input_obj}")
        except Exception as e:
            print(f"[SUB] Failed to parse input: {e}")
            return JSONResponse(content={"error": f"Failed to parse input for '{unit_type}': {e}"}, status_code=400)

        try:
            unit_instance = unit_class()
            print(f"[SUB] Instantiated unit class: {unit_instance}")
            output_obj = unit_instance.compute(input_obj)
            print(f"[SUB] Computation successful: {output_obj}")
            return JSONResponse(content=output_obj.dict())
        except Exception as e:
            print(f"[SUB] Exception during compute(): {e}")
            return JSONResponse(content={"error": f"Failed to compute: {e}"}, status_code=500)

    except Exception as e:
        print(f"[SUB] Unexpected failure in /compute handler: {e}")
        return JSONResponse(content={"error": f"Unexpected error: {e}"}, status_code=500)

    finally:
        is_busy = False
        print("[SUB] Marked as not busy")

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

@app.get("/health")
def health():
    return {"busy": busy}


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
