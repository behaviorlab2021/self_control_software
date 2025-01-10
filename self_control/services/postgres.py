import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from dotenv import load_dotenv
import os
import asyncio
import asyncpg

# Load environment variables from .env file
load_dotenv()

async def connect_to_db():
    conn = await asyncpg.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

class ExperimentDB:
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432)
        }
        self.connection = None
        self.connect()  # Ensure connection is established

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"Failed to connect to database: {e}")

    def close(self):
        if self.connection:
            self.connection.close()

    def insert_subject(self, subject_name):
        """Insert a new subject into the subjects table."""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO subjects (subject_name) VALUES (%s) RETURNING subject_id"
            cursor.execute(query, (subject_name,))
            subject_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            print(f"Inserted new subject with ID {subject_id}.")
            return subject_id
        except Exception as e:
            print(f"Failed to insert subject: {e}")
            return None

    def select_subject_by_name(self, subject_name):
        """Fetch a subject by its name."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM subjects WHERE subject_name = %s"
            cursor.execute(query, (subject_name,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Subject:", result)
                return result
            else:
                print(f"No subject found with name {subject_name}.")
                return None
        except Exception as e:
            print(f"Failed to fetch subject: {e}")
            return None

    def find_last_session_by_subject(self, subject_id):
        """Find the last session for a specific subject."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = """
            SELECT * FROM sessions
            WHERE subject_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """
            cursor.execute(query, (subject_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Found last session for subject.")
                return result
            else:
                print("No sessions found for subject.")
                return None
        except Exception as e:
            print(f"Failed to find last session for subject: {e}")
            return None

    def select_all_subjects(self):
        """Fetch all subjects from the subjects table."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM subjects"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Failed to fetch subjects: {e}")
            return []

    def select_all_modes(self):
        """Fetch all modes from the experiment_modes table."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM experiment_modes ORDER BY mode_id;"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Failed to fetch modes: {e}")
            return []

    def log_error_with_session_id(self, session_id, error_message):
        """Log an error with session_id in a separate transaction."""
        try:
            error_connection = psycopg2.connect(**self.db_config)
            cursor = error_connection.cursor()

            query = "SELECT log_error_with_session_id(%s, %s);"
            cursor.execute(query, (session_id, error_message))
            error_connection.commit()
            cursor.close()
            error_connection.close()
        except Exception as e:
            print(f"Failed to log error with session_id: {e}")

    async def async_log_error_with_session_id(self, session_id, error_message):
        """Log an error with session_id in a separate transaction."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    "SELECT log_error_with_session_id($1, $2);",
                    session_id, error_message
                )
        except Exception as e:
            print(f"Failed to log error with session_id: {e}")
        finally:
            await conn.close()

    def log_error_with_round_id(self, round_id, error_message):
        """Log an error with round_id in a separate transaction."""
        try:
            error_connection = psycopg2.connect(**self.db_config)
            cursor = error_connection.cursor()
            query = "SELECT log_error_with_round_id(%s, %s);"
            cursor.execute(query, (round_id, error_message))
            error_connection.commit()
            cursor.close()
            error_connection.close()
        except Exception as e:
            print(f"Failed to log error with round_id: {e}")

    async def async_log_error_with_round_id(self, round_id, error_message):
        """Log an error with round_id in a separate transaction."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    "SELECT log_error_with_round_id($1, $2);",
                    round_id, error_message
                )
        except Exception as e:
            print(f"Failed to log error with round_id: {e}")
        finally:
            await conn.close()

    def insert_session(self, session_data):
        """Insert a new session into the sessions table and return the session_id."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO sessions (
                session_id,
                reinforcement_ratio, 
                warning_hits, 
                punishment_duration, 
                feed_time, 
                total_reinforcements, 
                consecutive_warnings_limit, 
                warning_alarm_volume, 
                warning_display_volume, 
                subject_id, 
                mode_id, 
                is_spot_on,
                punishment_periodicity, 
                warning_duration, 
                time_before_warning_signal, 
                highlight_warning_signal, 
                warning_signal_position, 
                button_height, 
                button_size,
                grace_radius,
                peck_slide,
                comments
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING session_id
            """
            cursor.execute(query, (
                session_data['session_id'],
                session_data['reinforcement_ratio'], 
                session_data['warning_hits'], 
                session_data['punishment_duration'], 
                session_data['feed_time'], 
                session_data['total_reinforcements'], 
                session_data['consecutive_warnings_limit'], 
                session_data['warning_alarm_volume'], 
                session_data['warning_display_volume'], 
                session_data['subject_id'], 
                session_data['mode_id'], 
                session_data['is_spot_on'], 
                session_data['punishment_periodicity'], 
                session_data['warning_duration'], 
                session_data['time_before_warning_signal'], 
                session_data['highlight_warning_signal'], 
                session_data['warning_signal_position'], 
                session_data['button_height'],
                session_data['button_size'],
                session_data['grace_radius'],
                session_data['peck_slide'], 
                session_data['comments']
            ))
            self.connection.commit()
            cursor.close()
            print(f"Inserted new session with ID {session_data['session_id']}.")
            return session_data['session_id']
        except Exception as e:
            print(f"Failed to insert session: {e}")
            self.log_error_with_session_id(session_data['session_id'], str(e))
            return None

    def insert_session_with_uuid(self, session_data):
        """Insert a new session into the sessions table with a UUID."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO sessions (
                session_id,
                reinforcement_ratio, 
                warning_hits, 
                punishment_duration, 
                feed_time, 
                total_reinforcements, 
                consecutive_warnings_limit, 
                warning_alarm_volume, 
                warning_display_volume, 
                subject_id, 
                mode_id, 
                is_spot_on,
                punishment_periodicity, 
                warning_duration, 
                time_before_warning_signal, 
                highlight_warning_signal, 
                warning_signal_position, 
                button_height,
                button_size,
                grace_radius,
                peck_slide, 
                comments
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            session_id = session_data.get('session_id', str(uuid.uuid4()))
            cursor.execute(query, (
                session_id,
                session_data['reinforcement_ratio'], 
                session_data['warning_hits'], 
                session_data['punishment_duration'], 
                session_data['feed_time'], 
                session_data['total_reinforcements'], 
                session_data['consecutive_warnings_limit'], 
                session_data['warning_alarm_volume'], 
                session_data['warning_display_volume'], 
                session_data['subject_id'], 
                session_data['mode_id'], 
                session_data['is_spot_on'], 
                session_data['punishment_periodicity'], 
                session_data['warning_duration'], 
                session_data['time_before_warning_signal'], 
                session_data['highlight_warning_signal'], 
                session_data['warning_signal_position'], 
                session_data['button_height'],
                session_data['button_size'],
                session_data['grace_radius'],
                session_data['peck_slide'], 
                session_data['comments']
            ))
            self.connection.commit()
            cursor.close()
            print(f"Inserted new session with UUID {session_id}.")
        except Exception as e:
            print(f"Failed to insert session: {e}")
            self.log_error_with_session_id(session_id, str(e))

    def insert_event(self, round_id, event_type, warning_signal_present, hit_count):
        """Insert a new event into the events table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO events (
                round_id, event_type, warning_signal_present, hit_count
            ) VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (
                round_id, event_type, warning_signal_present, hit_count
            ))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Failed to insert event: {e}")
            self.log_error_with_round_id(round_id, str(e))

    async def async_insert_event(self, round_id, event_type, warning_signal_present, hit_count):
        """Insert a new event into the events table."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO events (
                        round_id, event_type, warning_signal_present, hit_count
                    ) VALUES ($1, $2, $3, $4)
                    """,
                    round_id, event_type, warning_signal_present, hit_count
                )
        except Exception as e:
            print(f"Failed to insert event: {e}")
            await self.async_log_error_with_round_id(round_id, str(e))
        finally:
            await conn.close()

    def insert_cumulative_record(self, hit_count, session_id):
        """Insert a new row into the cumulative_record table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO cumulative_record (hit_count, session_id)
            VALUES (%s, %s)
            """
            cursor.execute(query, (hit_count, session_id))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Failed to insert into cumulative_record: {e}")
            self.log_error_with_session_id(session_id, str(e))

    async def async_insert_cumulative_record(self, hit_count, session_id):
        """Insert a new row into the cumulative_record table."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO cumulative_record (hit_count, session_id)
                    VALUES ($1, $2)
                    """,
                    hit_count, session_id
                )
        except Exception as e:
            print(f"Failed to insert into cumulative_record: {e}")
            await self.async_log_error_with_session_id(session_id, str(e))
        finally:
            await conn.close()

    def select_session_by_id(self, session_id):
        """Fetch a session by its ID."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM sessions WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Session:", result)
                return result
            else:
                print(f"No session found with ID {session_id}.")
                return None
        except Exception as e:
            print(f"Failed to fetch session: {e}")
            self.log_error_with_session_id(session_id, str(e))
            return None

    def edit_session_subject(self, session_id, new_subject):
        """Edit the subject of an session by its ID."""
        try:
            cursor = self.connection.cursor()
            query = "UPDATE session SET subject = %s, updated_at = NOW() WHERE session_id = %s"
            cursor.execute(query, (new_subject, session_id))
            self.connection.commit()
            cursor.close()
            print(f"Updated session ID {session_id} with new subject: {new_subject}")
        except Exception as e:
            print(f"Failed to update session subject: {e}")
            self.log_error_with_session_id(session_id, str(e))

    def find_session_by_id(self, session_id):
        """Find and return a session based on session_id."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM sessions WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Session found:", result)
                return result
            else:
                print(f"No session found with ID {session_id}.")
                return None
        except Exception as e:
            print(f"Failed to find session: {e}")
            self.log_error_with_session_id(session_id, str(e))
            return None

    def find_subject_by_id(self, subject_id):
        """Find and return a subject based on subject_id."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM subjects WHERE subject_id = %s"
            cursor.execute(query, (subject_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Subject found:", result)
                return result
            else:
                print(f"No subject found with ID {subject_id}.")
                return None
        except Exception as e:
            print(f"Failed to find subject: {e}")
            self.log_error_with_session_id(subject_id, str(e))
            return None

    def insert_round_data(self, round_data):
        """Helper function to inject round data into the rounds table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO rounds (
                session_id, round_index, warning_index, warning_quarter, reinforcers_count
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING round_id
            """
            cursor.execute(query, (
                round_data['session_id'],
                round_data['round_index'],
                round_data['warning_index'],
                round_data['warning_quarter'],
                round_data['reinforcers_count']
            ))
            round_id = cursor.fetchone()[0]
            cursor.close()
            return round_id
        except Exception as e:
            print(f"Failed to insert round data: {e}")
            self.log_error_with_round_id(round_data['round_id'], str(e))
            return None

    def insert_peck(self, peck_data):
        """Insert a new peck into the pecks table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO pecks (
                x_start, y_start, x_pos, y_pos, screen_on, green_on, red_on, round_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                peck_data['x_start'],
                peck_data['y_start'],
                peck_data['x_pos'],
                peck_data['y_pos'],
                peck_data['screen_on'],
                peck_data['green_on'],
                peck_data['red_on'],
                peck_data['round_id']
            ))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Failed to insert peck: {e}")
            self.log_error_with_round_id(peck_data['round_id'], str(e))

    async def async_insert_peck(self, peck_data):
        """Insert a new peck into the pecks table."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO pecks (
                        x_start, y_start, x_pos, y_pos, screen_on, green_on, red_on, round_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
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
            await self.async_log_error_with_round_id(peck_data['round_id'], str(e))
        finally:
            await conn.close()

    def insert_round_results(self, round_id):
        """Insert round results for a specific round_id."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT insert_round_results(%s);"
            cursor.execute(query, (round_id,))
            self.connection.commit()
            cursor.close()
            print(f"Inserted round results for round ID {round_id}.")
        except Exception as e:
            print(f"Failed to insert round results: {e}")
            self.log_error_with_round_id(round_id, str(e))

    async def async_insert_round_results(self, round_id):
        """Insert round results for a specific round_id."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    "SELECT insert_round_results($1);",
                    round_id
                )
            print(f"Inserted round results for round ID {round_id}.")
        except Exception as e:
            print(f"Failed to insert round results: {e}")
            await self.async_log_error_with_round_id(round_id, str(e))
        finally:
            await conn.close()

    def check_round(self, round_id):
        """Check round for a specific round_id."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT check_round(%s);"
            cursor.execute(query, (round_id,))  # Add comma here to make it a tuple
            self.connection.commit()
            cursor.close()
            print(f"Checked round for round ID {round_id}.")
        except Exception as e:
            print(f"Failed to check round: {e}")
            self.log_error_with_round_id(round_id, str(e))

    async def async_check_round(self, round_id):
        """Check round for a specific round_id."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    "SELECT check_round($1);",
                    round_id
                )
            print(f"Checked round for round ID {round_id}.")
        except Exception as e:
            print(f"Failed to check round: {e}")
            await self.async_log_error_with_round_id(round_id, str(e))
        finally:
            await conn.close()

    def check_session(self, session_id):
        """Check session for a specific session_id."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT check_session(%s);"
            cursor.execute(query, (session_id,))  # Add comma here to make it a tuple
            self.connection.commit()
            cursor.close()
            print(f"Checked session for session ID {session_id}.")
        except Exception as e:
            print(f"Failed to check session: {e}")
            self.log_error_with_round_id(session_id, str(e))

    async def async_check_session(self, session_id):
        """Check session for a specific session_id."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    "SELECT check_session($1);",
                    session_id
                )
            print(f"Checked session for session ID {session_id}.")
        except Exception as e:
            print(f"Failed to check session: {e}")
            await self.async_log_error_with_round_id(session_id, str(e))
        finally:
            await conn.close()

    def insert_session_results(self, session_id):
        """Insert session results for a specific session_id."""
        try:
            cursor = self.connection.cursor()
            query = "SELECT insert_session_results(%s);"
            cursor.execute(query, (session_id,))
            self.connection.commit()
            cursor.close()
            print(f"Inserted session results for session ID {session_id}.")
        except Exception as e:
            print(f"Failed to insert session results: {e}")
            self.log_error_with_session_id(session_id, str(e))

    async def async_insert_session_results(self, session_id):
        """Insert session results for a specific session_id."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    "SELECT insert_session_results($1);",
                    session_id
                )
            print(f"Inserted session results for session ID {session_id}.")
        except Exception as e:
            print(f"Failed to insert session results: {e}")
            await self.async_log_error_with_round_id(session_id, str(e))
        finally:
            await conn.close()

    def update_session_window_size(self, session_id, window_x, window_y):
        """Update window size for a specific session_id."""
        try:
            cursor = self.connection.cursor()
            query = """
            UPDATE sessions
            SET window_width = %s, 
                window_height = %s
            WHERE session_id = %s
            """
            cursor.execute(query, (window_x, window_y, session_id))
            self.connection.commit()
            cursor.close()
            print(f"Updated window size for session ID {session_id}.")
        except Exception as e:
            print(f"Failed to update window size: {e}")
            self.log_error_with_session_id(session_id, str(e))

    async def async_update_session_window_size(self, session_id, window_x, window_y):
        """Update window size for a specific session_id."""
        conn = await connect_to_db()
        try:
            async with conn.transaction():
                await conn.execute(
                    """
                    UPDATE sessions
                    SET window_width = $1, 
                        window_height = $2
                    WHERE session_id = $3
                    """,
                    window_x, window_y, session_id
                )
            print(f"Updated window size for session ID {session_id}.")
        except Exception as e:
            print(f"Failed to update window size: {e}")
            await self.async_log_error_with_round_id(session_id, str(e))
        finally:
            await conn.close()

    def get_session_basic_info(self, session_id):
        """Fetch session created_at and subject name by session_id."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = """
            SELECT s.created_at as experiment_date, sub.subject_name, s.mode_id
            FROM sessions s
            JOIN subjects sub ON s.subject_id = sub.subject_id
            WHERE s.session_id = %s
            """
            cursor.execute(query, (session_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Session Basic Info:", result)
                return result
            else:
                print(f"No session found with ID {session_id}.")
                return None
        except Exception as e:
            print(f"Failed to fetch session basic info: {e}")
            self.log_error_with_session_id(session_id, str(e))
            return None
