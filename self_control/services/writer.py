from self_control_software.self_control.utils.time_functions import get_time_now, get_timestamp_for_filename, get_time_dif
import csv
import os
import sys
import threading


class Writer:

    def __init__(self, constant_data, subject):

        keys_to_remove = ['created_at', 'updated_at', 'window_height', 'window_width', 'comments']
        for key in keys_to_remove:
            constant_data.pop(key, None)  # Use pop with a default to avoid KeyError if the key doesn't exist
        main_dir_path = os.path.dirname(sys.argv[0])
        self.cd_values = list(constant_data.values())




        self.header =  list(constant_data.keys()) + ['Time', 
                'Reinforcers',
                'Quarter', 
                'hit_count', 
                'Event', 
                'x_pos', 
                'y_pos',
                'warning_present',
                'warning_signal_index'
                ]

        self.start_time = get_time_now()

        self.filename =  get_timestamp_for_filename()+ "_"+ subject + "_Data.csv"
        self.filepath = os.path.join(main_dir_path, "data", self.filename)
        
        print("Filepath: ", self.filepath)
        print("Filename: ", self.filename)

        self.lock = threading.Lock()

        with open(self.filepath, 'w', newline='') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            cwriter.writerow(self.header)
    def writer_update(self, constant_data):
        self.cd_values = list(constant_data.values())


    def write_to_file(self, data):
        with self.lock:
            with open(self.filepath, 'a', newline='') as csvfile:
                cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                cwriter.writerow(self.cd_values + data)

    def write_to_file_threaded(self, data):
        thread = threading.Thread(target=self.write_to_file, args=(data,))
        thread.start()

    def write_peck_data_blind(self, reinforcements, quarter, hit_count, click_x, click_y, event, warning_present, warning_signal_index):
        time = get_time_dif(self.start_time)
        data = [time, reinforcements, quarter, hit_count, event, click_x, click_y, warning_present, warning_signal_index]
        self.write_to_file_threaded(data)

    def write_peck_data(self, reinforcements, quarter, hit_count, click_x, click_y, warning_present, warning_signal_index):
        time = get_time_dif(self.start_time)
        event = "peck"
        data = [time, reinforcements, quarter, hit_count, event, click_x, click_y, warning_present, warning_signal_index]
        self.write_to_file_threaded(data)

    def write_data(self, reinforcements, quarter, hit_count, event, warning_present, warning_signal_index):
        time = get_time_dif(self.start_time)
        data = [time, reinforcements, quarter, hit_count, event, 0, 0, warning_present, warning_signal_index]
        self.write_to_file_threaded(data)




