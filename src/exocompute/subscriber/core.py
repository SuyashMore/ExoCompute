import requests
import time
import threading
import sys
from importlib import import_module
from exocompute.libs.base import ComputeUnit

class SubscriberNode:
    def __init__(self, orchestrator_url="http://localhost:8000"):
        self.orchestrator_url = orchestrator_url
        self.assigned_port = None
        self.busy = False
        self.shutdown_flag = False
        self.heartbeat_thread = None

    def register(self):
        try:
            r = requests.get(f"{self.orchestrator_url}/get_port")
            port = r.json().get("port")
            if port:
                self.assigned_port = port
                print(f"[SUB] Got assigned port: {port}")
                return port
            else:
                print(f"[SUB] No port assigned.")
                return None
        except Exception as e:
            print(f"[SUB] Registration failed: {e}")
            return None

    def unregister(self):
        if self.assigned_port:
            try:
                requests.post(f"{self.orchestrator_url}/unregister", json={"port": self.assigned_port})
                print(f"[SUB] Unregistered from orchestrator (port {self.assigned_port})")
            except Exception as e:
                print(f"[SUB] Failed to unregister: {e}")

    def start_heartbeat(self):
        self.shutdown_flag = False
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

    def stop_heartbeat(self):
        self.shutdown_flag = True

    def _heartbeat_loop(self):
        while not self.shutdown_flag:
            try:
                requests.post(f"{self.orchestrator_url}/health_check", json={"port": self.assigned_port})
            except Exception as e:
                print(f"[SUB] Heartbeat failed: {e}")
            time.sleep(5)

    def process_compute(self, unit_type: str, data: dict):
        self.busy = True
        try:
            # Module mapping for compute units in different files
            module_map = {
                'MatrixMultiplyUnit': 'matrix_ops',
                'MatrixInverseUnit': 'matrix_ops',
                'EigenvalueUnit': 'matrix_ops',
                'MatrixSVDUnit': 'matrix_ops',
                'PiEstimationUnit': 'monte_carlo',
                'OptionPricingUnit': 'monte_carlo',
                'RandomWalkUnit': 'monte_carlo',
                'GaussianBlurUnit': 'image_ops',
                'EdgeDetectionUnit': 'image_ops',
                'ImageRotateUnit': 'image_ops',
                'HistogramEqualizationUnit': 'image_ops',
            }
            
            # Dynamic import from exocompute.libs
            try:
                # Try module mapping first, fall back to lowercase unit name
                module_name = module_map.get(unit_type, unit_type.lower())
                module = import_module(f"exocompute.libs.{module_name}")
                unit_class: type[ComputeUnit] = getattr(module, unit_type)
            except Exception as e:
                raise ValueError(f"Invalid compute unit '{unit_type}': {e}")

            try:
                input_obj = unit_class.Input(**data)
            except Exception as e:
                raise ValueError(f"Failed to parse input for '{unit_type}': {e}")

            try:
                unit_instance = unit_class()
                output_obj = unit_instance.compute(input_obj)
                # Use model_dump() for Pydantic v2
                return output_obj.model_dump()
            except Exception as e:
                raise RuntimeError(f"Failed to compute: {e}")

        finally:
            self.busy = False
