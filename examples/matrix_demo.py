"""
Matrix Operations Demo - Distributed Linear Algebra with ExoCompute

This demo shows how to distribute matrix operations across compute nodes.
Run this after starting the orchestrator and subscriber nodes.
"""
import sys
import time
import numpy as np
from exocompute.client import ExoCompute
from exocompute.libs.matrix_ops import MatrixMultiplyUnit, MatrixInverseUnit, EigenvalueUnit, MatrixSVDUnit


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_matrix_multiply():
    """Demonstrate distributed matrix multiplication."""
    print_header("Matrix Multiplication Demo")
    
    ORCH_URL = "http://localhost:8000"
    client = ExoCompute(ORCH_URL, MatrixMultiplyUnit)
    
    # Create two random matrices
    size = 100
    matrix_a = np.random.rand(size, size).tolist()
    matrix_b = np.random.rand(size, size).tolist()
    
    print(f"Multiplying two {size}x{size} matrices...")
    
    # Submit to distributed compute
    start_time = time.time()
    input_data = MatrixMultiplyUnit.Input(matrix_a=matrix_a, matrix_b=matrix_b)
    result = client.compute(input_data)
    distributed_time = time.time() - start_time
    
    print(f"✓ Distributed computation completed in {distributed_time:.4f}s")
    print(f"  Result shape: {result['shape']}")
    print(f"  Node computation time: {result['computation_time']:.4f}s")
    
    # Compare with local computation
    print("\nComparing with local computation...")
    start_time = time.time()
    local_result = np.matmul(np.array(matrix_a), np.array(matrix_b))
    local_time = time.time() - start_time
    
    print(f"✓ Local computation completed in {local_time:.4f}s")
    
    # Verify correctness
    distributed_result = np.array(result['result'])
    if np.allclose(distributed_result, local_result):
        print("✓ Results match! Distributed computation is correct.")
    else:
        print("✗ Results don't match!")


def demo_matrix_inverse():
    """Demonstrate distributed matrix inversion."""
    print_header("Matrix Inverse Demo")
    
    ORCH_URL = "http://localhost:8000"
    client = ExoCompute(ORCH_URL, MatrixInverseUnit)
    
    # Create a random invertible matrix
    size = 50
    matrix = np.random.rand(size, size)
    # Make it more likely to be invertible
    matrix = matrix + np.eye(size) * 10
    
    print(f"Computing inverse of {size}x{size} matrix...")
    
    input_data = MatrixInverseUnit.Input(matrix=matrix.tolist())
    result = client.compute(input_data)
    
    if result['is_singular']:
        print("✗ Matrix is singular (not invertible)")
    else:
        print(f"✓ Matrix inverse computed successfully")
        print(f"  Determinant: {result['determinant']:.6f}")
        
        # Verify: A * A^-1 should be identity
        inverse = np.array(result['inverse'])
        identity_check = np.matmul(matrix, inverse)
        is_identity = np.allclose(identity_check, np.eye(size))
        
        if is_identity:
            print("✓ Verification passed: A * A^-1 = I")
        else:
            print("✗ Verification failed")


def demo_eigenvalues():
    """Demonstrate distributed eigenvalue computation."""
    print_header("Eigenvalue Computation Demo")
    
    ORCH_URL = "http://localhost:8000"
    client = ExoCompute(ORCH_URL, EigenvalueUnit)
    
    # Create a symmetric matrix (guaranteed real eigenvalues)
    size = 30
    matrix = np.random.rand(size, size)
    matrix = (matrix + matrix.T) / 2  # Make symmetric
    
    print(f"Computing eigenvalues of {size}x{size} symmetric matrix...")
    
    input_data = EigenvalueUnit.Input(matrix=matrix.tolist())
    result = client.compute(input_data)
    
    eigenvalues = np.array(result['eigenvalues'])
    print(f"✓ Eigenvalues computed successfully")
    print(f"  Largest eigenvalue: {eigenvalues.max():.6f}")
    print(f"  Smallest eigenvalue: {eigenvalues.min():.6f}")
    print(f"  Trace (sum of eigenvalues): {eigenvalues.sum():.6f}")
    print(f"  Matrix trace: {np.trace(matrix):.6f}")


def demo_svd():
    """Demonstrate distributed SVD computation."""
    print_header("Singular Value Decomposition Demo")
    
    ORCH_URL = "http://localhost:8000"
    client = ExoCompute(ORCH_URL, MatrixSVDUnit)
    
    # Create a random matrix
    m, n = 40, 30
    matrix = np.random.rand(m, n)
    
    print(f"Computing SVD of {m}x{n} matrix...")
    
    input_data = MatrixSVDUnit.Input(matrix=matrix.tolist())
    result = client.compute(input_data)
    
    singular_values = np.array(result['singular_values'])
    print(f"✓ SVD computed successfully")
    print(f"  Number of singular values: {len(singular_values)}")
    print(f"  Largest singular value: {singular_values.max():.6f}")
    print(f"  Smallest singular value: {singular_values.min():.6f}")
    print(f"  Condition number: {singular_values.max() / singular_values.min():.2f}")


def main():
    """Run all matrix operation demos."""
    print("\n" + "="*60)
    print("  ExoCompute - Matrix Operations Demo")
    print("  Distributed Linear Algebra with NumPy")
    print("="*60)
    
    try:
        demo_matrix_multiply()
        demo_matrix_inverse()
        demo_eigenvalues()
        demo_svd()
        
        print_header("Demo Complete!")
        print("All matrix operations executed successfully on distributed nodes.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure the orchestrator and subscriber nodes are running:")
        print("  Terminal 1: python -m exocompute.orchestrator")
        print("  Terminal 2: python -m exocompute.subscriber --count 2")
        sys.exit(1)


if __name__ == "__main__":
    main()
