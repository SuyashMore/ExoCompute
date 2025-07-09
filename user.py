import asyncio
import httpx
import time
import random
from libs.adder import Adder  # Import the actual ComputeUnit class
from libs.sub import Sub  # Import the actual ComputeUnit class
from libs.mul import Mul  # Import the actual ComputeUnit class
from libs.sqr import Sqr  # Import the actual ComputeUnit class


ORCHESTRATOR_URL = "http://localhost:8000/submit_task"

arr1 = [i for i in range(50)]
arr2 = [i * 2 for i in range(50)]
results = [None] * len(arr1)

RETRY_LIMIT = 1
RETRY_DELAY = 1.0  # seconds

UNIT_CLASS = Sqr  # Swap this to any other ComputeUnit subclass if needed

async def send_task(index, a, b, client):
    # Prepare input and serialize to dict
    compute_input = UNIT_CLASS.Input(a=a)
    payload = {
        "unit": UNIT_CLASS.__name__,
        "input": compute_input.model_dump()
    }

    for attempt in range(RETRY_LIMIT):
        try:
            resp = await client.post(ORCHESTRATOR_URL, json=payload)
            data = resp.json()
            if "result" in data:
                print(f"[USER] ✅ {UNIT_CLASS.__name__}({a}, {b}) = {data['result']}")
                results[index] = data["result"]
                return
            else:
                print(f"[USER] ⚠️ Error {UNIT_CLASS.__name__}({a}, {b}): {data.get('error')}")
        except Exception as e:
            print(f"[USER] ❌ Exception {UNIT_CLASS.__name__}({a}, {b}) - {e}")

        # Retry delay
        await asyncio.sleep(RETRY_DELAY + random.uniform(0, 0.5))

    print(f"[USER] ❌ Failed to compute {UNIT_CLASS.__name__}({a}, {b}) after {RETRY_LIMIT} retries")

async def main():
    start_time = time.time()

    async with httpx.AsyncClient(timeout=100.0) as client:
        tasks = [
            send_task(i, a, b, client)
            for i, (a, b) in enumerate(zip(arr1, arr2))
        ]
        await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    print("\n=== Summary ===")
    print("Results:", results)
    print(f"Total computation time: {total_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
