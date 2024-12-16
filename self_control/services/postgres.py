import psycopg2
from psycopg2.extras import RealDictCursor
import uuid


class ExperimentDB:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.db_config = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.connection = None

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

    def find_last_experiment_by_subject(self, subject_id):
        """Find the last experiment for a specific subject."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = """
            SELECT * FROM experiments
            WHERE subject_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """
            cursor.execute(query, (subject_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Found last experiment for subject.")
                return result
            else:
                print("No experiments found for subject.")
                return None
        except Exception as e:
            print(f"Failed to find last experiment for subject: {e}")
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

    def insert_experiment(self, experiment_data):
        """Insert a new experiment into the experiments table and return the experiment_id."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO experiments (
                experiment_id,
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
                comments
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING experiment_id
            """
            cursor.execute(query, (
                experiment_data['experiment_id'],
                experiment_data['reinforcement_ratio'], 
                experiment_data['warning_hits'], 
                experiment_data['punishment_duration'], 
                experiment_data['feed_time'], 
                experiment_data['total_reinforcements'], 
                experiment_data['consecutive_warnings_limit'], 
                experiment_data['warning_alarm_volume'], 
                experiment_data['warning_display_volume'], 
                experiment_data['subject_id'], 
                experiment_data['mode_id'], 
                experiment_data['is_spot_on'], 
                experiment_data['punishment_periodicity'], 
                experiment_data['warning_duration'], 
                experiment_data['time_before_warning_signal'], 
                experiment_data['highlight_warning_signal'], 
                experiment_data['warning_signal_position'], 
                experiment_data['comments']
            ))
            self.connection.commit()
            cursor.close()
            print(f"Inserted new experiment with ID {experiment_data['experiment_id']}.")
            return experiment_data['experiment_id']
        except Exception as e:
            print(f"Failed to insert experiment: {e}")
            return None

    def insert_experiment_with_uuid(self, experiment_data):
        """Insert a new experiment into the experiments table with a UUID."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO experiments (
                experiment_id,
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
                comments
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            experiment_id = experiment_data.get('experiment_id', str(uuid.uuid4()))
            cursor.execute(query, (
                experiment_id,
                experiment_data['reinforcement_ratio'], 
                experiment_data['warning_hits'], 
                experiment_data['punishment_duration'], 
                experiment_data['feed_time'], 
                experiment_data['total_reinforcements'], 
                experiment_data['consecutive_warnings_limit'], 
                experiment_data['warning_alarm_volume'], 
                experiment_data['warning_display_volume'], 
                experiment_data['subject_id'], 
                experiment_data['mode_id'], 
                experiment_data['is_spot_on'], 
                experiment_data['punishment_periodicity'], 
                experiment_data['warning_duration'], 
                experiment_data['time_before_warning_signal'], 
                experiment_data['highlight_warning_signal'], 
                experiment_data['warning_signal_position'], 
                experiment_data['comments']
            ))
            self.connection.commit()
            cursor.close()
            print(f"Inserted new experiment with UUID {experiment_id}.")
        except Exception as e:
            print(f"Failed to insert experiment: {e}")

    def insert_event(self, event_data):
        """Insert a new event into the events table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO events (
                event_time, reinforcers, quarter, hit_count, event_type, x_pos, y_pos, warning_present, warning_signal_index, experiment_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                event_data['event_time'], event_data['reinforcers'], event_data['quarter'], 
                event_data['hit_count'], event_data['event_type'], event_data['x_pos'], 
                event_data['y_pos'], event_data['warning_present'], event_data['warning_signal_index'], event_data['experiment_id']
            ))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Failed to insert event: {e}")
    def insert_cumulative_recorder(self, hit_count, experiment_id):
        """Insert a new row into the cumulative_recorder table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO cumulative_recorder (hit_count, experiment_id)
            VALUES (%s, %s)
            """
            cursor.execute(query, (hit_count, experiment_id))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Failed to insert into cumulative_recorder: {e}")


    def select_last_event(self):
        """Fetch the last event from the events table."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM events ORDER BY event_id DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Last Event:", result)
                return result
            else:
                print("The events table is empty.")
                return None
        except Exception as e:
            print(f"Failed to fetch the last event: {e}")
            return None

    def select_experiment_by_id(self, experiment_id):
        """Fetch an experiment by its ID."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM experiments WHERE experiment_id = %s"
            cursor.execute(query, (experiment_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Experiment:", result)
                return result
            else:
                print(f"No experiment found with ID {experiment_id}.")
                return None
        except Exception as e:
            print(f"Failed to fetch experiment: {e}")
            return None

    def edit_experiment_subject(self, experiment_id, new_subject):
        """Edit the subject of an experiment by its ID."""
        try:
            cursor = self.connection.cursor()
            query = "UPDATE experiments SET subject = %s, updated_at = NOW() WHERE experiment_id = %s"
            cursor.execute(query, (new_subject, experiment_id))
            self.connection.commit()
            cursor.close()
            print(f"Updated experiment ID {experiment_id} with new subject: {new_subject}")
        except Exception as e:
            print(f"Failed to update experiment subject: {e}")

    def find_experiment_by_id(self, experiment_id):
        """Find and return an experiment based on experiment_id."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM experiments WHERE experiment_id = %s"
            cursor.execute(query, (experiment_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Experiment found:", result)
                return result
            else:
                print(f"No experiment found with ID {experiment_id}.")
                return None
        except Exception as e:
            print(f"Failed to find experiment: {e}")
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
            return None


        

# # Example usage
# db = RandomNumberDB(dbname='postgres', user='postgres', password='pigeon123!')
# db.connect()

# # Insert a new experiment
# experiment_data = {
#     'reinforcement_ratio': 10,
#     'warning_hits': 3,
#     'punishment_duration': 60,
#     'feed_time': 30,
#     'total_reinforcements': 100,
#     'consecutive_warnings_limit': 0,
#     'warning_alarm_volume': 0.5,
#     'warning_display_volume': 0.5,
#     'punishment_condition': 1,
#     'subject': 'Subject A',
#     'is_spot_on': False,
#     'random_warning': False,
#     'miliseconds_after_touch': 500,
#     'in_warning_signal_training': False,
#     'punishment_periodicity': 10,
#     'warning_duration': 5,
#     'time_before_warning_signal': 10,
#     'highlight_warning_signal': False,
#     'warning_signal_position': 1.23456,
#     'comments': 'Test experiment'
# }
# db.insert_experiment(1, experiment_data)

# # Insert a new event
# event_data = {
#     'event_time': '2023-10-01 12:00:00',
#     'reinforcers': 2,
#     'quarter': 1,
#     'hit_count': 10,
#     'event_type': 'stimulus',
#     'x_pos': 1.23456,
#     'y_pos': 2.34567,
#     'warning_present': False
# }
# db.insert_event(event_data)

# # Fetch the last event
# last_event = db.select_last_event()
# print("Fetched Last Event:", last_event)

# # Fetch an experiment by ID
# experiment_id = 1
# experiment = db.select_experiment_by_id(experiment_id)
# print("Fetched Experiment by ID:", experiment)

# # Edit the subject of an experiment
# db.edit_experiment_subject(experiment_id, "New Subject")

# db.close()