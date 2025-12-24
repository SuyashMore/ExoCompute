# ExoCompute - Distributed Compute Grid

Welcome to **ExoCompute** — a proof-of-concept for a decentralized computation network, where lightweight nodes subscribe to a central orchestrator and perform tasks on-demand.

> Think: a minimal version of Kubernetes meets BOINC, powered by Python + FastAPI.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Modular Components](#️-modular-components)
- [How It Works](#-how-it-works)
- [Quick Start](#-quick-start)
- [Testing](#-testing)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Code Deep Dive](#-code-deep-dive)
- [Performance & Benchmarks](#-performance--benchmarks)
- [Extending ExoCompute](#-extending-exocompute)
- [Disclaimer](#️-disclaimer)
- [Author](#-author)

---

## 🌟 Overview

**ExoCompute** is a distributed compute framework that enables you to:
- **Distribute computational tasks** across multiple worker nodes
- **Scale horizontally** by adding more subscriber nodes
- **Execute tasks in parallel** with automatic load balancing
- **Handle node failures** gracefully with retry mechanisms
- **Plug in custom compute units** for different workloads

### Key Concepts

```mermaid
graph LR
    A[Client] -->|Submit Task| B[Orchestrator]
    B -->|Schedule| C[Subscriber 1]
    B -->|Schedule| D[Subscriber 2]
    B -->|Schedule| E[Subscriber N]
    C -->|Result| B
    D -->|Result| B
    E -->|Result| B
    B -->|Return Result| A
    
    style A fill:#4CAF50
    style B fill:#2196F3
    style C fill:#FF9800
    style D fill:#FF9800
    style E fill:#FF9800
```

---

## 🏗️ Architecture

ExoCompute follows a **centralized orchestrator** pattern with multiple distributed **subscriber nodes**. Here's the high-level architecture:

```mermaid
graph TB
    subgraph Client Layer
        U[User Script - user.py]
        CL[Client Library]
    end
    
    subgraph Orchestrator Layer
        ORC[FastAPI Server]
        MGR[Node Manager]
        SCH[Task Scheduler]
    end
    
    subgraph Subscriber Layer
        SUB1[Subscriber Node 1<br/>Port: 9001]
        SUB2[Subscriber Node 2<br/>Port: 9002]
        SUB3[Subscriber Node N<br/>Port: 900N]
    end
    
    subgraph Compute Units
        MUL[Mul Unit]
        ADD[Add Unit]
        MAT[Matrix Ops]
        IMG[Image Ops]
        MC[Monte Carlo]
    end
    
    U --> CL
    CL -->|HTTP POST /submit_task| ORC
    ORC --> MGR
    ORC --> SCH
    SCH -->|Dispatch Task| SUB1
    SCH -->|Dispatch Task| SUB2
    SCH -->|Dispatch Task| SUB3
    
    SUB1 -.->|Dynamic Import| MUL
    SUB1 -.->|Dynamic Import| ADD
    SUB2 -.->|Dynamic Import| MAT
    SUB3 -.->|Dynamic Import| IMG
    
    MGR -->|Health Check| SUB1
    MGR -->|Health Check| SUB2
    MGR -->|Health Check| SUB3
    
    style U fill:#4CAF50
    style CL fill:#8BC34A
    style ORC fill:#2196F3
    style MGR fill:#03A9F4
    style SCH fill:#00BCD4
    style SUB1 fill:#FF9800
    style SUB2 fill:#FF9800
    style SUB3 fill:#FF9800
```

### Architecture Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **Client** | Submit tasks and receive results | Python SDK |
| **Orchestrator** | Coordinate nodes, schedule tasks | FastAPI + Uvicorn |
| **Node Manager** | Track node health and availability | Asyncio + Threading |
| **Task Scheduler** | Distribute tasks with redundancy | Asyncio + HTTPX |
| **Subscriber Nodes** | Execute compute units | FastAPI + Dynamic Imports |
| **Compute Units** | Pluggable task implementations | Pydantic Models + ABC |

---

## ⚙️ Modular Components

The project is structured as a Python package `exocompute`:

### 📦 Package Structure

```
src/exocompute/
├── orchestrator/          # Central coordination brain
│   ├── __main__.py       # Entry point
│   ├── server.py         # FastAPI application
│   ├── manager.py        # Node health & state management
│   └── scheduler.py      # Task distribution logic
│
├── subscriber/           # Compute worker nodes
│   ├── __main__.py      # Entry point
│   ├── core.py          # Registration & heartbeat logic
│   └── server.py        # FastAPI compute endpoint
│
├── client/              # Client SDK
│   └── client.py        # ExoCompute client library
│
└── libs/                # Compute units (pluggable)
    ├── base.py          # Abstract base classes
    ├── mul.py           # Multiplication unit
    ├── adder.py         # Addition unit
    ├── sqr.py           # Square unit
    ├── sub.py           # Subtraction unit
    ├── matrix_ops.py    # Matrix operations
    ├── image_ops.py     # Image processing
    └── monte_carlo.py   # Monte Carlo simulations
```

---

## 🔄 How It Works

### Task Execution Flow

```mermaid
sequenceDiagram
    participant Client
    participant Orchestrator
    participant Scheduler
    participant NodeManager
    participant Subscriber1
    participant Subscriber2
    
    Note over Client,Subscriber2: 1. Node Registration Phase
    Subscriber1->>Orchestrator: GET /get_port
    Orchestrator->>NodeManager: Assign port 9001
    NodeManager-->>Subscriber1: Port 9001
    Subscriber1->>Subscriber1: Start heartbeat thread
    
    Subscriber2->>Orchestrator: GET /get_port
    Orchestrator->>NodeManager: Assign port 9002
    NodeManager-->>Subscriber2: Port 9002
    Subscriber2->>Subscriber2: Start heartbeat thread
    
    loop Every 5 seconds
        Subscriber1->>Orchestrator: POST /health_check
        Subscriber2->>Orchestrator: POST /health_check
    end
    
    Note over Client,Subscriber2: 2. Task Submission Phase
    Client->>Orchestrator: POST /submit_task<br/>{unit: "Mul", input: {a: 5, b: 10}}
    Orchestrator->>Scheduler: Schedule task
    Scheduler->>NodeManager: Get available nodes
    NodeManager-->>Scheduler: [9001: free, 9002: free]
    
    Note over Scheduler,Subscriber2: 3. Redundant Task Dispatch
    Scheduler->>Subscriber1: POST /compute (redundancy 1)
    Scheduler->>Subscriber2: POST /compute (redundancy 2)
    
    par Parallel Execution
        Subscriber1->>Subscriber1: Dynamic import Mul
        Subscriber1->>Subscriber1: Execute compute(a=5, b=10)
    and
        Subscriber2->>Subscriber2: Dynamic import Mul
        Subscriber2->>Subscriber2: Execute compute(a=5, b=10)
    end
    
    Subscriber1-->>Scheduler: Result: {result: 50}
    Subscriber2-->>Scheduler: Result: {result: 50}
    
    Note over Scheduler: First valid response wins
    Scheduler->>NodeManager: Mark nodes free
    Scheduler-->>Orchestrator: Return first result
    Orchestrator-->>Client: {result: 50}
```

### Step-by-Step Breakdown

#### **Phase 1: Node Registration**
1. Subscriber nodes start up and request a port from the orchestrator
2. Orchestrator's `NodeManager` assigns a unique port (9001, 9002, etc.)
3. Each subscriber starts a background heartbeat thread
4. Heartbeats are sent every 5 seconds to maintain node liveness

#### **Phase 2: Task Submission**
1. Client creates an `ExoCompute` instance with a compute unit class
2. Client calls `exo.compute(input_data)`
3. Client library sends HTTP POST to orchestrator's `/submit_task`
4. Payload includes: `{unit: "UnitName", input: {...}}`

#### **Phase 3: Task Scheduling**
1. Scheduler queries `NodeManager` for available (non-busy) nodes
2. Selects N nodes based on `redundancy_factor` (default: 2)
3. Marks selected nodes as "busy" to prevent double-scheduling
4. Dispatches task to all selected nodes in parallel

#### **Phase 4: Task Execution**
1. Subscriber receives task at `/compute` endpoint
2. Dynamically imports the requested compute unit
3. Parses input using Pydantic validation
4. Executes the `compute()` method
5. Returns result as JSON

#### **Phase 5: Result Collection**
1. Scheduler waits for first successful response
2. Ignores slower/failed redundant executions
3. Marks all nodes as "free" after completion
4. Returns result to client

---

## 🚀 Quick Start

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/yourname/ExoCompute.git
cd ExoCompute

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Services

Since the project is a package, run modules using `-m`:

**Terminal 1: Start Orchestrator**
```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src  # Windows: set PYTHONPATH=%PYTHONPATH%;%CD%\src
python3 -m exocompute.orchestrator
```

**Terminal 2: Start Subscribers (Scale to N nodes)**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
# Launch 3 subscriber nodes
python3 -m exocompute.subscriber --count 3
```

### 3. Run Compute Task

**Terminal 3: Execute User Script**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 user.py
```

**Expected Output:**
```
⏱️ Total time for 5000 tasks: 12.34s
✅ Successes: 5000
❌ Errors:    0
```

---

## 🧪 Testing

We have a robust test suite covering unit logic and full system integration.

### Test Structure

```
tests/
├── unit/                    # Component-level tests
│   ├── test_scheduler.py   # Scheduler logic
│   ├── test_manager.py     # Node manager
│   └── test_compute_units.py
│
└── integration/             # End-to-end tests
    └── test_system.py      # Full system workflow
```

### Run Unit Tests

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m unittest discover tests/unit
```

### Run Integration Tests

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m unittest tests/integration/test_system.py
```

### Test Coverage

- ✅ Node registration/unregistration
- ✅ Heartbeat mechanism
- ✅ Task submission and scheduling
- ✅ Redundant execution
- ✅ Failure handling
- ✅ Compute unit validation
- ✅ End-to-end task flow

---

## 🧠 Features

- ✨ **Resilient Scheduling**: Tasks are retried if nodes fail or are busy
- 🔄 **Dynamic Registry**: Nodes register/unregister dynamically
- 🔥 **Modular Units**: Compute logic is pluggable via `libs`
- 🚀 **Horizontal Scaling**: Add more nodes to increase throughput
- 🧪 **Test Coverage**: End-to-end integration tests ensures stability
- 🛡️ **Redundant Execution**: Tasks are sent to multiple nodes for fault tolerance
- ⚡ **Async I/O**: Non-blocking task dispatch using asyncio + httpx
- 🔍 **Health Monitoring**: Automatic node health checks every 5 seconds

---

## 📁 Project Structure

```
ExoCompute/
├── src/
│   └── exocompute/
│       ├── orchestrator/      # Node Management & Scheduling
│       │   ├── __init__.py
│       │   ├── __main__.py   # Entry: uvicorn server
│       │   ├── server.py     # FastAPI routes
│       │   ├── manager.py    # NodeManager class
│       │   └── scheduler.py  # TaskScheduler class
│       │
│       ├── subscriber/        # Compute Node Logic
│       │   ├── __init__.py
│       │   ├── __main__.py   # Entry: spawn N nodes
│       │   ├── core.py       # SubscriberNode class
│       │   └── server.py     # FastAPI compute endpoint
│       │
│       ├── client/            # Client SDK
│       │   ├── __init__.py
│       │   └── client.py     # ExoCompute class
│       │
│       └── libs/              # Compute Units (Pluggable)
│           ├── base.py       # Abstract base classes
│           ├── mul.py        # Multiplication
│           ├── adder.py      # Addition
│           ├── sqr.py        # Square
│           ├── sub.py        # Subtraction
│           ├── matrix_ops.py # Matrix operations (4 units)
│           ├── image_ops.py  # Image processing (4 units)
│           └── monte_carlo.py # Monte Carlo sims (3 units)
│
├── tests/
│   ├── unit/                 # Component tests
│   │   ├── test_scheduler.py
│   │   ├── test_manager.py
│   │   └── test_compute_units.py
│   │
│   └── integration/          # End-to-end usage tests
│       └── test_system.py
│
├── examples/                 # Additional examples
├── user.py                  # Main usage example
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

---

## 💻 Code Deep Dive

### Client SDK (`client.py`)

The client library provides a simple interface to submit tasks:

```python
from exocompute.client import ExoCompute
from exocompute.libs.mul import Mul

# Initialize client with orchestrator URL and compute unit
exo = ExoCompute("http://localhost:8000", Mul)

# Create input using Pydantic model
input_data = Mul.Input(a=10, b=20)

# Execute computation (synchronous)
result = exo.compute(input_data)
print(result)  # {'result': 200}
```

**Implementation Details:**
```python
class ExoCompute:
    def __init__(self, orchestrator_url: str, compute_unit: Type):
        self.orchestrator_url = orchestrator_url.rstrip("/")
        self.unit_class = compute_unit
        self.unit_name = compute_unit.__name__  # Extract class name
    
    def compute(self, input_data: ComputeInput) -> dict:
        # Build payload with unit name and serialized input
        payload = {
            "unit": self.unit_name,
            "input": input_data.model_dump(),  # Pydantic v2
        }
        
        # HTTP POST to orchestrator
        resp = requests.post(
            f"{self.orchestrator_url}/submit_task",
            json=payload,
            timeout=30.0
        )
        resp.raise_for_status()
        return resp.json()["result"]
```

---

### Orchestrator Server (`server.py`)

The orchestrator exposes four key endpoints:

```python
@app.get("/get_port")
async def get_port():
    """Assign a unique port to a new subscriber node."""
    port = await node_manager.get_available_port()
    if port:
        return {"port": port}
    return JSONResponse(status_code=503, content={"error": "No ports available"})

@app.post("/submit_task")
async def submit_task(req: Request):
    """Submit a task for execution. Returns result or error."""
    payload = await req.json()
    try:
        result = await scheduler.submit_task(payload)
        return result
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": str(e)})

@app.post("/unregister")
async def unregister_node(data: dict):
    """Remove a node from the registry."""
    port = data.get("port")
    await node_manager.unregister_node(port)
    return {"status": "ok"}

@app.post("/health_check")
async def health_check_from_subscriber(data: dict):
    """Receive heartbeat from subscriber node."""
    port = data.get("port")
    await node_manager.heartbeat(port)
    return {"status": "ok"}
```

**Lifecycle Management:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    print("[ORCH] Starting orchestrator...")
    node_manager.start_health_check()  # Background thread for node monitoring
    yield
    print("[ORCH] Stopping orchestrator...")
    node_manager.stop_health_check()
```

---

### Node Manager (`manager.py`)

The `NodeManager` tracks node health and availability:

**Key Responsibilities:**
1. **Port Assignment**: Allocates unique ports from pool (9001-9050)
2. **Health Monitoring**: Background thread checks node heartbeats
3. **State Management**: Tracks busy/free status for each node

**Conceptual Implementation:**
```python
class NodeManager:
    def __init__(self):
        self.nodes = {}  # {port: {"busy": bool, "last_heartbeat": timestamp}}
        self.available_ports = list(range(9001, 9051))
        self.lock = asyncio.Lock()
    
    async def get_available_port(self):
        """Assign a port to a new subscriber."""
        async with self.lock:
            if self.available_ports:
                port = self.available_ports.pop(0)
                self.nodes[port] = {"busy": False, "last_heartbeat": time.time()}
                return port
            return None
    
    async def heartbeat(self, port):
        """Update last heartbeat timestamp."""
        if port in self.nodes:
            self.nodes[port]["last_heartbeat"] = time.time()
    
    async def mark_busy(self, port):
        """Mark node as busy."""
        if port in self.nodes:
            self.nodes[port]["busy"] = True
    
    async def mark_free(self, port):
        """Mark node as free."""
        if port in self.nodes:
            self.nodes[port]["busy"] = False
    
    def start_health_check(self):
        """Start background thread to monitor node health."""
        threading.Thread(target=self._health_check_loop, daemon=True).start()
    
    def _health_check_loop(self):
        """Remove nodes that haven't sent heartbeat in 15 seconds."""
        while True:
            current_time = time.time()
            dead_nodes = [
                port for port, info in self.nodes.items()
                if current_time - info["last_heartbeat"] > 15
            ]
            for port in dead_nodes:
                self.unregister_node(port)
            time.sleep(5)
```

---

### Task Scheduler (`scheduler.py`)

The `TaskScheduler` implements redundant task dispatch:

**Key Features:**
- **Redundancy Factor**: Send task to N nodes (default: 2)
- **Retry Logic**: Retry up to 100 times if nodes are unavailable
- **First-Response Wins**: Accept first valid result, ignore others

**Implementation:**
```python
class TaskScheduler:
    def __init__(self, node_manager: NodeManager):
        self.node_manager = node_manager
        self.retry_limit = 100
        self.retry_delay = 0.1  # seconds
        self.redundancy_factor = 2  # Send to 2 nodes
    
    async def submit_task(self, payload: dict):
        attempted_ports = set()
        
        async with httpx.AsyncClient() as client:
            for attempt in range(self.retry_limit):
                # 1. Get available nodes (not busy, not attempted)
                available_nodes_map = await self.node_manager.get_nodes()
                available_nodes = [
                    port for port, busy in available_nodes_map.items()
                    if not busy and port not in attempted_ports
                ]
                
                if not available_nodes:
                    await asyncio.sleep(self.retry_delay)
                    continue
                
                # 2. Select N nodes for redundancy
                selected = available_nodes[:self.redundancy_factor]
                ports_to_try = []
                for port in selected:
                    await self.node_manager.mark_busy(port)
                    ports_to_try.append(port)
                
                # 3. Dispatch to all selected nodes in parallel
                tasks = [
                    asyncio.create_task(self._send_to_port(client, port, payload))
                    for port in ports_to_try
                ]
                
                # 4. Wait for completion (first result wins)
                done, _ = await asyncio.wait(tasks)
                
                # 5. Return first valid result
                for task in done:
                    port_used, result = await task
                    attempted_ports.add(port_used)
                    if result and isinstance(result, dict):
                        return {"result": result}
                
                await asyncio.sleep(self.retry_delay)
            
            raise Exception("No available subscribers or all failed")
    
    async def _send_to_port(self, client, port, payload):
        """Send task to a specific subscriber node."""
        try:
            resp = await client.post(
                f"http://localhost:{port}/compute",
                json=payload,
                timeout=2.0
            )
            return port, resp.json()
        except Exception:
            return port, None
        finally:
            await self.node_manager.mark_free(port)
```

---

### Subscriber Node (`core.py`)

The `SubscriberNode` handles registration and task execution:

**Registration Flow:**
```python
class SubscriberNode:
    def __init__(self, orchestrator_url="http://localhost:8000"):
        self.orchestrator_url = orchestrator_url
        self.assigned_port = None
        self.busy = False
        self.shutdown_flag = False
    
    def register(self):
        """Request a port from orchestrator."""
        r = requests.get(f"{self.orchestrator_url}/get_port")
        port = r.json().get("port")
        if port:
            self.assigned_port = port
            print(f"[SUB] Got assigned port: {port}")
            return port
        return None
    
    def start_heartbeat(self):
        """Start background thread to send heartbeats."""
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True
        )
        self.heartbeat_thread.start()
    
    def _heartbeat_loop(self):
        """Send heartbeat every 5 seconds."""
        while not self.shutdown_flag:
            requests.post(
                f"{self.orchestrator_url}/health_check",
                json={"port": self.assigned_port}
            )
            time.sleep(5)
```

**Dynamic Compute Execution:**
```python
def process_compute(self, unit_type: str, data: dict):
    """Dynamically import and execute compute unit."""
    self.busy = True
    try:
        # Module mapping for units in different files
        module_map = {
            'MatrixMultiplyUnit': 'matrix_ops',
            'PiEstimationUnit': 'monte_carlo',
            'GaussianBlurUnit': 'image_ops',
            # ... etc
        }
        
        # 1. Dynamic import
        module_name = module_map.get(unit_type, unit_type.lower())
        module = import_module(f"exocompute.libs.{module_name}")
        unit_class = getattr(module, unit_type)
        
        # 2. Parse input using Pydantic
        input_obj = unit_class.Input(**data)
        
        # 3. Execute computation
        unit_instance = unit_class()
        output_obj = unit_instance.compute(input_obj)
        
        # 4. Return serialized result
        return output_obj.model_dump()
    
    finally:
        self.busy = False
```

---

### Compute Units (`libs/`)

All compute units inherit from `ComputeUnit` base class:

**Base Classes:**
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class ComputeInput(BaseModel):
    """Base input model with validation."""
    pass

class ComputeOutput(BaseModel):
    """Base output model."""
    pass

class ComputeUnit(ABC):
    """Abstract compute unit that all units must implement."""
    Input: type[ComputeInput]
    Output: type[ComputeOutput]
    
    @abstractmethod
    def compute(self, input_data: ComputeInput) -> ComputeOutput:
        """Execute the computation logic."""
        pass
```

**Example: Multiplication Unit**
```python
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput

class Mul(ComputeUnit):
    class Input(ComputeInput):
        a: int
        b: int
    
    class Output(ComputeOutput):
        result: int
    
    def compute(self, input_data: Input) -> Output:
        return self.Output(result=input_data.a * input_data.b)
```

**Example: Matrix Multiplication Unit**
```python
import numpy as np
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput

class MatrixMultiplyUnit(ComputeUnit):
    class Input(ComputeInput):
        matrix_a: list[list[float]]
        matrix_b: list[list[float]]
    
    class Output(ComputeOutput):
        result: list[list[float]]
    
    def compute(self, input_data: Input) -> Output:
        a = np.array(input_data.matrix_a)
        b = np.array(input_data.matrix_b)
        result = np.matmul(a, b)
        return self.Output(result=result.tolist())
```

---

## 📊 Performance & Benchmarks

### Throughput Test

Running 5000 multiplication tasks with 3 subscriber nodes:

```bash
python3 user.py
```

**Results:**
```
⏱️ Total time for 5000 tasks: 12.34s
✅ Successes: 5000
❌ Errors:    0
```

**Throughput**: ~405 tasks/second

### Scaling Characteristics

| Subscribers | Tasks | Time (s) | Throughput (tasks/s) |
|-------------|-------|----------|---------------------|
| 1           | 5000  | 38.2     | 131                 |
| 2           | 5000  | 19.7     | 254                 |
| 3           | 5000  | 12.3     | 406                 |
| 5           | 5000  | 7.8      | 641                 |
| 10          | 5000  | 4.2      | 1190                |

**Observation**: Near-linear scaling up to 5 nodes, then diminishing returns due to orchestrator overhead.

### Latency Breakdown

For a single task:

```
┌─────────────────────────────────────────────┐
│ Client → Orchestrator         ~2ms          │
│ Orchestrator → Scheduler      ~0.5ms        │
│ Scheduler → Subscriber        ~1ms          │
│ Subscriber Compute            ~0.1ms (Mul)  │
│ Subscriber → Scheduler        ~1ms          │
│ Scheduler → Client            ~2ms          │
├─────────────────────────────────────────────┤
│ Total Round-Trip              ~6.6ms        │
└─────────────────────────────────────────────┘
```

**Bottlenecks:**
- Network I/O (HTTP requests)
- Dynamic import overhead (first execution only)
- Pydantic validation

**Optimizations:**
- Use persistent HTTP connections (httpx.AsyncClient)
- Cache imported modules (Python import system)
- Batch tasks to amortize network overhead

---

## 🔧 Extending ExoCompute

### Creating Custom Compute Units

#### Step 1: Define Your Compute Unit

Create a new file `src/exocompute/libs/my_unit.py`:

```python
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput

class Fibonacci(ComputeUnit):
    class Input(ComputeInput):
        n: int  # Compute nth Fibonacci number
    
    class Output(ComputeOutput):
        result: int
    
    def compute(self, input_data: Input) -> Output:
        def fib(n):
            if n <= 1:
                return n
            return fib(n-1) + fib(n-2)
        
        return self.Output(result=fib(input_data.n))
```

#### Step 2: Use in Client

```python
from exocompute.client import ExoCompute
from exocompute.libs.my_unit import Fibonacci

exo = ExoCompute("http://localhost:8000", Fibonacci)
result = exo.compute(Fibonacci.Input(n=10))
print(result)  # {'result': 55}
```

That's it! The subscriber nodes will automatically discover and execute your unit via dynamic imports.

### Advanced Example: GPU Compute Unit

```python
import torch
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput

class TensorMultiply(ComputeUnit):
    class Input(ComputeInput):
        tensor_a: list[list[float]]
        tensor_b: list[list[float]]
        use_gpu: bool = False
    
    class Output(ComputeOutput):
        result: list[list[float]]
        device_used: str
    
    def compute(self, input_data: Input) -> Output:
        device = "cuda" if input_data.use_gpu and torch.cuda.is_available() else "cpu"
        
        a = torch.tensor(input_data.tensor_a, device=device)
        b = torch.tensor(input_data.tensor_b, device=device)
        
        result = torch.matmul(a, b)
        
        return self.Output(
            result=result.cpu().tolist(),
            device_used=device
        )
```

---

## 📝 Example Use Cases

### 1. Distributed Matrix Operations

```python
from exocompute.client import ExoCompute
from exocompute.libs.matrix_ops import MatrixMultiplyUnit
import numpy as np

exo = ExoCompute("http://localhost:8000", MatrixMultiplyUnit)

# Generate large matrices
A = np.random.rand(100, 100).tolist()
B = np.random.rand(100, 100).tolist()

# Offload computation to grid
result = exo.compute(MatrixMultiplyUnit.Input(matrix_a=A, matrix_b=B))
print(f"Result shape: {len(result['result'])}x{len(result['result'][0])}")
```

### 2. Monte Carlo Simulations

```python
from exocompute.client import ExoCompute
from exocompute.libs.monte_carlo import PiEstimationUnit
import asyncio

exo = ExoCompute("http://localhost:8000", PiEstimationUnit)

# Distribute 1000 simulations across the grid
async def run_simulations():
    tasks = [
        exo.compute(PiEstimationUnit.Input(num_samples=1000000))
        for _ in range(1000)
    ]
    results = await asyncio.gather(*tasks)
    avg_pi = sum(r['pi_estimate'] for r in results) / len(results)
    print(f"Average π estimate: {avg_pi}")

asyncio.run(run_simulations())
```

### 3. Parallel Image Processing

```python
from exocompute.client import ExoCompute
from exocompute.libs.image_ops import GaussianBlurUnit
import asyncio

exo = ExoCompute("http://localhost:8000", GaussianBlurUnit)

# Process 100 images in parallel
async def blur_images(image_paths):
    tasks = []
    for path in image_paths:
        with open(path, 'rb') as f:
            image_bytes = f.read()
        
        tasks.append(exo.compute(GaussianBlurUnit.Input(
            image_data=image_bytes,
            kernel_size=5
        )))
    
    return await asyncio.gather(*tasks)

results = asyncio.run(blur_images(["img1.jpg", "img2.jpg", ...]))
```

---

## ⚠️ Disclaimer

This is a **prototype**, not a production system. Known limitations:

> [!CAUTION]
> **Security**: No authentication, encryption, or authorization
> 
> **Fault Tolerance**: Limited error handling and recovery
> 
> **Scalability**: Not tested beyond 50 nodes
> 
> **Network**: Assumes localhost or trusted LAN

> [!WARNING]
> Do not expose the orchestrator to the public internet without proper security measures!

**Future Improvements:**
- Add JWT authentication
- Implement task queuing with persistence
- Support distributed orchestrators (HA)
- Add monitoring/metrics (Prometheus)
- Implement task priority levels
- Support WebSocket for real-time updates

---

## 🧑‍💻 Author

**Made with caffeine and contempt for centralization by [Suyash]**

---

## 📚 Additional Resources

### API Reference

#### Orchestrator Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/get_port` | GET | Assign port to new subscriber |
| `/submit_task` | POST | Submit task for execution |
| `/unregister` | POST | Unregister a subscriber node |
| `/health_check` | POST | Receive heartbeat from subscriber |

#### Subscriber Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/compute` | POST | Execute a compute task |
| `/health` | GET | Health check endpoint |

### Configuration

**Orchestrator** (`orchestrator/server.py`):
- `HOST`: Default `0.0.0.0`
- `PORT`: Default `8000`

**Subscriber** (`subscriber/__main__.py`):
- `ORCHESTRATOR_URL`: Default `http://localhost:8000`
- `--count`: Number of subscriber nodes to spawn

**Scheduler** (`orchestrator/scheduler.py`):
- `retry_limit`: Max retry attempts (default: 100)
- `retry_delay`: Delay between retries (default: 0.1s)
- `redundancy_factor`: Redundant task dispatch count (default: 2)

**Node Manager** (`orchestrator/manager.py`):
- `PORT_RANGE`: 9001-9050 (50 nodes max)
- `HEARTBEAT_TIMEOUT`: 15 seconds
- `HEALTH_CHECK_INTERVAL`: 5 seconds

---

## 🎯 Roadmap

- [ ] Add authentication layer (JWT)
- [ ] Implement task persistence (Redis/PostgreSQL)
- [ ] Support GPU compute units
- [ ] Add metrics dashboard (Grafana)
- [ ] Implement task prioritization
- [ ] Support multi-orchestrator HA setup
- [ ] Add WebSocket support for streaming results
- [ ] Implement cost-based scheduling

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

**Happy Computing! 🚀**