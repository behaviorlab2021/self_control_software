import usbrelay_py
import time

count = usbrelay_py.board_count()
print("Count: ",count)

boards = usbrelay_py.board_details()
print("Boards: ",boards)

def activate_relay_1():

    try:
        usbrelay_py.board_control(boards[0][0], 1, 1)
    except:
        print("No relay found. Cannot activate.")
        pass


def deactivate_relay_1():
    try:
        usbrelay_py.board_control(boards[0][0], 1, 0)
    except:
        print("No relay found. Cannot deactivate.")
        pass


def activate_relay_2():

    try:
        usbrelay_py.board_control(boards[0][0], 2, 1)
    except:
        print("No relay found. Cannot activate.")
        pass


def deactivate_relay_2():
    try:
        usbrelay_py.board_control(boards[0][0], 2, 0)
    except:
        print("No relay found. Cannot deactivate.")
        pass
