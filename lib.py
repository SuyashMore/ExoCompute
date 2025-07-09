# lib.py

import time

def add_numbers(a, b, compute_time=1.0):
    """Add two numbers with artificial CPU load for compute_time seconds"""
    start = time.time()
    x = 0.0
    while time.time() - start < compute_time:
        # Useless math to keep the CPU busy
        x += (a * b) ** 0.5 / (a + 1)

    return a + b
