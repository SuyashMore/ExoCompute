# Distributed Compute Prototype

Welcome to the **Distributed Compute Grid** prototype — a proof-of-concept for a decentralized computation network, where lightweight nodes subscribe to a central orchestrator and perform tasks on-demand.

> Think: a minimal version of Kubernetes meets BOINC, powered by Python + FastAPI.

---

## ⚙️ How It Works

- **`orchestrator.py`**: Acts as the central brain. Manages node health, assigns compute, and tracks busy/free state.
- **`sub.py`**: Launches one or more compute nodes that register with the orchestrator and perform calculations.
- **`user.py`**: Sends compute requests to the orchestrator, which distributes work to healthy subscribers.
- **`lib.py`**: Contains the core compute logic (e.g. `add(a, b)`), with artificial CPU load to simulate heavy tasks.

---

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/yourname/distributed-compute-prototype.git
cd distributed-compute-prototype

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Orchestrator
```bash
python orchestrator.py
```

### 3. Launch Subscribers
```bash
# Launch 5 subscriber nodes in parallel
python sub.py --count 5
```

### 4. Run a User Program
```bash
python user.py
```

---

## 🧠 Features

- 🔁 **Retry logic**: User requests auto-retry failed elements with random backoff
- 🧍 **Idle/busy tracking**: Orchestrator ensures load-balanced scheduling
- 🔥 **CPU load simulation**: No fake sleeps — real math-heavy loops burn CPU per task
- 💀 **Health checks**: Dead nodes are booted and ports reclaimed
- 🧪 **Mass testing**: Spin up 100+ nodes easily for scale experiments

---

## 🧪 Benchmarking

### Ideal Target Time (with 4 healthy subs):
| Elements | Ideal Time  |
|----------|-------------|
| 16       | ~4.0–5.0s   |
| 8        | ~2.0–2.5s   |
| 1        | ~1.0s       |

---

## 📁 Project Structure

```
.
├── orchestrator.py     # Central task manager
├── sub.py              # Spawns compute nodes (subscribers)
├── user.py             # Sends compute requests
├── lib.py              # Compute logic with real CPU burn
├── requirements.txt    # Python dependencies
├── README.md           # You're reading it
```

---

## 🤔 What’s Next?

- [ ] Async orchestration for concurrency
- [ ] Multi-threaded compute engine
- [ ] Persistent node registry
- [ ] Credit system & resource market
- [ ] Fault-tolerant request replication
- [ ] UI dashboard for node status

---

## 🧠 Idea Behind This

Build an **elastic grid compute layer** that lets users:
- Borrow compute in exchange for credits
- Lend idle cores and earn passive credits
- Run workloads across a P2P-style network

---

## ⚠️ Disclaimer

This is a **prototype**, not a production system. You *will* break things. That’s the point.

---

## 🧑‍💻 Author

Made with caffeine and contempt for centralization by [Suyash].