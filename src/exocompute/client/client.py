import requests
from typing import Type
from exocompute.libs.base import ComputeInput

class ExoCompute:
    def __init__(self, orchestrator_url: str, compute_unit: Type):
        self.orchestrator_url = orchestrator_url.rstrip("/")
        self.unit_class = compute_unit
        self.unit_name = compute_unit.__name__

    def compute(self, input_data: ComputeInput) -> dict:
        payload = {
            "unit": self.unit_name,
            "input": input_data.model_dump(),
        }

        try:
            resp = requests.post(f"{self.orchestrator_url}/submit_task", json=payload, timeout=30.0)
            resp.raise_for_status()
            result = resp.json()
            
            if "result" not in result:
                raise Exception(f"Missing 'result' key in response: {result}")
            return result["result"]
        except requests.exceptions.RequestException as e:
            print(f"[ExoCompute] HTTP request failed: {e}")
            raise
        except Exception as e:
            print(f"[ExoCompute] Error: {e}")
            raise
