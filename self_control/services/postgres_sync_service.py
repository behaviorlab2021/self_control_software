import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from dotenv import load_dotenv
import os
import asyncio
import asyncpg

# Load environment variables from .env file
load_dotenv()

class PostgresSyncService:
    def __init__(self):
        self.db_config = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432)
        }
        self.connection = None
        # self.connect()  # Ensure connection is established

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"Failed to connect to database: {e}")

    def close(self):
        if self.connection:
            self.connection.close()



    def find_last_session_by_subject(self, subject_id):
        """Find the last session for a specific subject."""
        self.connect()
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
        finally:
            self.close()

    def select_all_subjects(self):
        """Fetch all subjects from the subjects table."""
        self.connect()
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
        finally:
            self.close()
    def select_subject_by_name(self, subject_name):
        """Fetch a subject by its name."""
        self.connect()
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
        finally:
            self.close()
    def select_all_modes(self):
        """Fetch all modes from the experiment_modes table."""
        self.connect()
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
        finally:
            self.close()

    def insert_session(self, session_data):
        """Insert a new session into the sessions table and return the session_id."""
        self.connect()
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
        finally:
            self.close()

    def find_session_by_id(self, session_id):
        """Find and return a session based on session_id."""
        self.connect()
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
        finally:
            self.close()

    def find_subject_by_id(self, subject_id):
        """Find and return a subject based on subject_id."""
        self.connect()
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
        finally:
            self.close()

    def insert_round_data(self, round_data):
        """Helper function to inject round data into the rounds table."""
        self.connect()
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO rounds (
                session_id, round_index, warning_index, warning_quarter, reinforcers_count, required_clicks
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING round_id
            """
            cursor.execute(query, (
                round_data['session_id'],
                round_data['round_index'],
                round_data['warning_index'],
                round_data['warning_quarter'],
                round_data['reinforcers_count'],
                round_data.get('required_clicks')
            ))
            round_id = cursor.fetchone()[0]
            self.connection.commit()  # Ensure the transaction is committed
            cursor.close()
            print(f"Inserted round data with ID {round_id} and session_id {round_data['session_id']}.")
            return round_id
        except Exception as e:
            print(f"Failed to insert round data: {e}")
            self.log_error_with_round_id(round_data['round_id'], str(e))
            return None
        finally:
            self.close()

    def get_session_basic_info(self, session_id):
        """Fetch session created_at and subject name by session_id."""
        self.connect()
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
        finally:
            self.close()
