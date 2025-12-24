"""Image processing compute units using NumPy."""
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput
from typing import List
import numpy as np


class GaussianBlurUnit(ComputeUnit):
    """Apply Gaussian blur to an image array."""
    
    class Input(ComputeInput):
        image: List[List[List[int]]]  # RGB image as nested list
        kernel_size: int = 5
        sigma: float = 1.0
    
    class Output(ComputeOutput):
        blurred_image: List[List[List[int]]]
        kernel_size: int
    
    def compute(self, input_data: Input) -> Output:
        from scipy.ndimage import gaussian_filter
        
        image = np.array(input_data.image)
        
        # Apply Gaussian blur to each channel
        blurred = np.zeros_like(image)
        for i in range(image.shape[2]):
            blurred[:, :, i] = gaussian_filter(image[:, :, i], sigma=input_data.sigma)
        
        return self.Output(
            blurred_image=blurred.astype(int).tolist(),
            kernel_size=input_data.kernel_size
        )


class EdgeDetectionUnit(ComputeUnit):
    """Sobel edge detection on grayscale image."""
    
    class Input(ComputeInput):
        image: List[List[int]]  # Grayscale image
    
    class Output(ComputeOutput):
        edges: List[List[int]]
        edge_strength: float
    
    def compute(self, input_data: Input) -> Output:
        from scipy.ndimage import sobel
        
        image = np.array(input_data.image, dtype=float)
        
        # Apply Sobel operator
        sx = sobel(image, axis=0)
        sy = sobel(image, axis=1)
        edges = np.hypot(sx, sy)
        
        # Normalize to 0-255
        edges = (edges / edges.max() * 255).astype(int)
        
        return self.Output(
            edges=edges.tolist(),
            edge_strength=float(np.mean(edges))
        )


class ImageRotateUnit(ComputeUnit):
    """Rotate an image by a specified angle."""
    
    class Input(ComputeInput):
        image: List[List[List[int]]]  # RGB image
        angle: float  # Rotation angle in degrees
    
    class Output(ComputeOutput):
        rotated_image: List[List[List[int]]]
        new_shape: List[int]
    
    def compute(self, input_data: Input) -> Output:
        from scipy.ndimage import rotate
        
        image = np.array(input_data.image)
        
        # Rotate image
        rotated = rotate(image, input_data.angle, reshape=True, mode='constant', cval=0)
        
        return self.Output(
            rotated_image=rotated.astype(int).tolist(),
            new_shape=list(rotated.shape)
        )


class HistogramEqualizationUnit(ComputeUnit):
    """Enhance image contrast using histogram equalization."""
    
    class Input(ComputeInput):
        image: List[List[int]]  # Grayscale image
    
    class Output(ComputeOutput):
        equalized_image: List[List[int]]
        original_histogram: List[int]
        equalized_histogram: List[int]
    
    def compute(self, input_data: Input) -> Output:
        image = np.array(input_data.image)
        
        # Calculate histogram
        hist, bins = np.histogram(image.flatten(), 256, [0, 256])
        
        # Calculate cumulative distribution function
        cdf = hist.cumsum()
        cdf_normalized = cdf * hist.max() / cdf.max()
        
        # Mask zero values
        cdf_m = np.ma.masked_equal(cdf, 0)
        cdf_m = (cdf_m - cdf_m.min()) * 255 / (cdf_m.max() - cdf_m.min())
        cdf = np.ma.filled(cdf_m, 0).astype('uint8')
        
        # Apply equalization
        equalized = cdf[image]
        
        # Calculate new histogram
        eq_hist, _ = np.histogram(equalized.flatten(), 256, [0, 256])
        
        return self.Output(
            equalized_image=equalized.tolist(),
            original_histogram=hist.tolist(),
            equalized_histogram=eq_hist.tolist()
        )
