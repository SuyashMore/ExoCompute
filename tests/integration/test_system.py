import unittest
import threading
import time
import requests
from uvicorn import Config, Server
import asyncio
import signal
import os

# We will spin up the actual orchestrator and one subscriber in separate threads/processes
# For simplicity in test, we can use threads if uvicorn allows, or just subprocesses.
# Using subprocesses is safer for full integration test to avoid event loop conflicts.

import subprocess
import sys

class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.join(os.getcwd(), "src")
        
        # Start Orchestrator
        cls.orch_proc = subprocess.Popen(
            [sys.executable, "-m", "exocompute.orchestrator"],
            cwd=os.getcwd(),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3) # Wait for startup

        # Start Subscriber
        cls.sub_proc = subprocess.Popen(
            [sys.executable, "-m", "exocompute.subscriber"],
            cwd=os.getcwd(),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3) # Wait for registration

    @classmethod
    def tearDownClass(cls):
        # We terminate first to ensure we can capture output
        cls.sub_proc.terminate()
        cls.orch_proc.terminate()
        try:
            cls.sub_proc.wait(timeout=2)
            cls.orch_proc.wait(timeout=2)
        except Exception:
            cls.sub_proc.kill()
            cls.orch_proc.kill()
        
        cls._print_logs("Orchestrator", cls.orch_proc)
        cls._print_logs("Subscriber", cls.sub_proc)

    @classmethod
    def _print_logs(cls, name, proc):
        # process is ended now
        try:
            outs, errs = proc.communicate(timeout=1)
            if outs or errs:
                print(f"[{name}] STDOUT: {outs.decode(errors='ignore') if outs else ''}")
                print(f"[{name}] STDERR: {errs.decode(errors='ignore') if errs else ''}")
        except Exception as e:
            print(f"[{name}] Could not get logs: {e}")

    def test_end_to_end_computation(self):
        # Wait for orchestrator
        for _ in range(10):
            try:
                requests.get("http://localhost:8000/get_port", timeout=1)
                break
            except:
                time.sleep(1)
        else:
            self.fail("Orchestrator failed to start")

        # Wait for subscriber to register
        # Only way to know is if orchestrator assignes ports.
        # But we can try submitting a task.
        
        # Use simple requests to submit a task
        payload = {
            "unit": "Mul",
            "input": {"a": 10, "b": 5}
        }
        
        # Retry a few times
        for _ in range(5):
            try:
                resp = requests.post("http://localhost:8000/submit_task", json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    self.assertIn("result", data)
                    self.assertEqual(data["result"]["res"], 50)
                    return
            except Exception:
                pass
            time.sleep(1)

        self.fail("Computation failed or timed out")

if __name__ == '__main__':
    unittest.main()
