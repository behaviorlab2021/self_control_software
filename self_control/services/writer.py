from self_control_software.self_control.utils.time_functions import get_time_now, get_timestamp_for_filename, get_time_dif
import csv
import os
import sys


class Writer:

    def __init__(self, constant_data, subject):
        main_dir_path = os.path.dirname(sys.argv[0])
        self.cd_values = list(constant_data.values())
        self.header =  list(constant_data.keys()) + ['Time', 
                'Reinforcers',
                'Quarter', 
                'Pecks', 
                'Event', 
                'x_pos', 
                'y_pos',
                'warning_present'
                ]

        self.start_time = get_time_now()

        self.filename =  get_timestamp_for_filename()+ "_"+ subject + "_Data.csv"
        self.filepath =  main_dir_path + "/data/" + self.filename
        with open(self.filepath, 'w', newline='') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            cwriter.writerow(self.header)
    def writer_update(self, constant_data):
        self.cd_values = list(constant_data.values())


    def write_to_file(self, data):
        with open(self.filepath, 'a', newline='') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            cwriter.writerow(self.cd_values + data)

    def write_peck_data_blind(self, reinforcements, quarter, pecks, click_x, click_y, event, warning_present):
        time = get_time_dif(self.start_time)
        data = [time, reinforcements, quarter, pecks, event, click_x, click_y, warning_present]
        self.write_to_file(data)

    def write_peck_data(self, reinforcements, quarter, pecks, click_x, click_y, warning_present):
        time = get_time_dif(self.start_time)
        event = "peck"
        data = [time, reinforcements, quarter, pecks, event, click_x, click_y, warning_present]
        self.write_to_file(data)

    def write_data(self, reinforcements, quarter, pecks, event, warning_present):
        time = get_time_dif(self.start_time)
        data = [time, reinforcements, quarter, pecks, event, 0, 0, warning_present]
        self.write_to_file(data)




