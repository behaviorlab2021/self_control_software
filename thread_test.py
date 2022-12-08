
from time import sleep
from threading import Thread
 
# a custom function that blocks for a moment
def task1():
    # block for a moment
    sleep(1)
    # display a message
    print('This is from task 1')
 
def task2():
    sleep(2)
    print("This is from task 2")


def task3():
    sleep(3)
    print("This is from task 3")

# create a thread
thread1 = Thread(target=task1)
thread2 = Thread(target=task2)
thread3 = Thread(target=task3)

# run the thread
thread1.start()
thread2.start()
thread3.start()
# wait for the thread to finish
thread1.join()
thread2.join()
thread3.join()
print('Waiting for the thread...')