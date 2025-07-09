import asyncio
import time
from functools import partial
from exo_client import ExoCompute
from libs.mul import Mul  # Or another ComputeUnit with Input and compute()

ORCH_URL = "http://localhost:8000"
HTTP_TIMEOUT = 30.0

# Initialize the ExoCompute client with your unit class
exo = ExoCompute(ORCH_URL, Mul)

# 1. Use the Input Pydantic model from the compute unit
inputs = [Mul.Input(a=i, b=i + 1) for i in range(5000)]

async def compute_with_timeout(input_obj, timeout=HTTP_TIMEOUT):
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, partial(exo.compute, input_obj)),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        return RuntimeError(f"Timeout after {timeout}s for input: {input_obj}")
    except Exception as e:
        return e

async def main():
    start = time.perf_counter()

    # 2. Create tasks using the .dict() form of each Input
    tasks = [compute_with_timeout(input_obj) for input_obj in inputs]

    # 3. Run all tasks concurrently
    all_results = await asyncio.gather(*tasks)

    # 4. Separate successes and errors into two explicit arrays
    successes = []
    errors = []

    for result in all_results:
        if isinstance(result, Exception):
            errors.append(result)
        else:
            successes.append(result)

    duration = time.perf_counter() - start

    # 5. Print summary and results
    print(f"\n⏱️ Total time for {len(inputs)} tasks: {duration:.2f}s")
    print(f"✅ Successes: {len(successes)}")
    print(f"❌ Errors:    {len(errors)}\n")
    print(f"Result:{successes}")

if __name__ == "__main__":
    asyncio.run(main())
