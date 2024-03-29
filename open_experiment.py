import tkinter as tk
from tkinter import messagebox
from kivy.config import Config
import subprocess
from tkinter import ttk

def is_number(input):
    if input == "":
        return True  # Allow empty input
    try:
        float(input)  # Try to convert the input to a float
        return True
    except ValueError:
        return False
def toggle_warning_level(*args):
    if punishment_var.get():
        warning_level_entry.config(state="normal")
    else:
        warning_level_entry.config(state="disabled")

def start_kivy_app():
    number_argument = number_entry.get()  # Get the input value for the number
    trials_argument = trials_entry.get()  # Get the input value for the trials
    dropdown_argument = dropdown_var.get()  # Get the input value for the string
    punishment_argument = punishment_var.get()  # Get the state of the punishment checkbox
    warning_level_argument = warning_level_entry.get()  # Get the input value for the warning level

    # Check if the number input is empty
    if number_argument.strip() == "":
        messagebox.showerror("Error", "Please enter number of reinforcers.")
        return
    if trials_argument.strip() == "":
        messagebox.showerror("Error", "Please enter number of trials.")
        return
    if warning_level_argument.strip() =="" and  warning_level_entry.cget("state") != "disabled":
        messagebox.showerror("Error", "Please enter warning level %.")
        return    
    subprocess.Popen(["python", "c:/Users/SKINNER BOX/Documents/self_control_software/self_control.py", number_argument, trials_argument, dropdown_argument, str(punishment_argument), warning_level_argument ])
    root.destroy()

Config.set('graphics', 'fullscreen', 'auto')

root = tk.Tk()
root.title("Open experiment")
root.iconbitmap("g220.ico")

# Set the default size of the application
root.geometry("300x350")


# REINFORCING RATIO
# Create a label for the number input
number_label = tk.Label(root, text="Enter reinforcing ratio:", font=("Helvetica", 14), justify='center')
number_label.pack()

# Create a validation command
validate_number = (root.register(is_number), '%P')

# Create an Entry widget for the number input with the validation command and centered input text
number_entry = tk.Entry(root, validate="key", validatecommand=validate_number, justify='center')
number_entry.pack()


# NUMBER OF TRIALS
# Create a label for the number input
trials_label = tk.Label(root, text="Enter number of trials:", font=("Helvetica", 14), justify='center')
trials_label.pack()

# Create a validation command
validate_trials = (root.register(is_number), '%P')

# Create an Entry widget for the number input with the validation command and centered input text
trials_entry = tk.Entry(root, validate="key", validatecommand=validate_trials, justify='center')
trials_entry.pack()

# # PIGEON NAME
# # Create a label for the string input
# string_label = tk.Label(root, text="Enter pigeon name:", font=("Helvetica", 14), justify='center')
# string_label.pack()

# # Create an Entry widget for the string input with a default value
# string_entry = tk.Entry(root,  justify='center')
# string_entry.insert(0, "Pigeon")  # Insert the default value
# string_entry.pack()


# DROPDOWN
# # Add a margin before the button
# margin = tk.Label(root, height=1)
# margin.pack()

# Create a label for the dropdown
dropdown_label = tk.Label(root, text="Select pigeon:", font=("Helvetica", 14), justify='center')
dropdown_label.pack()

# Create a dropdown menu
options = ["Adam", "Snik", "Moses", "Ermis"]
dropdown_var = tk.StringVar()
dropdown = ttk.Combobox(root, textvariable=dropdown_var, values=options, state="readonly")
dropdown.pack()

dropdown.set(options[0])

# WARNING CHECKBOX
# Create a label for the punishment checkbox
punishment_label = tk.Label(root, text="Punishment:", font=("Helvetica", 14), justify='center')
punishment_label.pack()

# Create a BooleanVar to hold the state of the checkbox
punishment_var = tk.BooleanVar()
punishment_var.trace("w", toggle_warning_level)
# Create a Checkbutton for the punishment option

punishment_checkbutton = tk.Checkbutton(root, text="Enable", variable=punishment_var)
punishment_checkbutton.pack()

# SIGNAL LEVEL
# Create a label for the warning level input
warning_level_label = tk.Label(root, text="Enter warning level %:", font=("Helvetica", 14), justify='center')
warning_level_label.pack()

# Create a validation command
validate_warning_level = (root.register(is_number), '%P')

# Create an Entry widget for the warning level input with the validation command and centered input text
warning_level_entry = tk.Entry(root, validate="key", validatecommand=validate_warning_level, justify='center', state='disabled')
warning_level_entry.pack()
# Add a margin before the button


margin = tk.Label(root, height=2)
margin.pack()

start_button = tk.Button(root, text="Open", command=start_kivy_app, justify='center')
start_button.pack()

root.mainloop()