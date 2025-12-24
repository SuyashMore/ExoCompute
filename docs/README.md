# ExoCompute Documentation

Complete documentation for the ExoCompute distributed compute framework.

---

## 📚 Documentation Index

### Getting Started

- **[README](../README.md)** - Project overview, vision, and quick links
- **[Getting Started Guide](GETTING_STARTED.md)** - Installation, setup, and first task (⭐ Start here!)
  - 2-minute onboarding
  - Three usage modes (consumer, contributor, orchestrator)
  - Recursive orchestration setup
  - Troubleshooting guide

---

### Core Concepts

- **[Architecture Deep Dive](ARCHITECTURE.md)** - Technical implementation details
  - System overview with diagrams
  - Component architecture
  - Task execution flow  
  - Recursive orchestration mechanics
  - Performance analysis
  - Fault tolerance mechanisms

- **[API Reference](API_REFERENCE.md)** - Complete API documentation
  - Client SDK reference
  - Orchestrator endpoints
  - Subscriber endpoints
  - Built-in compute units
  - Custom unit creation guide

---

### Vision & Future

- **[Vision & Future](VISION.md)** - The world computer concept
  - What is a world computer?
  - Recursive orchestration benefits
  - Real-world applications (7 detailed use cases)
  - Future scope and potential features
  - Economic model
  - Global impact

- **[How We're Different](COMPARISON.md)** - Comparison with existing solutions
  - vs. Ray, Dask, Spark, BOINC, Kubernetes
  - Feature comparison matrix
  - Performance benchmarks
  - When to use ExoCompute

---

### Contributing

- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
  - Development workflow
  - Code style guide
  - Testing guidelines
  - High-priority contribution areas
  - Bug report template
  - Feature request template

---

## 🎯 Quick Navigation

### For New Users

1. **[Quick Start](GETTING_STARTED.md#-quick-start)** - Get running in 2 minutes
2. **[Your First Custom Task](GETTING_STARTED.md#-your-first-custom-task)** - Create a compute unit
3. **[API Reference](API_REFERENCE.md)** - Look up specific APIs

### For Contributors

1. **[Architecture](ARCHITECTURE.md)** - Understand the system
2. **[Contributing Guide](CONTRIBUTING.md)** - Development workflow
3. **[Vision](VISION.md#-future-scope)** - See potential future directions

### For Researchers/Architects

1. **[Vision: World Computer](VISION.md#-the-world-computer-vision)** - Big picture
2. **[Recursive Orchestration](VISION.md#-recursive-orchestration-the-key-innovation)** - Key innovation
3. **[Practical Applications](VISION.md#-practical-applications)** - Use cases
4. **[Comparison](COMPARISON.md)** - How it differs from alternatives

---

## 📖 Document Summaries

| Document | Purpose | Length | Audience |
|----------|---------|--------|----------|
| **README** | Overview & quick start | Short | Everyone |
| **GETTING_STARTED** | Setup & onboarding | Medium | New users |
| **ARCHITECTURE** | Technical deep dive | Long | Developers |
| **API_REFERENCE** | API documentation | Long | Developers |
| **VISION** | Future & applications | Long | Everyone |
| **COMPARISON** | Differentiation | Medium | Decision-makers |
| **CONTRIBUTING** | Development guide | Medium | Contributors |

---

## 🌟 Key Highlights

### What Makes ExoCompute Unique?

1. **[Recursive Orchestration](VISION.md#-recursive-orchestration-the-key-innovation)**
   - Any subscriber can become an orchestrator
   - Infinite scalability (fractal architecture)
   - No single point of failure

2. **[2-Minute Onboarding](GETTING_STARTED.md#-quick-start)**
   - `pip install && python -m exocompute.subscriber`
   - No infrastructure, no configuration

3. **[Pluggable Compute Units](API_REFERENCE.md#-creating-custom-compute-units)**
   - Simple Python classes
   - Dynamic imports at runtime
   - No deployment needed

4. **[World Computer Vision](VISION.md#-the-world-computer-vision)**
   - Community-driven compute
   - Global resource sharing
   - Economic incentives (future)

---

## 🔍 Finding Information

### By Topic

| Topic | Document | Section |
|-------|----------|---------|
| Installation | [GETTING_STARTED](GETTING_STARTED.md) | Installation |
| Running first task | [GETTING_STARTED](GETTING_STARTED.md) | Quick Start |
| Creating compute units | [API_REFERENCE](API_REFERENCE.md) | Creating Custom Units |
| Recursive orchestration | [VISION](VISION.md) | Recursive Orchestration |
| System architecture | [ARCHITECTURE](ARCHITECTURE.md) | System Overview |
| Performance benchmarks | [COMPARISON](COMPARISON.md) | Performance Comparison |
| Contributing code | [CONTRIBUTING](CONTRIBUTING.md) | Development Workflow |
| Use cases | [VISION](VISION.md) | Practical Applications |

---

## 📝 Examples

### Code Examples

**Submit a simple task:**
```python
from exocompute.client import ExoCompute
from exocompute.libs.mul import Mul

exo = ExoCompute("http://localhost:8000", Mul)
result = exo.compute(Mul.Input(a=10, b=20))
print(result)  # {'result': 200}
```

**Create a custom compute unit:**
```python
class Fibonacci(ComputeUnit):
    class Input(ComputeInput):
        n: int
    
    class Output(ComputeOutput):
        result: int
    
    def compute(self, input_data: Input) -> Output:
        # Your logic here
        return self.Output(result=fib(input_data.n))
```

**Enable recursive orchestration:**
```bash
# Node becomes subscriber AND orchestrator
python -m exocompute.subscriber --orchestrator http://parent:8000 &
python -m exocompute.orchestrator --port 8001 &
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for more examples.

---

## 🎓 Learning Path

### Beginner (0-1 week)

1. Read [README](../README.md)
2. Follow [GETTING_STARTED](GETTING_STARTED.md)
3. Create your first custom unit
4. Browse [API_REFERENCE](API_REFERENCE.md)

### Intermediate (1-4 weeks)

1. Read [ARCHITECTURE](ARCHITECTURE.md)
2. Set up recursive orchestration
3. Explore [VISION](VISION.md) use cases
4. Contribute a simple compute unit

### Advanced (1+ months)

1. Deep dive into [ARCHITECTURE](ARCHITECTURE.md)
2. Read [COMPARISON](COMPARISON.md)
3. Contribute to core features (see [CONTRIBUTING](CONTRIBUTING.md))
4. Build a production deployment

---

## 🚀 Project Status

**Current Version:** 0.1.0 (Beta)

**What Works:**
- ✅ Core orchestrator/subscriber architecture
- ✅ Task submission and execution
- ✅ Redundant execution for fault tolerance
- ✅ Dynamic compute unit imports
- ✅ Health monitoring
- ✅ Recursive orchestration support

**What's Coming:**
- 🚧 Authentication & security
- 🚧 Metrics & monitoring
- 🚧 Web dashboard
- 🚧 GPU support
- 🚧 Inter-orchestrator mesh

See [VISION.md](VISION.md#-future-scope) for the complete future scope.

---

## 💬 Getting Help

- **Documentation Issues:** Open an issue with "docs:" prefix
- **Questions:** Use [GitHub Discussions](https://github.com/yourname/ExoCompute/discussions)
- **Bugs:** See [bug report template](CONTRIBUTING.md#-bug-reports)
- **Feature Requests:** See [feature request template](CONTRIBUTING.md#-feature-requests)

---

## 📄 License

ExoCompute is MIT licensed. See [LICENSE](../LICENSE) for details.

---

**Let's build the world computer together! 🌍**

[← Back to Main README](../README.md)
