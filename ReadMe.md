# ExoCompute - Distributed Compute Grid

Welcome to the **ExoCompute** prototype — a proof-of-concept for a decentralized computation network, where lightweight nodes subscribe to a central orchestrator and perform tasks on-demand.

> Think: a minimal version of Kubernetes meets BOINC, powered by Python + FastAPI.

---

## ⚙️ Modular Architecture

The project has been refactored into a specific python package `exocompute`:

- **`src/exocompute/orchestrator`**: The central brain.
    - `server.py`: FastAPI application.
    - `manager.py`: Manages node health and busy/free state.
    - `scheduler.py`: Distributes tasks to available nodes.
- **`src/exocompute/subscriber`**: The compute nodes.
    - `core.py`: Subscriber logic (registration, heartbeat).
    - `server.py`: FastAPI node server.
- **`src/exocompute/client`**: Client library for connecting to the grid.
- **`user.py`**: Example user script that submits tasks.

---

## 🚀 Quick Start

### 1. Setup
```bash
# Clone and enter directory
git clone https://github.com/yourname/distributed-compute-prototype.git
cd distributed-compute-prototype

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Services
Since the project is now a package, you should run modules using `-m`.

**Terminal 1: Start Orchestrator**
```bash
# Ensure src is in PYTHONPATH if not installed as editable
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m exocompute.orchestrator
```

**Terminal 2: Start Subscribers**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
# Launch 1 subscriber
python3 -m exocompute.subscriber --count 1
```

### 3. Run Compute Task
**Terminal 3: User Script**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 user.py
```

---

## 🧪 Testing

We have a robust test suite covering unit logic and full system integration.

**Run Unit Tests:**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m unittest discover tests/unit
```

**Run Integration Tests:**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m unittest tests/integration/test_system.py
```

---

## 🧠 Features

- � **Resilient Scheduling**: Tasks are retried if nodes fail or are busy.
- � **Dynamic Registry**: Nodes register/unregister dynamically.
- 🔥 **Modular Units**: Compute logic is pluggable via `libs`.
- 🧪 **Test Coverage**: End-to-end integration tests ensures stability.

---

## 📁 Project Structure

```
.
├── src/
│   └── exocompute/
│       ├── orchestrator/   # Node Management & Scheduling
│       ├── subscriber/     # Compute Node Logic
│       ├── client/         # Client SDK
│       └── libs/           # Compute Units (Mul, Add, etc.)
├── tests/
│   ├── unit/              # Component tests
│   └── integration/       # End-to-end usage tests
├── user.py                # Usage example
├── requirements.txt
└── README.md
```

---

## ⚠️ Disclaimer

This is a **prototype**, not a production system. You *will* break things. That’s the point.

---

## 🧑‍💻 Author

Made with caffeine and contempt for centralization by [Suyash].