# ExoCompute

> A lightweight framework for distributing Python compute tasks across worker processes, with a pluggable "compute unit" model and redundant task dispatch.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
🚧 **Status: Beta / prototype** — see [Current State vs. Vision](#current-state-vs-vision) below.

## What It Does

ExoCompute lets you write a unit of computation once (a `ComputeUnit`) and run it on any subscriber node registered with an orchestrator, without writing networking or scheduling code yourself:

```python
class MyCustomUnit(ComputeUnit):
    class Input(ComputeInput):
        data: str

    class Output(ComputeOutput):
        result: str

    def compute(self, input_data: Input) -> Output:
        return self.Output(result=input_data.data.upper())
```

A client submits typed input to an orchestrator, the orchestrator hands the task to one or more available subscriber nodes, and the result comes back as a typed output.

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/SuyashMore/ExoCompute.git && cd ExoCompute
pip install -r requirements.txt

# 2. Start an orchestrator (coordinates tasks)
python -m exocompute.orchestrator

# 3. Start subscriber node(s) that will execute compute units
python -m exocompute.subscriber --count 3

# 4. Submit a task from a client
python user.py
```

### Consumer example

```python
from exocompute.client import ExoCompute
from exocompute.libs.mul import Mul

exo = ExoCompute("http://localhost:8000", Mul)
result = exo.compute(Mul.Input(a=10, b=20))
print(result)  # {'result': 200}
```

## How It Works Today

| Component | Location | What it actually does |
|---|---|---|
| **Orchestrator** | `src/exocompute/orchestrator/` | A FastAPI service (`server.py`) that assigns each subscriber a port (`manager.py`), health-checks registered subscribers every few seconds, and dispatches submitted tasks (`scheduler.py`) |
| **Scheduler** | `orchestrator/scheduler.py` | Sends each task to `redundancy_factor` (default 2) subscribers concurrently and returns the first successful result, retrying against other nodes on failure |
| **Subscriber** | `src/exocompute/subscriber/` | Registers with the orchestrator to get a port, runs a small HTTP server (`server.py`) that executes the requested `ComputeUnit` (`core.py`), and sends periodic heartbeats |
| **Client** | `src/exocompute/client/` | Thin wrapper that serializes a Pydantic `Input`, POSTs it to the orchestrator's `/submit_task`, and returns the typed result |
| **Compute units** | `src/exocompute/libs/` | Built-in units: arithmetic (`Adder`, `Mul`, `Sqr`, `Sub`), linear algebra (`MatrixMultiplyUnit`, `MatrixInverseUnit`, `EigenvalueUnit`, `MatrixSVDUnit`), Monte Carlo methods (`PiEstimationUnit`, `OptionPricingUnit`, `RandomWalkUnit`), and image processing (`GaussianBlurUnit`, `EdgeDetectionUnit`, `ImageRotateUnit`, `HistogramEqualizationUnit`) |

In the current implementation, an orchestrator runs on one machine and manages subscriber processes via a fixed local port range (`9000`–`9250` by default) — `--count N` simply spawns `N` subscriber subprocesses. There is one orchestrator per run; multi-orchestrator peer discovery and subscriber-as-orchestrator nesting are not implemented yet (see below).

## Current State vs. Vision

The project's long-term goal is a decentralized, internet-scale "world computer" — recursive orchestration, torrent-style peer discovery, and community-contributed compute across arbitrary networks. That vision is written up in [`docs/VISION.md`](docs/VISION.md) and the comparison in [`docs/COMPARISON.md`](docs/COMPARISON.md).

What exists today is the core building block for that vision: a working orchestrator/subscriber/client protocol with redundant task dispatch and a pluggable compute-unit interface, exercised by unit tests (`tests/unit/`) and an integration test (`tests/integration/test_system.py`). Multi-orchestrator federation, peer discovery, and recursive orchestration described in the vision docs are roadmap items, not yet implemented.

## Examples

The `examples/` folder has runnable demos against a live orchestrator + subscribers:

```bash
python examples/matrix_demo.py   # distributed matrix multiply/inverse/eigenvalues/SVD
python examples/exo_helper.py
```

## Testing

```bash
python -m unittest discover tests/unit
python -m unittest discover tests/integration
```

## Requirements

- Python 3.8+
- FastAPI, uvicorn, httpx, pydantic, requests (orchestrator/subscriber/client)
- numpy, scipy (matrix and Monte Carlo compute units)

See `requirements.txt` for pinned versions.

## Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Vision & Roadmap](docs/VISION.md)
- [Comparison with Ray/Dask/Spark/BOINC](docs/COMPARISON.md)
- [Contributing](docs/CONTRIBUTING.md)

## License

MIT — see [LICENSE](LICENSE) if present, or the badge above.
