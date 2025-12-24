"""Monte Carlo simulation compute units for statistical analysis."""
from exocompute.libs.base import ComputeUnit, ComputeInput, ComputeOutput
import numpy as np


class PiEstimationUnit(ComputeUnit):
    """Estimate π using Monte Carlo method with random sampling."""
    
    class Input(ComputeInput):
        num_samples: int
        seed: int = None
    
    class Output(ComputeOutput):
        pi_estimate: float
        samples_inside: int
        total_samples: int
        error: float
    
    def compute(self, input_data: Input) -> Output:
        if input_data.seed is not None:
            np.random.seed(input_data.seed)
        
        # Generate random points in unit square
        x = np.random.uniform(-1, 1, input_data.num_samples)
        y = np.random.uniform(-1, 1, input_data.num_samples)
        
        # Check if points are inside unit circle
        distances = x**2 + y**2
        inside = np.sum(distances <= 1.0)
        
        # Estimate π
        pi_estimate = 4.0 * inside / input_data.num_samples
        error = abs(pi_estimate - np.pi)
        
        return self.Output(
            pi_estimate=float(pi_estimate),
            samples_inside=int(inside),
            total_samples=input_data.num_samples,
            error=float(error)
        )


class OptionPricingUnit(ComputeUnit):
    """Black-Scholes Monte Carlo option pricing."""
    
    class Input(ComputeInput):
        spot_price: float      # Current stock price
        strike_price: float    # Strike price
        time_to_maturity: float  # Time to expiration (years)
        risk_free_rate: float  # Risk-free interest rate
        volatility: float      # Volatility (sigma)
        num_simulations: int   # Number of Monte Carlo paths
        option_type: str = "call"  # "call" or "put"
        seed: int = None
    
    class Output(ComputeOutput):
        option_price: float
        std_error: float
        confidence_interval_lower: float
        confidence_interval_upper: float
    
    def compute(self, input_data: Input) -> Output:
        if input_data.seed is not None:
            np.random.seed(input_data.seed)
        
        S0 = input_data.spot_price
        K = input_data.strike_price
        T = input_data.time_to_maturity
        r = input_data.risk_free_rate
        sigma = input_data.volatility
        N = input_data.num_simulations
        
        # Generate random paths using geometric Brownian motion
        Z = np.random.standard_normal(N)
        ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
        
        # Calculate payoffs
        if input_data.option_type.lower() == "call":
            payoffs = np.maximum(ST - K, 0)
        else:  # put
            payoffs = np.maximum(K - ST, 0)
        
        # Discount to present value
        option_price = np.exp(-r * T) * np.mean(payoffs)
        
        # Calculate standard error and confidence interval
        std_error = np.std(payoffs) / np.sqrt(N)
        ci_lower = option_price - 1.96 * std_error
        ci_upper = option_price + 1.96 * std_error
        
        return self.Output(
            option_price=float(option_price),
            std_error=float(std_error),
            confidence_interval_lower=float(ci_lower),
            confidence_interval_upper=float(ci_upper)
        )


class RandomWalkUnit(ComputeUnit):
    """Simulate a random walk for statistical analysis."""
    
    class Input(ComputeInput):
        num_steps: int
        num_walks: int
        step_size: float = 1.0
        seed: int = None
    
    class Output(ComputeOutput):
        final_positions: list[float]
        mean_position: float
        std_position: float
        max_distance: float
    
    def compute(self, input_data: Input) -> Output:
        if input_data.seed is not None:
            np.random.seed(input_data.seed)
        
        # Generate random steps (-1 or +1)
        steps = np.random.choice([-1, 1], size=(input_data.num_walks, input_data.num_steps))
        steps = steps * input_data.step_size
        
        # Calculate cumulative positions
        positions = np.cumsum(steps, axis=1)
        final_positions = positions[:, -1]
        
        return self.Output(
            final_positions=final_positions.tolist(),
            mean_position=float(np.mean(final_positions)),
            std_position=float(np.std(final_positions)),
            max_distance=float(np.max(np.abs(final_positions)))
        )
