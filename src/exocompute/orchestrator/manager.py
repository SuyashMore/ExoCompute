import threading
import time
import requests

class NodeManager:
    def __init__(self, port_range_start=9000, port_range_end=9250):
        self.subscribers = {}  # port -> last_seen_timestamp
        self.busy_state = {}   # port -> bool
        self.port_range = list(range(port_range_start, port_range_end))
        self.lock = threading.Lock()
        self.shutdown_flag = False
        self.health_thread = None

    def start_health_check(self):
        self.health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_thread.start()

    def stop_health_check(self):
        self.shutdown_flag = True

    def _health_check_loop(self):
        while not self.shutdown_flag:
            with self.lock:
                to_remove = []
                for port, last_seen in list(self.subscribers.items()):
                    try:
                        r = requests.get(f"http://localhost:{port}/health", timeout=1)
                        is_busy = r.json().get("busy", False)
                        self.busy_state[port] = is_busy
                    except:
                        print(f"[ORCH] Node on port {port} is down")
                        to_remove.append(port)
                for port in to_remove:
                    self._remove_subscriber(port)
            time.sleep(3)

    def _remove_subscriber(self, port):
        if port in self.subscribers:
            del self.subscribers[port]
        self.busy_state.pop(port, None)

    def get_available_port(self):
        with self.lock:
            for port in self.port_range:
                if port not in self.subscribers:
                    self.subscribers[port] = time.time()
                    self.busy_state[port] = False
                    print(f"[ORCH] Assigned port {port}")
                    return port
        return None

    def unregister_node(self, port):
        with self.lock:
            if port in self.subscribers:
                self._remove_subscriber(port)
                print(f"[ORCH] Port {port} unregistered")

    def heartbeat(self, port):
        with self.lock:
            if port in self.subscribers:
                self.subscribers[port] = time.time()

    def get_nodes(self):
        with self.lock:
            return self.busy_state.copy()

    def mark_busy(self, port):
        with self.lock:
            self.busy_state[port] = True

    def mark_free(self, port):
        with self.lock:
            self.busy_state[port] = False
