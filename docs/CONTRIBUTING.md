# Contributing to ExoCompute

Thank you for your interest in contributing to **ExoCompute**! This document provides guidelines for contributing to the world computer.

---

## 🌟 Ways to Contribute

### 1. **Code Contributions**
- Implement features from the [future scope](VISION.md#-future-scope)
- Fix bugs
- Improve performance
- Add new compute units

### 2. **Documentation**
- Improve existing docs
- Add tutorials and examples
- Translate documentation
- Create video tutorials

### 3. **Testing**
- Write unit tests
- Create integration tests
- Perform load testing
- Report bugs

### 4. **Community**
- Answer questions in discussions
- Help onboard new users
- Share use cases
- Spread awareness

---

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/ExoCompute.git
cd ExoCompute
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies + dev tools
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

---

## 📝 Development Workflow

### 1. Make Changes

- Follow existing code style
- Add docstrings to new functions/classes
- Write tests for new features

### 2. Run Tests

```bash
# Run all tests
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m pytest tests/

# Run with coverage
pytest --cov=exocompute tests/
```

### 3. Format Code

```bash
# Auto-format with black
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add amazing new feature"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## 🎯 Contribution Areas

### High Priority

#### 1. Authentication & Security
**Goal:** Add JWT-based authentication

**Tasks:**
- [ ] JWT token generation for clients
- [ ] API key authentication for subscribers
- [ ] Middleware for token validation
- [ ] Tests for auth flows

**Example:**
```python
@app.post("/submit_task")
async def submit_task(
    req: Request,
    token: str = Depends(verify_jwt_token)
):
    # Existing logic
```

---

#### 2. Metrics & Monitoring
**Goal:** Prometheus integration

**Tasks:**
- [ ] Add prometheus_client dependency
- [ ] Instrument orchestrator (tasks/sec, latency)
- [ ] Instrument subscribers (compute time, errors)
- [ ] Create Grafana dashboard JSON

**Example:**
```python
from prometheus_client import Counter, Histogram

tasks_total = Counter('exocompute_tasks_total', 'Total tasks')
task_latency = Histogram('exocompute_task_latency', 'Task latency')
```

---

#### 3. Inter-Orchestrator Communication
**Goal:** Enable orchestrator mesh networking

**Tasks:**
- [ ] Orchestrator discovery protocol
- [ ] Task delegation between orchestrators
- [ ] Load balancing across orchestrators
- [ ] Tests for multi-orchestrator scenarios

---

### Medium Priority

#### 4. Web Dashboard
**Goal:** React dashboard for monitoring

**Features:**
- Real-time node count
- Task throughput graph
- Recent task history
- Node health status

---

#### 5. GPU Support
**Goal:** CUDA/ROCm compute units

**Tasks:**
- [ ] Detect GPU availability
- [ ] GPU-enabled MatrixMultiply unit
- [ ] ML inference unit (PyTorch)
- [ ] GPU resource tracking

---

#### 6. Task Queuing
**Goal:** Persistent task queue (Redis)

**Tasks:**
- [ ] Redis integration
- [ ] Enqueue tasks when no nodes available
- [ ] Dequeue when nodes become available
- [ ] Priority queue support

---

### Low Priority

#### 7. CLI Tool
**Goal:** `exocompute` command-line tool

```bash
exocompute orchestrator start --port 8000
exocompute subscriber start --count 5
exocompute task submit --unit Mul --input '{"a": 5, "b": 10}'
exocompute cluster status
```

---

## 🧪 Testing Guidelines

### Unit Tests

**Location:** `tests/unit/`

**Example:**
```python
import unittest
from exocompute.orchestrator.scheduler import TaskScheduler

class TestScheduler(unittest.TestCase):
    def test_redundancy_factor(self):
        scheduler = TaskScheduler(node_manager=MockNodeManager())
        self.assertEqual(scheduler.redundancy_factor, 2)
```

### Integration Tests

**Location:** `tests/integration/`

**Example:**
```python
import unittest
from exocompute.client import ExoCompute

class TestSystemIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start orchestrator and subscribers
        pass
    
    def test_end_to_end_task(self):
        exo = ExoCompute("http://localhost:8000", Mul)
        result = exo.compute(Mul.Input(a=10, b=20))
        self.assertEqual(result["result"], 200)
```

---

## 📚 Code Style Guide

### Python Style

**Follow PEP 8:**
- 4 spaces for indentation
- Max line length: 100 characters
- Use type hints

**Example:**
```python
def submit_task(
    payload: dict,
    timeout: float = 30.0
) -> dict:
    """
    Submit a task for execution.
    
    Args:
        payload: Task specification
        timeout: Request timeout in seconds
    
    Returns:
        Result dictionary
    
    Raises:
        TimeoutError: If request exceeds timeout
    """
    # Implementation
```

### Docstrings

Use **Google style** docstrings:
```python
class ExoCompute:
    """Client for submitting tasks to ExoCompute grid.
    
    Attributes:
        orchestrator_url: Base URL of orchestrator
        unit_class: Compute unit class reference
    """
```

---

## 🐛 Bug Reports

### Template

```markdown
**Bug Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Start orchestrator
2. Submit task with input {...}
3. Observe error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.5
- ExoCompute version: 0.1.0

**Logs:**
```
[paste relevant logs]
```
```

---

## ✨ Feature Requests

### Template

```markdown
**Feature Description:**
Clear description of the feature

**Use Case:**
Why this feature is needed

**Proposed Solution:**
How it could be implemented

**Alternatives Considered:**
Other approaches you've thought about
```

---

## 📖 Documentation Guidelines

### Markdown Style

- Use **headers** for organization
- Include **code examples** for APIs
- Add **diagrams** for complex concepts
- Use **tables** for comparisons

### Example Structure

```markdown
# Feature Name

Brief description

## Usage

\```python
# Code example
\```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| foo | str | Description |

## Examples

### Example 1
...
```

---

## 🎨 Creating Compute Units

### Checklist

- [ ] Inherit from `ComputeUnit`
- [ ] Define `Input` and `Output` models
- [ ] Implement `compute()` method
- [ ] Add docstrings
- [ ] Write unit tests
- [ ] Add to documentation

### Template

```python
"""Module for [category] compute units."""
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput
from typing import List

class MyNewUnit(ComputeUnit):
    """Brief description of what this unit does.
    
    This unit performs [operation] on [input] and returns [output].
    Useful for [use case].
    """
    
    class Input(ComputeInput):
        """Input specification."""
        field1: str
        field2: int
    
    class Output(ComputeOutput):
        """Output specification."""
        result: str
    
    def compute(self, input_data: Input) -> Output:
        """Execute the computation.
        
        Args:
            input_data: Validated input
        
        Returns:
            Computation result
        """
        # Your logic here
        result = f"Processed: {input_data.field1} x {input_data.field2}"
        return self.Output(result=result)
```

---

## 🏆 Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Annual contributor spotlight

**Top contributors may receive:**
- Maintainer status
- EXOC tokens (post-tokenomics launch)
- Conference speaking opportunities

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment.

### Standards

**Expected Behavior:**
- Be respectful and considerate
- Accept constructive criticism
- Focus on what's best for the community

**Unacceptable Behavior:**
- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information

### Enforcement

Report violations to: [conduct@exocompute.org](mailto:conduct@exocompute.org)

---

## 📞 Communication Channels

- **GitHub Issues:** Bug reports and features
- **GitHub Discussions:** Questions and ideas
- **Discord:** Real-time chat (coming soon)
- **Twitter:** [@ExoCompute](https://twitter.com/ExoCompute)

---

## 🎓 Learning Resources

### For New Contributors

1. Read [Getting Started](GETTING_STARTED.md)
2. Read [Architecture Deep Dive](ARCHITECTURE.md)
3. Browse [existing issues](https://github.com/yourname/ExoCompute/issues)
4. Start with "good first issue" label

### Advanced Topics

- [Recursive Orchestration](VISION.md#-recursive-orchestration-the-key-innovation)
- [Fault Tolerance](ARCHITECTURE.md#️-fault-tolerance-mechanisms)
- [Performance Optimization](ARCHITECTURE.md#-performance-characteristics)

---

## 🚢 Release Process

### Versioning

We follow **Semantic Versioning** (semver):
- `MAJOR.MINOR.PATCH`
- `0.1.0` → `0.2.0` (new features)
- `0.2.0` → `0.2.1` (bug fixes)
- `0.x.y` → `1.0.0` (production-ready)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Git tag created
- [ ] PyPI package published

---

## ❓ FAQ for Contributors

**Q: Do I need to sign a CLA?**
A: No, ExoCompute is MIT licensed. Your contributions are yours.

**Q: How long do PR reviews take?**
A: Typically 1-3 days. Be patient!

**Q: Can I work on multiple issues at once?**
A: Yes, but please don't start too many. Finish what you start.

**Q: What if my PR is rejected?**
A: Don't take it personally. We'll explain why and suggest improvements.

---

## 🎯 Potential Focus Areas

> [!NOTE]
> As a POC, these represent potential areas of interest for future development. Implementation is not guaranteed and depends on community interest and project direction.

**Near-term possibilities:**
- Authentication & security
- Metrics & monitoring
- Docker deployment

**Medium-term possibilities:**
- Inter-orchestrator communication
- Web dashboard
- GPU support

**See [VISION.md](VISION.md) for full future scope.**

---

## 🙏 Thank You!

Every contribution, no matter how small, helps build the world computer.

**Together, we're democratizing access to computational power.**

---

[← Back to README](../README.md) | [Vision →](VISION.md)
