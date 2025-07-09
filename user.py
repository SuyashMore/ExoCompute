import asyncio
import httpx
import time
import random

ORCHESTRATOR_URL = "http://localhost:8000/submit_task"

arr1 = [i for i in range(100)]
arr2 = [i * 2 for i in range(100)]
results = [None] * len(arr1)

RETRY_LIMIT = 1
RETRY_DELAY = 1.0  # seconds

async def send_task(index, a, b, client):
    for attempt in range(RETRY_LIMIT):
        try:
            print("Sending request")
            resp = await client.post(ORCHESTRATOR_URL, json={"a": a, "b": b})
            data = resp.json()
            if "result" in data:
                print(f"[USER] ✅ add({a}, {b}) = {data['result']}")
                results[index] = data["result"]
                return
            else:
                print(f"[USER] ⚠️ Error add({a}, {b}): {data.get('error')}")
        except Exception as e:
            print(f"[USER] ❌ Exception add({a}, {b}) - {e}")

        # Retry delay
        await asyncio.sleep(RETRY_DELAY + random.uniform(0, 0.5))

    print(f"[USER] ❌ Failed to compute add({a}, {b}) after {RETRY_LIMIT} retries")

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
