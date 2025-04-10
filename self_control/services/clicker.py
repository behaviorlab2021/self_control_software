
import pyhid_usb_relay
import datetime
class Clicker:

    def __init__(self):
        self.relay = pyhid_usb_relay.find()


    def click(self):
        a = datetime.datetime.now()
        self.relay.toggle_state(3)
        b = datetime.datetime.now()
        print("Time Dif", (b-a).microseconds) 