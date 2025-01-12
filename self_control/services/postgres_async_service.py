import asyncpg
import os
from dotenv import load_dotenv
import asyncio
import random

load_dotenv()

class PostgresAsyncService:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        return await asyncpg.create_pool(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )

    async def init_pool(self):
        self.pool = await self.create_pool()

    async def wait_for_pool(self):
        while self.pool is None:
            await asyncio.sleep(0.1)

    def is_pool_empty(self):
        if self.pool:
            queue_size = self.pool._queue.qsize()
            total_connections = len(self.pool._holders)
            # Check if all connections are available and none are in use
            return queue_size == total_connections and all(not holder._in_use for holder in self.pool._holders)
        return True

    async def close_pool(self):
        if self.pool:
            await self.pool.close()
            print("Connection pool closed.")
        else :
            print("No connection pool to close.")

    async def insert_index(self, index):
        await self.wait_for_pool()
        print("Inserting index:", index)
        async with self.pool.acquire() as conn:
            await asyncio.sleep(1)
            await conn.execute("INSERT INTO indexes (index_num) VALUES ($1)", index)
            print("Inserted index:", index)

    async def insert_event(self, round_id, event_type, warning_signal_present, hit_count):
        """Insert a new event into the events table."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = """
                INSERT INTO events (
                    round_id, event_type, warning_signal_present, hit_count
                ) VALUES ($1, $2, $3, $4)
                """
                await conn.execute(query, round_id, event_type, warning_signal_present, hit_count)
        except Exception as e:
            print(f"Failed to insert event: {e}")
            await self.log_error_with_round_id(round_id, str(e))

    async def insert_cumulative_record(self, hit_count, session_id):
        """Insert a new row into the cumulative_record table."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = """
                INSERT INTO cumulative_record (hit_count, session_id)
                VALUES ($1, $2)
                """
                await conn.execute(query, hit_count, session_id)
        except Exception as e:
            print(f"Failed to insert into cumulative_record: {e}")
            await self.log_error_with_session_id(session_id, str(e))

    async def insert_peck(self, peck_data):
        """Insert a new peck into the pecks table."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = """
                INSERT INTO pecks (
                    x_start, y_start, x_pos, y_pos, screen_on, green_on, red_on, round_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """
                await conn.execute(query, 
                    peck_data['x_start'],
                    peck_data['y_start'],
                    peck_data['x_pos'],
                    peck_data['y_pos'],
                    peck_data['screen_on'],
                    peck_data['green_on'],
                    peck_data['red_on'],
                    peck_data['round_id']
                )
        except Exception as e:
            print(f"Failed to insert peck: {e}")
            await self.log_error_with_round_id(peck_data['round_id'], str(e))

    async def insert_round_results(self, round_id):
        """Insert round results for a specific round_id."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT insert_round_results($1);"
                await conn.execute(query, round_id)
        except Exception as e:
            print(f"Failed to insert round results: {e}")
            await self.log_error_with_round_id(round_id, str(e))

    async def check_round(self, round_id):
        """Check round for a specific round_id."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT check_round($1);"
                await conn.execute(query, round_id)
        except Exception as e:
            print(f"Failed to check round: {e}")
            await self.log_error_with_round_id(round_id, str(e))

    async def check_session(self, session_id):
        """Check session for a specific session_id."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT check_session($1);"
                await conn.execute(query, session_id)
        except Exception as e:
            print(f"Failed to check session: {e}")
            await self.log_error_with_session_id(session_id, str(e))

    async def insert_session_results(self, session_id):
        """Insert session results for a specific session_id."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT insert_session_results($1);"
                await conn.execute(query, session_id)
        except Exception as e:
            print(f"Failed to insert session results: {e}")
            await self.log_error_with_session_id(session_id, str(e))

    async def update_session_window_size(self, session_id, window_x, window_y):
        """Update window size for a specific session_id."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = """
                UPDATE sessions
                SET window_width = $1, 
                    window_height = $2
                WHERE session_id = $3
                """
                await conn.execute(query, window_x, window_y, session_id)
        except Exception as e:
            print(f"Failed to update window size: {e}")
            await self.log_error_with_session_id(session_id, str(e))

    async def log_error_with_session_id(self, session_id, error_message):
        """Log an error with session_id in a separate transaction."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT log_error_with_session_id($1, $2);"
                await conn.execute(query, session_id, error_message)
                print(f"Logged error with session_id: {session_id}")
        except Exception as e:
            print(f"Failed to log error with session_id: {e}")

    async def log_error_with_round_id(self, round_id, error_message):
        """Log an error with round_id in a separate transaction."""
        await self.wait_for_pool()
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT log_error_with_round_id($1, $2);"
                await conn.execute(query, round_id, error_message)
                print(f"Logged error with round_id: {round_id}")
        except Exception as e:
            print(f"Failed to log error with round_id: {e}")