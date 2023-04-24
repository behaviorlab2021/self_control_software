import tkinter as tk
from tkinter import messagebox
from kivy.config import Config
import subprocess

def is_number(input):
    if input == "":
        return True  # Allow empty input
    try:
        float(input)  # Try to convert the input to a float
        return True
    except ValueError:
        return False

def start_kivy_app():
    number_argument = number_entry.get()  # Get the input value for the number
    string_argument = string_entry.get()  # Get the input value for the string

    # Check if the number input is empty
    if number_argument.strip() == "":
        messagebox.showerror("Error", "Please enter a number.")
        return

    subprocess.Popen(["python", "c:/Users/SKINNER BOX/Documents/self_control_software/self_control.py", number_argument, string_argument])
    root.destroy()

Config.set('graphics', 'fullscreen', 'auto')

root = tk.Tk()
root.title("Open experiment")
root.iconbitmap("g220.ico")

# Set the default size of the application
root.geometry("300x250")

# Create a label for the number input
number_label = tk.Label(root, text="Enter reinforcing ratio:", font=("Helvetica", 14), justify='center')
number_label.pack()

# Create a validation command
validate_number = (root.register(is_number), '%P')

# Create an Entry widget for the number input with the validation command and centered input text
number_entry = tk.Entry(root, validate="key", validatecommand=validate_number, justify='center')
number_entry.pack()

# Create a label for the string input
string_label = tk.Label(root, text="Enter pigeon name:", font=("Helvetica", 14), justify='center')
string_label.pack()

# Create an Entry widget for the string input with a default value
string_entry = tk.Entry(root,  justify='center')
string_entry.insert(0, "Pigeon")  # Insert the default value
string_entry.pack()

# Add a margin before the button
margin = tk.Label(root, height=2)
margin.pack()

start_button = tk.Button(root, text="Open", command=start_kivy_app, justify='center')
start_button.pack()

root.mainloop()