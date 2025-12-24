# ExoCompute Examples

This directory contains real-world examples demonstrating ExoCompute's distributed computing capabilities using NumPy and SciPy.

## Prerequisites

Install the required dependencies:
```bash
pip install -r ../requirements.txt
```

Make sure to set up the PYTHONPATH:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/../src
```

## Running the Examples

### 1. Start the Orchestrator
In Terminal 1:
```bash
cd ..
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m exocompute.orchestrator
```

### 2. Start Subscriber Nodes
In Terminal 2:
```bash
cd ..
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m exocompute.subscriber --count 2
```

### 3. Run Examples
In Terminal 3:

**Matrix Operations Demo:**
```bash
cd examples
export PYTHONPATH=$PYTHONPATH:$(pwd)/../src
python matrix_demo.py
```

**Monte Carlo Simulations Demo:**
```bash
python monte_carlo_demo.py
```

**Image Processing Demo:**
```bash
python image_demo.py
```

## Examples Overview

### 🔢 Matrix Operations (`matrix_demo.py`)
Demonstrates distributed linear algebra operations:
- **Matrix Multiplication**: Multiply large matrices across nodes
- **Matrix Inversion**: Compute matrix inverses with verification
- **Eigenvalue Computation**: Find eigenvalues and eigenvectors
- **Singular Value Decomposition (SVD)**: Decompose matrices for analysis

**Use Cases**: Machine learning, data science, scientific computing

### 🎲 Monte Carlo Simulations (`monte_carlo_demo.py`)
Demonstrates parallel statistical simulations:
- **Pi Estimation**: Estimate π using random sampling across multiple nodes
- **Option Pricing**: Black-Scholes Monte Carlo for financial derivatives
- **Random Walk**: Simulate stochastic processes

**Use Cases**: Finance, physics simulations, statistical analysis

### 🖼️ Image Processing (`image_demo.py`)
Demonstrates distributed image operations:
- **Gaussian Blur**: Apply smoothing filters
- **Edge Detection**: Sobel operator for edge detection
- **Image Rotation**: Rotate images by arbitrary angles
- **Histogram Equalization**: Enhance image contrast
- **Parallel Processing**: Process multiple images simultaneously

**Use Cases**: Computer vision, image analysis, batch processing

## Performance Notes

- The demos compare distributed vs. local execution times
- Performance gains increase with:
  - Larger problem sizes
  - More compute nodes
  - CPU-intensive operations
- Network overhead is minimal for large computations

## Extending the Examples

To create your own compute units:

1. Create a new file in `../src/exocompute/libs/`
2. Define Input and Output classes using Pydantic
3. Implement the `compute()` method
4. Use the ExoComputeClient to submit tasks

Example:
```python
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput
import numpy as np

class MyCustomUnit(ComputeUnit):
    class Input(ComputeInput):
        data: list[float]
    
    class Output(ComputeOutput):
        result: float
    
    def compute(self, input_data: Input) -> Output:
        arr = np.array(input_data.data)
        return self.Output(result=float(arr.mean()))
```

## Troubleshooting

**Error: "No module named 'exocompute'"**
- Make sure PYTHONPATH is set correctly
- Run from the examples directory

**Error: "No available subscribers"**
- Ensure orchestrator is running on port 8000
- Ensure at least one subscriber node is running
- Check that nodes successfully registered

**Import errors for numpy/scipy:**
- Run `pip install -r ../requirements.txt`
