# API Reference

Complete API documentation for ExoCompute client, orchestrator, and subscriber interfaces.

---

## 🔌 Client SDK

### ExoCompute Class

```python
from exocompute.client import ExoCompute
```

#### Constructor

```python
ExoCompute(orchestrator_url: str, compute_unit: Type[ComputeUnit])
```

**Parameters:**
- `orchestrator_url` (str): Base URL of orchestrator (e.g., `http://localhost:8000`)
- `compute_unit` (Type[ComputeUnit]): Compute unit class reference

**Example:**
```python
from exocompute.libs.mul import Mul
exo = ExoCompute("http://localhost:8000", Mul)
```

---

#### Methods

##### `compute(input_data: ComputeInput) -> dict`

Submit a task for execution.

**Parameters:**
- `input_data` (ComputeInput): Pydantic model instance

**Returns:**
- `dict`: Result dictionary from compute unit

**Raises:**
- `requests.exceptions.RequestException`: HTTP errors
- `Exception`: Missing result key or other errors

**Example:**
```python
result = exo.compute(Mul.Input(a=10, b=20))
# Returns: {'result': 200}
```

---

## 🎛️ Orchestrator API

Base URL: `http://localhost:8000`

### Endpoints

#### GET `/get_port`

Assign a unique port to a new subscriber node.

**Response:**
```json
{
  "port": 9001
}
```

**Error Response (503):**
```json
{
  "error": "No ports available"
}
```

**Example:**
```bash
curl http://localhost:8000/get_port
```

---

#### POST `/submit_task`

Submit a computational task for execution.

**Request Body:**
```json
{
  "unit": "MatrixMultiplyUnit",
  "input": {
    "matrix_a": [[1, 2], [3, 4]],
    "matrix_b": [[5, 6], [7, 8]]
  }
}
```

**Response:**
```json
{
  "result": {
    "result": [[19, 22], [43, 50]],
    "shape": [2, 2],
    "computation_time": 0.001
  }
}
```

**Error Response (503):**
```json
{
  "error": "No available subscribers or all failed"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/submit_task \
  -H "Content-Type: application/json" \
  -d '{"unit": "Mul", "input": {"a": 5, "b": 10}}'
```

---

#### POST `/unregister`

Remove a subscriber node from the registry.

**Request Body:**
```json
{
  "port": 9001
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

#### POST `/health_check`

Receive heartbeat from subscriber node.

**Request Body:**
```json
{
  "port": 9001
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

## 🖥️ Subscriber API

Base URL: `http://localhost:9001` (or assigned port)

### Endpoints

#### POST `/compute`

Execute a computational task.

**Request Body:**
```json
{
  "unit": "Mul",
  "input": {
    "a": 10,
    "b": 20
  }
}
```

**Response:**
```json
{
  "result": 200
}
```

**Error Response (500):**
```json
{
  "error": "Invalid compute unit 'InvalidUnit': ..."
}
```

---

#### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## 🧩 Compute Units

### Base Classes

```python
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput
```

#### ComputeInput

Base class for all compute unit inputs.

```python
class ComputeInput(BaseModel):
    pass
```

All inputs must inherit from this and define fields using Pydantic.

---

#### ComputeOutput

Base class for all compute unit outputs.

```python
class ComputeOutput(BaseModel):
    pass
```

---

#### ComputeUnit

Abstract base class for all compute units.

```python
class ComputeUnit(ABC):
    Input: type[ComputeInput]
    Output: type[ComputeOutput]
    
    @abstractmethod
    def compute(self, input_data: ComputeInput) -> ComputeOutput:
        pass
```

**Required:**
- Define nested `Input` class
- Define nested `Output` class
- Implement `compute()` method

---

### Built-in Compute Units

#### Math Operations

##### Mul (Multiplication)
```python
from exocompute.libs.mul import Mul

Mul.Input(a: int, b: int)
Mul.Output(result: int)
```

##### Add (Addition)
```python
from exocompute.libs.adder import Add

Add.Input(a: int, b: int)
Add.Output(result: int)
```

##### Sub (Subtraction)
```python
from exocompute.libs.sub import Sub

Sub.Input(a: int, b: int)
Sub.Output(result: int)
```

##### Sqr (Square)
```python
from exocompute.libs.sqr import Sqr

Sqr.Input(value: int)
Sqr.Output(result: int)
```

---

#### Matrix Operations

##### MatrixMultiplyUnit
```python
from exocompute.libs.matrix_ops import MatrixMultiplyUnit

MatrixMultiplyUnit.Input(
    matrix_a: List[List[float]],
    matrix_b: List[List[float]]
)

MatrixMultiplyUnit.Output(
    result: List[List[float]],
    shape: List[int],
    computation_time: float
)
```

##### MatrixInverseUnit
```python
MatrixInverseUnit.Input(
    matrix: List[List[float]]
)

MatrixInverseUnit.Output(
    inverse: List[List[float]],
    determinant: float,
    is_singular: bool
)
```

##### EigenvalueUnit
```python
EigenvalueUnit.Input(
    matrix: List[List[float]]
)

EigenvalueUnit.Output(
    eigenvalues: List[float],
    eigenvectors: List[List[float]]
)
```

##### MatrixSVDUnit
```python
MatrixSVDUnit.Input(
    matrix: List[List[float]]
)

MatrixSVDUnit.Output(
    u: List[List[float]],
    singular_values: List[float],
    vh: List[List[float]]
)
```

---

## 🛠️ Creating Custom Compute Units

### Template

```python
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput
from typing import List

class MyCustomUnit(ComputeUnit):
    """Description of what this unit does."""
    
    class Input(ComputeInput):
        # Define input fields
        data: str
        count: int
    
    class Output(ComputeOutput):
        # Define output fields
        result: str
        processed_count: int
    
    def compute(self, input_data: Input) -> Output:
        # Your computation logic
        result = input_data.data * input_data.count
        
        return self.Output(
            result=result,
            processed_count=input_data.count
        )
```

### Best Practices

1. **Use type hints** for all fields
2. **Add docstrings** to explain behavior
3. **Handle errors gracefully** within compute()
4. **Return meaningful outputs** (not just result)
5. **Keep compute() pure** (no side effects)
6. **Validate inputs** (Pydantic does this automatically)

---

## 🔧 Configuration

### Environment Variables

#### Orchestrator
```bash
EXOCOMPUTE_ORCHESTRATOR_HOST=0.0.0.0
EXOCOMPUTE_ORCHESTRATOR_PORT=8000
EXOCOMPUTE_PORT_RANGE_START=9001
EXOCOMPUTE_PORT_RANGE_END=9050
EXOCOMPUTE_HEALTH_CHECK_INTERVAL=5
EXOCOMPUTE_HEARTBEAT_TIMEOUT=15
```

#### Subscriber
```bash
EXOCOMPUTE_ORCHESTRATOR_URL=http://localhost:8000
EXOCOMPUTE_HEARTBEAT_INTERVAL=5
EXOCOMPUTE_COMPUTE_TIMEOUT=30
```

#### Scheduler
```bash
EXOCOMPUTE_RETRY_LIMIT=100
EXOCOMPUTE_RETRY_DELAY=0.1
EXOCOMPUTE_REDUNDANCY_FACTOR=2
```

---

## 📝 Error Codes

| Code | Description |
|------|-------------|
| **200** | Success |
| **503** | Service Unavailable (no nodes or all failed) |
| **500** | Internal Server Error (compute unit error) |
| **400** | Bad Request (invalid input) |
| **404** | Not Found (invalid endpoint) |

---

## 🧪 Testing Helpers

### Mock Compute Unit

```python
class MockUnit(ComputeUnit):
    class Input(ComputeInput):
        value: int
    
    class Output(ComputeOutput):
        result: int
    
    def compute(self, input_data: Input) -> Output:
        return self.Output(result=input_data.value * 2)
```

### Integration Test Pattern

```python
import unittest
from exocompute.client import ExoCompute

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Start orchestrator and subscribers
        pass
    
    def tearDown(self):
        # Stop services
        pass
    
    def test_task_execution(self):
        exo = ExoCompute("http://localhost:8000", MockUnit)
        result = exo.compute(MockUnit.Input(value=10))
        self.assertEqual(result["result"], 20)
```

---

**For more examples, see the [examples/](../examples/) directory.**

[← Back to README](../README.md) | [Getting Started →](GETTING_STARTED.md)
