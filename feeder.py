
from usb_relay import activate_relay_1, deactivate_relay_1
from kivy.clock import Clock

class Feeder:

    def __init__(self):
        self.counter = 0 
        self.is_active = False

    def activate(self):
        self.is_active = True
        activate_relay_1()

    def deactivate(self):
        self.is_active = False
        deactivate_relay_1()
        print("Feeder is reactivated")
        pass

    def create_deactivate_feeder_event(self, feed_time):
        Clock.schedule_once(lambda dt: self.deactivate(), feed_time)
        pass
