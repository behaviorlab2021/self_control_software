from time_functions import *
import csv
import os



class Writer:

    def __init__(self, constant_data, subject):
        self.cd_values = list(constant_data.values())
        self.header =  list(constant_data.keys()) + ['Time', 
                'Reinforcers',
                'Quarter', 
                'Pecks', 
                'Event', 
                'x', 
                'y'
                ]

        self.start_time = get_time_now()

        self.filename =  "c:/Users/SKINNER BOX/Documents/self_control_software/" + "data/" + get_timestamp_for_filename()+ "_"+ subject + "_Data.csv"
        with open(self.filename, 'w') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            cwriter.writerow(self.header)

    def write_to_file(self, data):
        with open(self.filename, 'a') as csvfile:
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

    


