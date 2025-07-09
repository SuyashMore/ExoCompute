# sub.py

import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import threading
import argparse
import time
import random
import logging
from lib import add_numbers  # our compute logic

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] SUB-%(name)s - %(message)s",
    datefmt="%H:%M:%S"
)

app_template = FastAPI()
busy_status = {}

class ComputeRequest(BaseModel):
    a: int
    b: int

def create_app(port):

    app = FastAPI()
    name = f"{port}"
    busy_status[port] = False

    @app.get("/health")
    def health():
        logging.info(f"[{name}] Health check received.")
        return {"status": "ok"}

    @app.post("/compute")
    def compute(req: ComputeRequest):
        if busy_status[port]:
            return {"error": "Busy"}
        logging.info(f"[{name}] Received compute: {req.a} + {req.b}")
        busy_status[port] = True
        try:
            result = add_numbers(req.a, req.b)
            return {"result": result}
        finally:
            busy_status[port] = False

    return app

def launch_instance(index):
    try:
        # Register with orchestrator
        r = requests.post("http://localhost:8000/register", json={})
        r.raise_for_status()
        data = r.json()
        port = data["port"]
        logging.info(f"Subscriber-{index} launched at port {port}")
        app = create_app(port)
        uvicorn.run(app, host="localhost", port=port)
    except Exception as e:
        logging.error(f"Failed to launch Subscriber-{index}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1, help="Number of subscriber instances to spawn")
    args = parser.parse_args()

    for i in range(args.count):
        threading.Thread(target=launch_instance, args=(i,), daemon=True).start()

    # Block forever
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
