from time_functions import *
import csv

header = ['Time', 'Operant', 'Reinforcers', 'Event', 'x', 'y']


class Writer:

    def __init__(self):
        self.start_time = get_time_now()
        self.filename = "data/" + get_timestamp_for_filename() + "_Data.csv"
        with open(self.filename, 'w') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            cwriter.writerow(header)

    def write_to_file(self, data):
        with open(self.filename, 'a') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            cwriter.writerow(data)

    def write_peck_data(self, reinforcements, quarter, pecks, click_x, click_y):
        time = get_time_dif(self.start_time)
        event = "peck"
        data = [time, reinforcements, quarter, pecks, event, click_x, click_y]
        self.write_to_file(data)

    def write_data(self, reinforcements, quarter, pecks, event):
        time = get_time_dif(self.start_time)
        data = [time, reinforcements, quarter, pecks, event, 0, 0]
        self.write_to_file(data)


