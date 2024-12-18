from self_control_software.self_control.utils.time_functions import get_time_now, get_time_dif
from self_control_software.self_control.services.postgres import ExperimentDB
import psycopg2

class Injector:

    def __init__(self, constant_data):
        self.db = ExperimentDB()
        self.session_id = constant_data['session_id']
        self.start_time = get_time_now()

    def injector_update(self, constant_data):
        self.session_id = constant_data['session_id']

    def inject_event(self, round_id, event_type, warning_signal_present):
        self.db.connect()
        self.db.insert_event(round_id, event_type, warning_signal_present)
        self.db.close()


    def inject_cumulative_record(self, hit_count):
        self.db.connect()
        self.db.insert_cumulative_record(hit_count,self.session_id)
        self.db.close()
        pass


    def inject_round_data(self, session_id, round_index, warning_index, warning_quarter, reinforcers_count):
        """Inject new round data into the database."""
        self.db.connect()
        round_data = {
            'session_id': session_id,
            'round_index': round_index,
            'warning_index': warning_index,
            'warning_quarter': warning_quarter,
            'reinforcers_count': reinforcers_count
        }
        try:
            round_id = self.db.insert_round_data(round_data)
            self.db.connection.commit()
            print(f"Inserted new round with ID {round_id}.")
            return round_id
        except Exception as e:
            print(f"Failed to insert round: {e}")
            return None
        finally:
            self.db.close()

    def inject_peck(self, x_pos, y_pos, screen_on, round_id):
        """Inject a new peck into the pecks table."""
        self.db.connect()
        peck_data = {
            'x_pos': x_pos,
            'y_pos': y_pos,
            'screen_on': screen_on,
            'round_id': round_id
        }
        self.db.insert_peck(peck_data)
        self.db.close()

