import asyncio
import httpx
import time
from .manager import NodeManager

class TaskScheduler:
    def __init__(self, node_manager: NodeManager):
        self.node_manager = node_manager
        self.retry_limit = 100
        self.retry_delay = 0.1
        self.redundancy_factor = 2

    async def submit_task(self, payload: dict):
        attempted_ports = set()

        async with httpx.AsyncClient() as client:
            for attempt in range(self.retry_limit):
                ports_to_try = []

                # 1. Select nodes
                available_nodes_map = await self.node_manager.get_nodes()
                available_nodes = [
                    port for port, busy in available_nodes_map.items()
                    if not busy and port not in attempted_ports
                ]

                if not available_nodes:
                    # print(f"[ORCH] No available nodes, sleeping...")
                    pass
                else:
                    # Naive selection: pick first N
                    selected = available_nodes[:self.redundancy_factor]
                    for port in selected:
                         await self.node_manager.mark_busy(port)
                         ports_to_try.append(port)

                if not ports_to_try:
                    await asyncio.sleep(self.retry_delay)
                    continue

                # 2. Dispatch tasks
                tasks = []
                for port in ports_to_try:
                    tasks.append(asyncio.create_task(self._send_to_port(client, port, payload)))

                done, _ = await asyncio.wait(tasks)

                # 3. Process results
                for d in done:
                    port_used, result = await d
                    attempted_ports.add(port_used)
                    if result and "result" in result:
                        print(f"[ORCH] Success from {port_used}")
                        return {"result": result["result"]}

                print(f"[ORCH] Attempt {attempt + 1}/{self.retry_limit} failed. Retrying...")
                await asyncio.sleep(self.retry_delay)

            raise Exception("No available subscribers or all failed")

    async def _send_to_port(self, client, port, payload):
        try:
            print(f"[ORCH] Sending task to port {port}")
            resp = await client.post(f"http://localhost:{port}/compute", json=payload, timeout=2.0)
            print(f"[ORCH] Response from port {port}: {resp.text}")
            return port, resp.json()
        except Exception as e:
            print(f"[ORCH] Error with port {port}: {e}")
            return port, None
        finally:
            await self.node_manager.mark_free(port)
