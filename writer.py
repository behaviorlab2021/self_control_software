from time_functions import *
import csv

header = ['Time', 'Operant', 'Reinforcers', 'Event', 'Hit', 'x', 'y']


class Writer:

    def __init__(self):
        self.start_time = get_time_now()
        self.filename = "data/" + get_timestamp_for_filename() + "_Data.csv"
        with open(self.filename, 'w') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            cwriter.writerow(header)

    def write_data(self, data):
        with open(self.filename, 'a') as csvfile:
            cwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            cwriter.writerow(data)

    def write_click_data(self, operant, reinforcements, click_x, click_y):
        time = get_time_dif(self.start_time)
        event = "click"
        data = [time, operant, reinforcements, event, click_x, click_y]
        self.write_data(data)



