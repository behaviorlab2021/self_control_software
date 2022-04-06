
from usb_relay import activate_relay, deactivate_relay
from kivy.clock import Clock

class Feeder:

    def __init__(self):
        self.counter = 0 
        self.is_active = False

    def activate(self):
        self.is_active = True
        activate_relay()

    def deactivate(self):
        self.is_active = False
        deactivate_relay()
        print("Feeder is reactivated")
        pass

    def create_deactivate_feeder_event(self, feed_time):
        Clock.schedule_once(lambda dt: self.deactivate(), feed_time)
        pass
