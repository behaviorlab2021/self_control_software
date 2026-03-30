from self_control_software.self_control.utils.time_functions import get_time_now, get_time_dif
from self_control_software.self_control.services.postgres_sync_service import PostgresSyncService
from self_control_software.self_control.services.async_loop import AsyncLoop
import psycopg2
import threading

class PostgresSyncController:

    def __init__(self):
        self.db = PostgresSyncService()
        self.start_time = get_time_now() 
    

    def inject_round_data(self, session_id, round_index, warning_index, warning_quarter, reinforcers_count, required_clicks=None):
        """Inject new round data into the database."""
        round_data = {
            'session_id': session_id,
            'round_index': round_index,
            'warning_index': warning_index,
            'warning_quarter': warning_quarter,
            'reinforcers_count': reinforcers_count,
            'required_clicks': required_clicks
        }
        try:
            round_id = self.db.insert_round_data(round_data)
            print(f"Inserted new round with ID {round_id}.")
            return round_id
        except Exception as e:
            print(f"Failed to insert round: {e}")
            return None
        
    def find_last_session_by_subject(self, subject_id):
        """Find the last session for a specific subject."""
        try:
            result = self.db.find_last_session_by_subject(subject_id)
            return result
        except Exception as e:
            print(f"Failed to find last session by subject: {e}")
            return None

    def select_all_subjects(self):
        """Fetch all subjects from the subjects table."""
        try:
            results = self.db.select_all_subjects()
            return results
        except Exception as e:
            print(f"Failed to fetch all subjects: {e}")
            return []

    def select_all_modes(self):
        """Fetch all modes from the experiment_modes table."""
        try:
            results = self.db.select_all_modes()
            return results
        except Exception as e:
            print(f"Failed to fetch all modes: {e}")
            return []

    def insert_session(self, session_data):
        """Insert a new session into the sessions table and return the session_id."""
        try:
            session_id = self.db.insert_session(session_data)
            return session_id
        except Exception as e:
            print(f"Failed to insert session: {e}")
            return None

    def find_session_by_id(self, session_id):
        """Find and return a session based on session_id."""
        try:
            result = self.db.find_session_by_id(session_id)
            return result
        except Exception as e:
            print(f"Failed to find session by ID: {e}")
            return None

    def find_subject_by_id(self, subject_id):
        """Find and return a subject based on subject_id."""
        try:
            result = self.db.find_subject_by_id(subject_id)
            return result
        except Exception as e:
            print(f"Failed to find subject by ID: {e}")
            return None

    def get_session_basic_info(self, session_id):
        """Fetch session created_at and subject name by session_id."""
        try:
            result = self.db.get_session_basic_info(session_id)
            return result
        except Exception as e:
            print(f"Failed to fetch session basic info: {e}")
            return None

    def select_subject_by_name(self, subject_name):
        """Fetch a subject by its name."""
        try:
            result = self.db.select_subject_by_name(subject_name)
            return result
        except Exception as e:
            print(f"Failed to fetch subject by name: {e}")
            return None