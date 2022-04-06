import usbrelay_py
import time

count = usbrelay_py.board_count()
print("Count: ",count)

boards = usbrelay_py.board_details()
print("Boards: ",boards)

def activate_relay():

    try:
        usbrelay_py.board_control(boards[0][0], 1, 1)
    except:
        print("No relay found. Cannot activate.")
        pass


def deactivate_relay():
    try:
        usbrelay_py.board_control(boards[0][0], 1, 0)
    except:
        print("No relay found. Cannot deactivate.")
        pass
