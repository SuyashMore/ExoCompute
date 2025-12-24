"""Matrix operations compute units using NumPy for distributed linear algebra."""
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput
from typing import List
import numpy as np


class MatrixMultiplyUnit(ComputeUnit):
    """Multiply two matrices using NumPy."""
    
    class Input(ComputeInput):
        matrix_a: List[List[float]]
        matrix_b: List[List[float]]
    
    class Output(ComputeOutput):
        result: List[List[float]]
        shape: List[int]
        computation_time: float
    
    def compute(self, input_data: Input) -> Output:
        import time
        start = time.time()
        
        # Convert to numpy arrays
        a = np.array(input_data.matrix_a)
        b = np.array(input_data.matrix_b)
        
        # Perform matrix multiplication
        result = np.matmul(a, b)
        
        computation_time = time.time() - start
        
        return self.Output(
            result=result.tolist(),
            shape=list(result.shape),
            computation_time=computation_time
        )


class MatrixInverseUnit(ComputeUnit):
    """Compute the inverse of a square matrix."""
    
    class Input(ComputeInput):
        matrix: List[List[float]]
    
    class Output(ComputeOutput):
        inverse: List[List[float]]
        determinant: float
        is_singular: bool
    
    def compute(self, input_data: Input) -> Output:
        matrix = np.array(input_data.matrix)
        
        try:
            det = np.linalg.det(matrix)
            if abs(det) < 1e-10:
                # Matrix is singular
                return self.Output(
                    inverse=[],
                    determinant=float(det),
                    is_singular=True
                )
            
            inverse = np.linalg.inv(matrix)
            return self.Output(
                inverse=inverse.tolist(),
                determinant=float(det),
                is_singular=False
            )
        except np.linalg.LinAlgError:
            return self.Output(
                inverse=[],
                determinant=0.0,
                is_singular=True
            )


class EigenvalueUnit(ComputeUnit):
    """Compute eigenvalues and eigenvectors of a matrix."""
    
    class Input(ComputeInput):
        matrix: List[List[float]]
    
    class Output(ComputeOutput):
        eigenvalues: List[float]
        eigenvectors: List[List[float]]
    
    def compute(self, input_data: Input) -> Output:
        matrix = np.array(input_data.matrix)
        
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        
        return self.Output(
            eigenvalues=eigenvalues.real.tolist(),
            eigenvectors=eigenvectors.real.tolist()
        )


class MatrixSVDUnit(ComputeUnit):
    """Compute Singular Value Decomposition of a matrix."""
    
    class Input(ComputeInput):
        matrix: List[List[float]]
    
    class Output(ComputeOutput):
        u: List[List[float]]
        singular_values: List[float]
        vh: List[List[float]]
    
    def compute(self, input_data: Input) -> Output:
        matrix = np.array(input_data.matrix)
        
        u, s, vh = np.linalg.svd(matrix)
        
        return self.Output(
            u=u.tolist(),
            singular_values=s.tolist(),
            vh=vh.tolist()
        )
