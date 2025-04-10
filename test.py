import time
import asyncio
import threading

def thread_test():
    start = time.perf_counter()
    time.sleep(0.15)
    elapsed = (time.perf_counter() - start) * 1_000_000
    print(f"[Thread] Slept for {int(elapsed)} μs")

async def async_test():
    start = time.perf_counter()
    await asyncio.sleep(0.15)
    elapsed = (time.perf_counter() - start) * 1_000_000
    print(f"[Async] Slept for {int(elapsed)} μs")

def run_tests():
    print("Starting test...\n")

    t = threading.Thread(target=thread_test)
    t.start()
    t.join()

    asyncio.run(async_test())

run_tests()
