
from kivy.clock import Clock
import pyhid_usb_relay

class Feeder:

    def __init__(self):
        self.counter = 0 
        self.is_active = False
        self.relay = pyhid_usb_relay.find()


    def activate(self):
        self.is_active = True
        self.activate_relay_1()

    def deactivate(self):
        self.is_active = False
        self.deactivate_relay_1()
        pass

    def switch(self):
        if self.is_active:
            self.is_active=False
            self.deactivate_relay_1()
            return 0
        else:
            self.is_active=True
            self.deactivate_relay_1()
            return 1

    def create_deactivate_feeder_event(self, feed_time):
        Clock.schedule_once(lambda dt: self.deactivate(), feed_time)
        pass


    def activate_relay_1(self):
        def task(relay):
            try:
                if not relay.get_state(1):
                    relay.toggle_state(1)
            except:
                print("An exception occurred")
        task(self.relay)
        pass

    def deactivate_relay_1(self):
        def task(relay):
            try:
                if relay.get_state(1):
                    relay.toggle_state(1)
            except:
                print("An exception occurred")
        task(self.relay)
        pass
