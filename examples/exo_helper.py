"""Simple helper for submitting tasks to ExoCompute."""
from exocompute.client import ExoCompute


def submit_task(unit_class, input_dict, orch_url="http://localhost:8000"):
    """
    Submit a task to the ExoCompute orchestrator.
    
    Args:
        unit_class: The compute unit class (e.g., MatrixMultiplyUnit)
        input_dict: Dictionary of input parameters
        orch_url: Orchestrator URL
        
    Returns:
        Result dictionary from the compute unit
    """
    client = ExoCompute(orch_url, unit_class)
    input_data = unit_class.Input(**input_dict)
    return client.compute(input_data)
