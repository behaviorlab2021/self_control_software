import pyhid_usb_relay
import time
import threading

def activate_relay_1():
    def task():
        relay = pyhid_usb_relay.find()
        try:
            if not relay.get_state(1):
                relay.toggle_state(1)
        except:
            print("An exception occurred")
    threading.Thread(target=task).start()
    pass

def deactivate_relay_1():
    def task():
        relay = pyhid_usb_relay.find()
        try:
            if relay.get_state(1):
                relay.toggle_state(1)
        except:
            print("An exception occurred")
    threading.Thread(target=task).start()
    pass

def activate_relay_2():
    def task():
        relay = pyhid_usb_relay.find()
        print(relay.get_state(1))
        if not relay.get_state(2):
            relay.toggle_state(2)
    threading.Thread(target=task).start()
    pass

def deactivate_relay_2():
    def task():
        relay = pyhid_usb_relay.find()
        print(relay.get_state(1))
        if relay.get_state(2):
            relay.toggle_state(2)
    threading.Thread(target=task).start()
    pass

def toggle_relay_3():
    def task():
        relay = pyhid_usb_relay.find()
        relay.toggle_state(3)
    threading.Thread(target=task).start()
    pass

# while True:
#     activate_relay_1()
#     time.sleep(5)
#     deactivate_relay_1()
#     time.sleep(20)
