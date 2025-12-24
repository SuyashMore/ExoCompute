import asyncio
import time
import httpx

class NodeManager:
    def __init__(self, port_range_start=9000, port_range_end=9250):
        self.subscribers = {}  # port -> last_seen_timestamp
        self.busy_state = {}   # port -> bool
        self.port_range = list(range(port_range_start, port_range_end))
        self.lock = asyncio.Lock()
        self.shutdown_flag = False
        self.health_task = None

    def start_health_check(self):
        self.health_task = asyncio.create_task(self._health_check_loop())

    def stop_health_check(self):
        self.shutdown_flag = True
        if self.health_task:
            self.health_task.cancel()

    async def _health_check_loop(self):
        async with httpx.AsyncClient() as client:
            while not self.shutdown_flag:
                try:
                    # Snapshot subscribers to avoid holding lock during network calls
                    async with self.lock:
                        current_subscribers = list(self.subscribers.items())

                    to_remove = []
                    for port, last_seen in current_subscribers:
                        try:
                            r = await client.get(f"http://localhost:{port}/health", timeout=1.0)
                            is_busy = r.json().get("busy", False)
                            async with self.lock:
                                if port in self.subscribers: # Check if still exists
                                    self.busy_state[port] = is_busy
                        except Exception as e:
                            print(f"[ORCH] Node on port {port} is down: {e}")
                            to_remove.append(port)
                    
                    if to_remove:
                        async with self.lock:
                            for port in to_remove:
                                self._remove_subscriber(port)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"[ORCH] Health check error: {e}")
                
                await asyncio.sleep(3)

    def _remove_subscriber(self, port):
        # Internal helper, assumes lock is held
        if port in self.subscribers:
            del self.subscribers[port]
        self.busy_state.pop(port, None)

    async def get_available_port(self):
        async with self.lock:
            for port in self.port_range:
                if port not in self.subscribers:
                    self.subscribers[port] = time.time()
                    self.busy_state[port] = False
                    print(f"[ORCH] Assigned port {port}")
                    return port
        return None

    async def unregister_node(self, port):
        async with self.lock:
            if port in self.subscribers:
                self._remove_subscriber(port)
                print(f"[ORCH] Port {port} unregistered")

    async def heartbeat(self, port):
        async with self.lock:
            if port in self.subscribers:
                self.subscribers[port] = time.time()

    async def get_nodes(self):
        async with self.lock:
            return self.busy_state.copy()

    async def mark_busy(self, port):
        async with self.lock:
            self.busy_state[port] = True

    async def mark_free(self, port):
        async with self.lock:
            self.busy_state[port] = False
