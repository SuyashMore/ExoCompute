import asyncio
import aiohttp
import random
import time

ORCHESTRATOR_URL = "http://localhost:8000/compute"
MAX_RETRIES = 100
RETRY_DELAY = 0.5  # Fixed delay
JITTER_RANGE = (0.2, 0.5)

array_a = [i for i in range(1, 10)]
array_b = [i * 10 for i in range(1, 10)]

async def send_request(session, a, b):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.post(ORCHESTRATOR_URL, json={"a": a, "b": b}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["result"]
                else:
                    print(f"[WARN] Attempt {attempt}: {a}+{b} failed (status {resp.status})")
        except Exception as e:
            print(f"[ERROR] Attempt {attempt}: {a}+{b} exception: {e}")
        
        if attempt < MAX_RETRIES:
            jitter = random.uniform(*JITTER_RANGE)
            delay = RETRY_DELAY + jitter
            print(f"[RETRY] {a}+{b} in {delay:.2f}s...")
            await asyncio.sleep(delay)

    print(f"[FAIL] {a}+{b} failed after {MAX_RETRIES} attempts.")
    return None

async def main():
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, a, b) for a, b in zip(array_a, array_b)]
        results = await asyncio.gather(*tasks)

    duration = time.time() - start_time
    print(f"\n✅ Final Results: {results}")
    print(f"⏱️ Total compute time: {duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
