
from kivy.clock import Clock
import pyhid_usb_relay

class HouseLight:

    def __init__(self):
        self.counter = 0 
        self.is_active = False
        self.relay = pyhid_usb_relay.find()


    def activate(self):
        self.is_active = True
        self.activate_relay_2()

    def deactivate(self):
        self.is_active = False
        self.deactivate_relay_2()
        pass


    def create_deactivate_feeder_event(self, feed_time):
        Clock.schedule_once(lambda dt: self.deactivate(), feed_time)
        pass
    
    def activate_relay_2(self):
        def task(relay):
            print(relay.get_state(1))
            if not relay.get_state(2):
                relay.toggle_state(2)
        task(self.relay)
        pass

    def deactivate_relay_2(self):
        def task(relay):
            print(relay.get_state(1))
            if relay.get_state(2):
                relay.toggle_state(2)
        task(self.relay)
        pass