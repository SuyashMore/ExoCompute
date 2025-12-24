import argparse
import subprocess
import signal
import sys
import time
from .core import SubscriberNode
from .server import run_subscriber_server

def start_subscriber():
    node = SubscriberNode()
    port = node.register()
    if not port:
        print("[SUB] Could not register. Exiting.")
        return
    
    run_subscriber_server(port, node)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    if args.count == 1:
        start_subscriber()
    else:
        processes = []
        # We need a way to launch multiple instances.
        # Since we are in a package now, we can use `python -m exocompute.subscriber`?
        # But we need an entry point.
        
        # We can just spawn this same script.
        # Assuming this text is in __init__.py and we call it via -m exocompute.subscriber
        
        for _ in range(args.count):
             # We use sys.executable and -m
             proc = subprocess.Popen([sys.executable, "-m", "exocompute.subscriber"])
             processes.append(proc)

        def multi_kill(sig, frame):
            print("\n[SPAWN] Shutting down all subprocesses...")
            for p in processes:
                p.terminate()
            sys.exit(0)

        signal.signal(signal.SIGINT, multi_kill)
        signal.signal(signal.SIGTERM, multi_kill)

        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
