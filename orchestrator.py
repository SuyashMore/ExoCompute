# orchestrator.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
import threading
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI()

class Subscriber(BaseModel):
    url: str
    port: int
    busy: bool = False
    alive: bool = True

subscribers = []
available_ports = list(range(8001, 8100))

class SingleComputeRequest(BaseModel):
    a: int
    b: int

@app.post("/register")
def register_subscriber(_: dict):
    if not available_ports:
        raise HTTPException(status_code=503, detail="No ports available")
    assigned_port = available_ports.pop(0)
    url = f"http://localhost:{assigned_port}"
    sub = Subscriber(url=url, port=assigned_port)
    subscribers.append(sub)
    logging.info(f"New subscriber registered at {url}")
    return {"status": "registered", "url": url, "port": assigned_port}

def health_check():
    while True:
        for sub in subscribers[:]:
            try:
                r = requests.get(f"{sub.url}/health", timeout=2)
                sub.alive = r.status_code == 200
            except:
                if sub.alive:
                    logging.warning(f"Subscriber {sub.url} is DOWN")
                sub.alive = False
                if sub.port not in available_ports:
                    available_ports.append(sub.port)
                    logging.info(f"Freed port {sub.port} from dead subscriber {sub.url}")
        time.sleep(5)

@app.post("/compute")
def compute(req: SingleComputeRequest):
    if not subscribers:
        raise HTTPException(status_code=503, detail="No subscribers available")

    logging.info("Received compute request")

    payload = {"a": req.a, "b": req.b}
    target = next((s for s in subscribers if s.alive and not s.busy), None)
    if not target:
        raise HTTPException(status_code=503, detail="No healthy and idle subscribers")

    target.busy = True
    try:
        r = requests.post(f"{target.url}/compute", json=payload, timeout=5)
        r.raise_for_status()
        return {"result": r.json()["result"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compute failed: {e}")
    finally:
        target.busy = False

@app.get("/subscribers")
def list_subs():
    return [{"url": s.url, "port": s.port, "alive": s.alive, "busy": s.busy} for s in subscribers]

if __name__ == "__main__":
    threading.Thread(target=health_check, daemon=True).start()
    uvicorn.run(app, host="localhost", port=8000)
