import pyhid_usb_relay
import time
import threading
import datetime

def activate_relay_1():
    def task():
        relay = pyhid_usb_relay.find()
        try:
            if not relay.get_state(1):
                relay.toggle_state(1)
        except:
            print("An exception occurred")
    task()
    pass

def deactivate_relay_1():
    def task():
        relay = pyhid_usb_relay.find()
        try:
            if relay.get_state(1):
                relay.toggle_state(1)
        except:
            print("An exception occurred")
    task()
    pass

def activate_relay_2():
    def task():
        relay = pyhid_usb_relay.find()
        print(relay.get_state(1))
        if not relay.get_state(2):
            relay.toggle_state(2)
    task()
    pass

def deactivate_relay_2():
    def task():
        relay = pyhid_usb_relay.find()
        print(relay.get_state(1))
        if relay.get_state(2):
            relay.toggle_state(2)
    task()
    pass

