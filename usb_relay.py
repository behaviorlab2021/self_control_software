import pyhid_usb_relay
import time


def activate_relay_1():
    relay = pyhid_usb_relay.find()
    try:
        if not relay.get_state(1):
            relay.toggle_state(1)
    except:
        print("An exception occurred")



def deactivate_relay_1():
    relay = pyhid_usb_relay.find()
    try:
        if relay.get_state(1):
            relay.toggle_state(1)
    except:
        print("An exception occurred")




def activate_relay_2():
    relay = pyhid_usb_relay.find()
    print(relay.get_state(1))
    if not relay.get_state(2):
        relay.toggle_state(2)



def deactivate_relay_2():
    relay = pyhid_usb_relay.find()
    print(relay.get_state(1))
    if relay.get_state(2):
        relay.toggle_state(2)

def toggle_relay_3():
    relay = pyhid_usb_relay.find()
    relay.toggle_state(3)


# while True:
#     activate_relay_1()
#     time.sleep(5)
#     deactivate_relay_1()
#     time.sleep(20)
