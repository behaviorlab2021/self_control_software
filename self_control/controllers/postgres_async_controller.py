from self_control_software.self_control.services.async_loop import AsyncLoop
from self_control_software.self_control.services.postgres_async_service import PostgresAsyncService
from self_control_software.self_control.utils.time_functions import get_time_now, get_time_dif
import asyncio
import time

class PostgresAsyncController:
    def __init__(self):
        self.loop = AsyncLoop()
        self.postgres_service = PostgresAsyncService()
        self.add_task(self.init_services())

    async def init_services(self):
        await self.postgres_service.init_pool()
     
    def add_task(self, coro):
        self.loop.add_task(coro)

    def is_worker_busy(self):
        return self.loop.has_tasks()

    def is_pool_empty(self):
        return self.postgres_service.is_pool_empty()



    def shutdown(self):
        # Wait for remaining jobs to complete
        while self.is_worker_busy():
            time.sleep(0.1)
        while not self.is_pool_empty():
            time.sleep(0.1)
        
        # Close the connection pool
        self.close_pool()
        # Terminate the async loop
        self.terminate_loop()

    def insert_data(self, data):
        self.loop.add_task(self.postgres_service.insert_index(data))
    
    def terminate_loop(self):
        self.loop.terminate()
        
    def close_pool(self):
        future = asyncio.run_coroutine_threadsafe(self.postgres_service.close_pool(), self.loop.loop)
        future.result()  # Wait for the close_pool coroutine to complete

    def inject_event(self, round_id, event_type, warning_signal_present, hit_count):
        self.loop.add_task(self.postgres_service.insert_event(round_id, event_type, warning_signal_present, hit_count))

    def inject_cumulative_record(self, hit_count, session_id):
        self.loop.add_task(self.postgres_service.insert_cumulative_record(hit_count, session_id))

    def inject_peck(self, x_start, y_start, x_pos, y_pos, screen_on, green_on, red_on, round_id):
        peck_data = {
            'x_start': x_start,
            'y_start': y_start,
            'x_pos': x_pos,
            'y_pos': y_pos,
            'screen_on': screen_on,
            'green_on': green_on,
            'red_on': red_on,
            'round_id': round_id
        }
        self.loop.add_task(self.postgres_service.insert_peck(peck_data))

    def trigger_round_results(self, round_id):
        self.loop.add_task(self.postgres_service.insert_round_results(round_id))

    def trigger_check_round(self, round_id):
        self.loop.add_task(self.postgres_service.check_round(round_id))

    def trigger_check_session(self, session_id):
        self.loop.add_task(self.postgres_service.check_session(session_id))

    def trigger_session_results(self, session_id):
        self.loop.add_task(self.postgres_service.insert_session_results(session_id))

    def update_session_window_size(self, session_id, window_x, window_y):
        self.loop.add_task(self.postgres_service.update_session_window_size(session_id, window_x, window_y))