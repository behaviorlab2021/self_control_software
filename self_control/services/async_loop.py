import asyncio
from threading import Thread
import logging

class AsyncLoop:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.queue = asyncio.Queue()
        self.loop_thread = Thread(target=self.run_asyncio_loop, daemon=True)
        self.loop_thread.start()
        self.loop.create_task(self.worker())

    def run_asyncio_loop(self):
        self.loop.run_forever()

    async def worker(self):
        while True:
            task = await self.queue.get()
            try:
                await task
            except Exception as e:
                logging.error("Error processing task: %s", e)
            finally:
                self.queue.task_done()

    def add_task(self, coro):
        print("Adding task")
        self.loop.call_soon_threadsafe(self.queue.put_nowait, coro)

    def has_tasks(self):
        return not self.queue.empty()
    
    async def shutdown(self):
        tasks = [t for t in asyncio.all_tasks(self.loop) if t is not asyncio.current_task(self.loop)]
        list(map(lambda task: task.cancel(), tasks))
        await asyncio.gather(*tasks, return_exceptions=True)
        self.loop.stop()

    def terminate(self):
        asyncio.run_coroutine_threadsafe(self.shutdown(), self.loop)
        self.loop_thread.join()
        logging.debug("Async loop terminated")
