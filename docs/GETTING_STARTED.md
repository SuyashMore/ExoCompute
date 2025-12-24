# Getting Started with ExoCompute

Welcome to ExoCompute! This guide will get you up and running in **under 2 minutes**.

---

## 📋 Prerequisites

- **Python 3.8+** installed
- **pip** package manager
- **Git** (for cloning the repository)

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourname/ExoCompute.git
cd ExoCompute
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client
- `pydantic` - Data validation
- `numpy` - Numerical computing (for matrix operations)
- `requests` - HTTP library

---

## 🎮 Three Ways to Use ExoCompute

### 1️⃣ As a Compute Consumer (Submit Tasks)

**Terminal 1: Start an Orchestrator**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m exocompute.orchestrator
```

**Terminal 2: Start Subscriber Nodes**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m exocompute.subscriber --count 3
```

**Terminal 3: Run Your First Task**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python user.py
```

**Expected Output:**
```
⏱️ Total time for 5000 tasks: 12.34s
✅ Successes: 5000
❌ Errors:    0
```

---

### 2️⃣ As a Compute Contributor (Provide Resources)

Simply run:
```bash
python -m exocompute.subscriber --count 5
```

This will:
1. Register 5 nodes with the orchestrator
2. Start heartbeat threads
3. Begin accepting compute tasks
4. Contribute your CPU to the grid

**That's it!** Your machine is now part of the distributed compute network.

---

### 3️⃣ As an Orchestrator Operator (Coordinate Nodes)

```bash
python -m exocompute.orchestrator --host 0.0.0.0 --port 8000
```

Your orchestrator is now:
- Accepting node registrations
- Scheduling tasks
- Monitoring node health
- Serving clients

**Pro Tip:** Deploy orchestrators in multiple regions for global coverage.

---

## 📝 Your First Custom Task

Create a file `my_task.py`:

```python
from exocompute.client import ExoCompute
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput

# 1. Define your compute unit
class StringReverse(ComputeUnit):
    class Input(ComputeInput):
        text: str
    
    class Output(ComputeOutput):
        reversed_text: str
    
    def compute(self, input_data: Input) -> Output:
        return self.Output(reversed_text=input_data.text[::-1])

# 2. Save this as src/exocompute/libs/string_reverse.py
# (For this example, we'll define it inline)

# 3. Use it!
if __name__ == "__main__":
    import sys
    sys.path.append("src")
    
    exo = ExoCompute("http://localhost:8000", StringReverse)
    result = exo.compute(StringReverse.Input(text="Hello ExoCompute!"))
    print(result)  # {'reversed_text': '!etupmoCoxE olleH'}
```

**To make it permanent:**
1. Save the `StringReverse` class to `src/exocompute/libs/string_reverse.py`
2. Import and use from anywhere!

---

## 🔄 Enabling Recursive Orchestration

**The Game Changer:** Any subscriber can also act as an orchestrator.

### Architecture Overview

```
Client → Orchestrator A → Subscriber 1
                        → Subscriber 2 (also Orchestrator B) → Subscriber 3
                                                              → Subscriber 4
```

### How to Enable

**Terminal 1: Primary Orchestrator**
```bash
python -m exocompute.orchestrator --port 8000
```

**Terminal 2: Hybrid Node (Subscriber + Orchestrator)**
```bash
# First, register as subscriber to primary orchestrator
python -m exocompute.subscriber --count 1 --orchestrator http://localhost:8000

# In a separate process, also run as orchestrator on different port
python -m exocompute.orchestrator --port 8001
```

**Terminal 3: Leaf Nodes (Register to secondary orchestrator)**
```bash
python -m exocompute.subscriber --count 5 --orchestrator http://localhost:8001
```

**Terminal 4: Submit Task to Primary**
```python
from exocompute.client import ExoCompute
from exocompute.libs.mul import Mul

# Task goes to primary orchestrator → gets delegated to secondary → executes on leaf nodes
exo = ExoCompute("http://localhost:8000", Mul)
result = exo.compute(Mul.Input(a=100, b=200))
print(result)
```

**Result:** Infinite scalability through hierarchical delegation! 🚀

---

## 🧪 Running Tests

### Unit Tests
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m unittest discover tests/unit
```

### Integration Tests
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m unittest tests/integration/test_system.py
```

### Test Coverage
```bash
pip install pytest pytest-cov
pytest --cov=exocompute tests/
```

---

## 🌍 Deploying to Production

### Docker Deployment (Coming Soon)

```dockerfile
# Dockerfile.orchestrator
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "-m", "exocompute.orchestrator"]
```

```bash
docker build -t exocompute-orchestrator -f Dockerfile.orchestrator .
docker run -p 8000:8000 exocompute-orchestrator
```

### Kubernetes Deployment (Future)

Deploy orchestrators as a StatefulSet and subscribers as a DaemonSet for maximum coverage.

---

## 🔧 Configuration

### Environment Variables

```bash
# Orchestrator
export EXOCOMPUTE_ORCHESTRATOR_HOST=0.0.0.0
export EXOCOMPUTE_ORCHESTRATOR_PORT=8000
export EXOCOMPUTE_PORT_RANGE_START=9001
export EXOCOMPUTE_PORT_RANGE_END=9050

# Subscriber
export EXOCOMPUTE_ORCHESTRATOR_URL=http://localhost:8000
export EXOCOMPUTE_HEARTBEAT_INTERVAL=5
export EXOCOMPUTE_COMPUTE_TIMEOUT=30
```

---

## 🎯 Next Steps

1. ✅ Run your first task
2. ✅ Create a custom compute unit
3. ✅ Set up recursive orchestration
4. 📖 Read the [Architecture Deep Dive](ARCHITECTURE.md)
5. 🌍 Explore [Vision & Future](VISION.md)
6. 🔄 Compare with [existing solutions](COMPARISON.md)

---

## ❓ Troubleshooting

### "No ports available" error
- **Cause:** All 50 ports (9001-9050) are in use
- **Solution:** Increase port range or stop unused subscribers

### "Connection refused" error
- **Cause:** Orchestrator not running
- **Solution:** Start orchestrator first before subscribers

### Tasks timing out
- **Cause:** No available subscribers or subscriber crashed
- **Solution:** Check subscriber logs and restart if needed

### Import errors
- **Cause:** `PYTHONPATH` not set correctly
- **Solution:** Always run with `export PYTHONPATH=$PYTHONPATH:$(pwd)/src` from project root

---

## 💬 Getting Help

- **Documentation:** [docs/](../docs/)
- **Issues:** [GitHub Issues](https://github.com/yourname/ExoCompute/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourname/ExoCompute/discussions)

---

**You're ready to compute!** 🎉

[← Back to Main README](../README.md) | [Architecture Deep Dive →](ARCHITECTURE.md)
