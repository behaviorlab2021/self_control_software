import psycopg2
from psycopg2.extras import RealDictCursor
import random

class RandomNumberDB:
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
            print("Database connection established.")
        except Exception as e:
            print(f"Failed to connect to database: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def insert_random_number(self):
        """Insert a random number into the table."""
        try:
            cursor = self.connection.cursor()
            random_number = random.uniform(0, 100)  # Generate a random number
            query = "INSERT INTO random_num (random_number) VALUES (%s)"
            cursor.execute(query, (random_number,))
            self.connection.commit()
            cursor.close()
            print(f"Inserted random number: {random_number}")
        except Exception as e:
            print(f"Failed to insert random number: {e}")

    def get_last_entry(self):
        """Fetch the last entry from the table."""
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM random_num ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("Last Entry:", result)
                return result
            else:
                print("The table is empty.")
                return None
        except Exception as e:
            print(f"Failed to fetch the last entry: {e}")
            return None

    def insert_experiment(self, experiment_data):
        """Insert a new experiment into the experiments table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO experiments (
                reinforcement_ratio, warning_signal_points, warning_pecks, punishment_period, 
                feed_time, total_reinforcements, skip_to_next_value, warning_alarm_volume, 
                warning_display_volume, punishment_condition, subject, is_spot_on, 
                random_warning, miliseconds_after_touch, in_warning_signal_training, 
                regular_rounds_before_warning_signal_training, warning_duration, 
                time_before_warning_signal, highlight_warning_signal, warning_signal_position, 
                comments
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                experiment_data['reinforcement_ratio'], experiment_data['warning_signal_points'], 
                experiment_data['warning_pecks'], experiment_data['punishment_period'], 
                experiment_data['feed_time'], experiment_data['total_reinforcements'], 
                experiment_data['skip_to_next_value'], experiment_data['warning_alarm_volume'], 
                experiment_data['warning_display_volume'], experiment_data['punishment_condition'], 
                experiment_data['subject'], experiment_data['is_spot_on'], 
                experiment_data['random_warning'], experiment_data['miliseconds_after_touch'], 
                experiment_data['in_warning_signal_training'], 
                experiment_data['regular_rounds_before_warning_signal_training'], 
                experiment_data['warning_duration'], experiment_data['time_before_warning_signal'], 
                experiment_data['highlight_warning_signal'], experiment_data['warning_signal_position'], 
                experiment_data['comments']
            ))
            self.connection.commit()
            cursor.close()
            print("Inserted new experiment.")
        except Exception as e:
            print(f"Failed to insert experiment: {e}")

    def insert_event(self, event_data):
        """Insert a new event into the events table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO events (
                event_time, reinforcers, quarter, pecks, event_type, x_pos, y_pos, warning_present
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                event_data['event_time'], event_data['reinforcers'], event_data['quarter'], 
                event_data['pecks'], event_data['event_type'], event_data['x_pos'], 
                event_data['y_pos'], event_data['warning_present']
            ))
            self.connection.commit()
            cursor.close()
            print("Inserted new event.")
        except Exception as e:
            print(f"Failed to insert event: {e}")

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

# Example usage
db = RandomNumberDB(dbname='postgres', user='postgres', password='pigeon123!')
db.connect()

# Insert a random number
db.insert_random_number()

# Fetch the last entry
last_entry = db.get_last_entry()
print("Fetched Last Entry:", last_entry)

# Insert a new experiment
experiment_data = {
    'reinforcement_ratio': 10,
    'warning_signal_points': 5,
    'warning_pecks': 3,
    'punishment_period': 60,
    'feed_time': 30,
    'total_reinforcements': 100,
    'skip_to_next_value': 0,
    'warning_alarm_volume': 0.5,
    'warning_display_volume': 0.5,
    'punishment_condition': 1,
    'subject': 'Subject A',
    'is_spot_on': False,
    'random_warning': False,
    'miliseconds_after_touch': 500,
    'in_warning_signal_training': False,
    'regular_rounds_before_warning_signal_training': 10,
    'warning_duration': 5,
    'time_before_warning_signal': 10,
    'highlight_warning_signal': False,
    'warning_signal_position': 1.23456,
    'comments': 'Test experiment'
}
db.insert_experiment(experiment_data)

# Insert a new event
event_data = {
    'event_time': '2023-10-01 12:00:00',
    'reinforcers': 2,
    'quarter': 1,
    'pecks': 10,
    'event_type': 'stimulus',
    'x_pos': 1.23456,
    'y_pos': 2.34567,
    'warning_present': False
}
db.insert_event(event_data)

# Fetch the last event
last_event = db.select_last_event()
print("Fetched Last Event:", last_event)

db.close()