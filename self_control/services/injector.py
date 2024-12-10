from self_control_software.self_control.utils.time_functions import get_time_now, get_time_dif
from self_control_software.self_control.services.postgres import ExperimentDB
import psycopg2

class Injector:

    def __init__(self, constant_data):
        self.db = ExperimentDB(dbname='postgres', user='postgres', password='pigeon123!')
        self.experiment_id = constant_data['experiment_id']
        self.start_time = get_time_now()

    def injector_update(self, constant_data):
        self.experiment_id = constant_data['experiment_id']

    def inject_to_db(self, data):
        self.db.connect()
        event_time = get_time_now()  # Change to current time
        event_data = {
            'event_time': event_time,  # Use current time
            'reinforcers': data[0],
            'quarter': data[1],
            'hit_count': data[2],
            'event_type': data[3],
            'x_pos': data[4],
            'y_pos': data[5],
            'warning_present': data[6],
            'warning_signal_index': data[7],
            'experiment_id': data[8]
        }
        self.db.insert_event(event_data)
        self.db.close()


    def inject_peck_data_blind(self, reinforcements, quarter, hit_count, click_x, click_y, event, warning_present, warning_signal_index):
        data = [reinforcements, quarter, hit_count, event, click_x, click_y, warning_present, warning_signal_index, self.experiment_id]
        self.inject_to_db(data)

    def inject_peck_data(self, reinforcements, quarter, hit_count, click_x, click_y, warning_present, warning_signal_index):
        event = "peck"
        data = [reinforcements, quarter, hit_count, event, click_x, click_y, warning_present, warning_signal_index ,self.experiment_id]
        self.inject_to_db(data)

    def inject_data(self, reinforcements, quarter, hit_count, event, warning_present , warning_signal_index):
        time = get_time_dif(self.start_time)
        data = [ reinforcements, quarter, hit_count, event, 0, 0, warning_present, warning_signal_index ,self.experiment_id]
        self.inject_to_db(data)

    def inject_cumulative_record(self, hit_count):
        self.db.connect()
        self.db.insert_cumulative_recorder(hit_count,self.experiment_id)
        print("Cumulative record inserted", hit_count,  self)
        self.db.close()
        pass
