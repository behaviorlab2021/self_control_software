import sys
import os
import threading

# Add the parent directory of self_control_software to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
print("Project Root: ", project_root)
sys.path.append(project_root)

import tkinter as tk
from tkinter import ttk, messagebox
from self_control_software.self_control.controllers.postgres_sync_controller import PostgresSyncController
import uuid
import subprocess
import json


class MultiStepApp:
    def __init__(self, root):
        self.root = root  # Add this line
        self.root.title("Multi-Step Setup Wizard")
        self.root.geometry("720x520")
        img_path = os.path.join(project_root, 'self_control_software','self_control', 'assets', 'icons', 'settings.png')
        img = tk.PhotoImage(file=img_path)
        root.iconphoto(False, img)    
        self.pg_controller = PostgresSyncController()
        self.current_step = 1
        self.session_id = str(uuid.uuid4())
        self.subject_name = tk.StringVar()
        self.total_reinforcements = tk.StringVar(value="35")
        self.punishment_duration = tk.StringVar(value="30")
        self.feed_time = tk.StringVar(value="4")
        self.is_spot_on = tk.BooleanVar(value=False)
        self.reinforcement_ratio = tk.StringVar(value="60")
        self.subjects = self.pg_controller.select_all_subjects()
        self.mode_id = tk.StringVar()
        self.modes = self.pg_controller.select_all_modes()
        self.consecutive_warnings_limit = tk.StringVar(value="3")
        self.warning_alarm_volume = tk.StringVar(value="100")
        self.warning_display_volume = tk.StringVar(value="100")
        self.warning_hits = tk.StringVar(value="3")
        self.punishment_periodicity = tk.StringVar(value="1")
        self.warning_duration = tk.StringVar(value="5")
        self.time_before_warning_signal = tk.StringVar(value="5")
        self.highlight_warning_signal = tk.BooleanVar(value=False)
        self.warning_signal_position = tk.StringVar(value="0")
        self.button_height = tk.StringVar(value="50")
        self.button_size = tk.StringVar(value="15")
        self.grace_radius = tk.StringVar(value="1")
        self.peck_slide = tk.StringVar(value="5")
        self.comments = tk.StringVar()
        self.inputs_frame = None  # Initialize inputs_frame to None

        self.style = ttk.Style()
        self.style.map('TCombobox', 
                       selectbackground=[('readonly', 'white')],
                       selectforeground=[('readonly', 'black')],
                       fieldbackground=[('readonly', 'white')],
                       background=[('readonly', 'white')])

        self.create_widgets()
        self.mode_id.trace_add("write", self.update_step)

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.step_frame = tk.Frame(self.main_frame)
        self.step_frame.pack(fill="both", expand=True)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(fill="x", side="bottom")

        self.back_button = tk.Button(self.button_frame, text="Back", command=self.previous_step)
        self.back_button.pack(side="left", padx=5, pady=5)

        self.next_button = tk.Button(self.button_frame, text="Next", command=self.next_step)
        self.next_button.pack(side="right", padx=5, pady=5)

        self.root.register(self.validate_between_0_and_100)
        self.root.register(self.validate_greater_than_1)
        self.root.register(self.validate_between_1_and_10)
        self.root.register(self.validate_between_1_and_600)

        self.update_step()

    def show_step_1(self):
        self.clear_frame()

        tk.Label(self.step_frame, text="Step 1: Select Subject Name", font=("Tahoma", 14)).pack(pady=5)

        input_frame = tk.Frame(self.step_frame)
        input_frame.pack(expand=True)

        # Remove the label for subject name
        # tk.Label(input_frame, text="Subject Name:", font=("Tahoma", 12)).grid(row=0, column=0, pady=5, sticky="e")

        # Replace dropdown with radio buttons
        for idx, subject in enumerate(self.subjects):
            tk.Radiobutton(input_frame, text=subject['subject_name'], variable=self.subject_name, value=subject['subject_name'], font=("Tahoma", 12)).grid(row=idx, column=0, pady=2, sticky="w")

        # Trace changes to the subject_name variable
        self.subject_name.trace_add("write", self.update_next_button_state)

        # Configure columns to expand and center-align the grid
        input_frame.grid_columnconfigure(0, weight=1)

        self.back_button.config(state="disabled")
        self.update_next_button_state()

    def update_next_button_state(self, *args):
        if self.subject_name.get().strip():
            self.next_button.config(state="normal")
        else:
            self.next_button.config(state="disabled")

    def show_step_2(self):
        self.clear_frame()

        tk.Label(self.step_frame, text="Step 2: Enter Session Details", font=("Tahoma", 14)).pack(pady=5)

        input_frame = tk.Frame(self.step_frame)
        input_frame.pack(expand=True)

        tk.Label(input_frame, text="Subject Name:", font=("Tahoma", 12)).grid(row=0, column=0, pady=2, sticky="e")        
        tk.Label(input_frame, text=f"{self.subject_name.get()}", font=("Tahoma", 12)).grid(row=0, column=1, pady=2, sticky="w")

        # Mode Selection
        tk.Label(input_frame, text="Select Mode:", font=("Tahoma", 12)).grid(row=1, column=0, pady=2, sticky="e")
        mode_names = [mode['mode_name'] for mode in self.modes]
        self.mode_dropdown = ttk.Combobox(input_frame, textvariable=self.mode_id, values=mode_names, state="readonly", width=20, style='TCombobox')
        self.mode_dropdown.grid(row=1, column=1, pady=2, sticky="w", columnspan=5)

        self.mode_id.trace_add("write", self.update_next_button_state_step_2)

        self.inputs_frame = tk.Frame(self.step_frame)  # Initialize inputs_frame
        self.inputs_frame.pack(expand=True)

        if not self.mode_id.get():
            self.update_next_button_state_step_2()
            self.inputs_frame.pack_forget()
        else:
            self.show_inputs()

        self.back_button.config(state="normal", command=self.previous_step)
        self.update_next_button_state_step_2()

    def show_inputs(self):
        input_frame = self.inputs_frame

        # Reinforcement Ratio
        if not self.is_basic_training_mode():
            ratio_label = "Variability Ratio:" if self.mode_id.get() in ("VARIABLE RATIO", "VARIABLE WARNING") else "Reinforcement Ratio:"
            tk.Label(input_frame, text=ratio_label, font=("Tahoma", 12)).grid(row=2, column=0, pady=2, sticky="e")
            self.reinforcement_ratio_entry = tk.Entry(input_frame, textvariable=self.reinforcement_ratio, validate="key", validatecommand=(self.root.register(self.validate_greater_than_1), '%P'), width=5)
            self.reinforcement_ratio_entry.grid(row=2, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.reinforcement_ratio, 1)).grid(row=2, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.reinforcement_ratio, 1)).grid(row=2, column=3, padx=2)
            tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.reinforcement_ratio, 10)).grid(row=2, column=4, padx=2)
            tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.reinforcement_ratio, 10)).grid(row=2, column=5, padx=2)

        # Total Reinforcements
        tk.Label(input_frame, text="Total Reinforcements:", font=("Tahoma", 12)).grid(row=3, column=0, pady=2, sticky="e")
        self.total_reinforcements_entry = tk.Entry(input_frame, textvariable=self.total_reinforcements, validate="key", validatecommand=(self.root.register(self.validate_greater_than_1), '%P'), width=5)
        self.total_reinforcements_entry.grid(row=3, column=1, pady=2, sticky="w")
        tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.total_reinforcements, 1)).grid(row=3, column=2, padx=2)
        tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.total_reinforcements, 1)).grid(row=3, column=3, padx=2)
        tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.total_reinforcements, 10)).grid(row=3, column=4, padx=2)
        tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.total_reinforcements, 10)).grid(row=3, column=5, padx=2)

        # Warning Alarm Volume
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode():
            tk.Label(input_frame, text="Warning Alarm Volume:", font=("Tahoma", 12)).grid(row=4, column=0, pady=2, sticky="e")
            self.warning_alarm_volume_entry = tk.Entry(input_frame, textvariable=self.warning_alarm_volume, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.warning_alarm_volume_entry.grid(row=4, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.warning_alarm_volume, 1)).grid(row=4, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.warning_alarm_volume, 1)).grid(row=4, column=3, padx=2)
            tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.warning_alarm_volume, 10)).grid(row=4, column=4, padx=2)
            tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.warning_alarm_volume, 10)).grid(row=4, column=5, padx=2)
            self.warning_alarm_volume_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.warning_alarm_volume, 0, 100))

        # Warning Display Volume
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode():
            tk.Label(input_frame, text="Warning Display Volume:", font=("Tahoma", 12)).grid(row=5, column=0, pady=2, sticky="e")
            self.warning_display_volume_entry = tk.Entry(input_frame, textvariable=self.warning_display_volume, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.warning_display_volume_entry.grid(row=5, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.warning_display_volume, 1)).grid(row=5, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.warning_display_volume, 1)).grid(row=5, column=3, padx=2)
            tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.warning_display_volume, 10)).grid(row=5, column=4, padx=2)
            tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.warning_display_volume, 10)).grid(row=5, column=5, padx=2)
            self.warning_display_volume_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.warning_display_volume, 0, 100))

        # More Options Button
        self.more_options_button = tk.Button(input_frame, text="More Options", command=self.show_more_options)
        self.more_options_button.grid(row=6, column=0, columnspan=6, pady=10)

        # Add Comment Label and Text Box
        tk.Label(input_frame, text="Comments:", font=("Tahoma", 12), anchor="center").grid(row=7, column=0, pady=2, sticky="ew", columnspan=6)
        self.comments_entry = tk.Entry(input_frame, textvariable=self.comments, width=50, justify="center")
        self.comments_entry.grid(row=8, column=0, pady=2, sticky="we", columnspan=6)

        # UUID Entry (copyable)
        self.uuid_entry = tk.Entry(input_frame, textvariable=tk.StringVar(value=self.session_id), state="readonly", width=36, justify="center")
        self.uuid_entry.grid(row=9, column=0, pady=2, sticky="we", columnspan=6)

        # Center the UUID entry and comments entry horizontally
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(2, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)
        input_frame.grid_columnconfigure(4, weight=1)
        input_frame.grid_columnconfigure(5, weight=1)

        # Configure columns to expand and center-align the grid
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(2, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)
        input_frame.grid_columnconfigure(4, weight=1)
        input_frame.grid_columnconfigure(5, weight=1)

    def update_next_button_state_step_2(self, *args):
        if self.mode_id.get().strip():
            self.next_button.config(state="normal")
            if self.inputs_frame is None or not self.inputs_frame.winfo_exists():
                self.inputs_frame = tk.Frame(self.step_frame)
            self.inputs_frame.pack(expand=True)
            self.show_inputs()
        else:
            self.next_button.config(state="disabled")
            if self.inputs_frame is not None and self.inputs_frame.winfo_exists():
                self.inputs_frame.pack_forget()

    def is_basic_training_mode(self):
        return self.mode_id.get() == "HOPPER TRAINING"

    def is_schedule_training_mode(self):
        return self.mode_id.get() in ("SCHEDULE TRAINING", "VARIABLE RATIO")

    def is_random_warning_mode(self):
        return self.mode_id.get() in ("RANDOM WARNING", "VARIABLE WARNING")

    def is_warning_training_mode(self):
        return self.mode_id.get() == "WARNING TRAINING"

    def increment_value(self, variable, increment):
        try:
            current_value = int(variable.get())
            new_value = current_value + increment
            if variable == self.reinforcement_ratio and new_value >= 1:
                variable.set(new_value)
            elif variable == self.warning_hits and 1 <= new_value <= 10:
                variable.set(new_value)
            elif variable == self.total_reinforcements and new_value >= 1:
                variable.set(new_value)
            elif variable == self.warning_alarm_volume and new_value <= 100:
                variable.set(new_value)
            elif variable == self.warning_display_volume and new_value <= 100:
                variable.set(new_value)
            elif variable == self.punishment_duration and new_value <= 100:
                variable.set(new_value)
            elif variable == self.feed_time and 1 <= new_value <= 600:
                variable.set(new_value)
            elif variable == self.consecutive_warnings_limit and 1 <= new_value <= 10:
                variable.set(new_value)
            elif variable == self.punishment_periodicity and 1 <= new_value <= 10:
                variable.set(new_value)
            elif variable == self.warning_duration and new_value >= 1:
                variable.set(new_value)
            elif variable == self.time_before_warning_signal and 0 <= new_value <= 100:
                variable.set(new_value)
            elif variable == self.warning_signal_position and new_value <= 100:
                variable.set(new_value)
            elif variable == self.button_height and new_value <= 100:
                variable.set(new_value)
            elif variable == self.button_size and new_value <= 100:
                variable.set(new_value)
            elif variable == self.grace_radius and new_value <= 100:
                variable.set(new_value)
            elif variable == self.peck_slide and new_value <= 100:
                variable.set(new_value)
        except ValueError:
            variable.set(increment)

    def decrement_value(self, variable, decrement):
        try:
            current_value = int(variable.get())
            if variable == self.reinforcement_ratio:
                if current_value > 1:
                    variable.set(max(1, current_value - decrement))
            elif variable == self.warning_hits:
                if current_value > 1:
                    variable.set(max(1, current_value - decrement))
            elif variable == self.total_reinforcements:
                if current_value > 1:
                    variable.set(max(1, current_value - decrement))
            elif variable == self.warning_alarm_volume:
                if current_value > 0:
                    variable.set(max(0, current_value - decrement))
            elif variable == self.warning_display_volume:
                if current_value > 0:
                    variable.set(max(0, current_value - decrement))
            elif variable == self.punishment_duration:
                if current_value > 0:
                    variable.set(max(0, current_value - decrement))
            elif variable == self.feed_time:
                if current_value > 1:
                    variable.set(max(1, current_value - decrement))
            elif variable == self.consecutive_warnings_limit:
                if current_value > 1:
                    variable.set(max(1, current_value - decrement))
            elif variable == self.punishment_periodicity:
                if current_value > 1:
                    variable.set(max(1, current_value - decrement))
            elif variable == self.warning_duration:
                if current_value > 1:
                    variable.set(max(1, current_value - decrement))
            elif variable == self.time_before_warning_signal:
                if current_value > 0:
                    variable.set(max(1, current_value - decrement))
            elif variable == self.warning_signal_position:
                if current_value > 0:
                    variable.set(max(0, current_value - decrement))
            elif variable == self.button_height:
                if current_value > 0:
                    variable.set(max(0, current_value - decrement))
            elif variable == self.button_size:
                if current_value > 0:
                    variable.set(max(0, current_value - decrement))
            elif variable == self.grace_radius:
                if current_value > 0:
                    variable.set(max(0, current_value - decrement))
            elif variable == self.peck_slide:
                if current_value > 0:
                    variable.set(max(0, current_value - decrement))
        except ValueError:
            variable.set(0)

    def show_more_options(self):
        self.clear_frame()

        tk.Label(self.step_frame, text="Step 2: Additional Options", font=("Tahoma", 14)).pack(pady=5)

        input_frame = tk.Frame(self.step_frame)
        input_frame.pack(expand=True)

        tk.Label(input_frame, text="Subject Name:", font=("Tahoma", 12)).grid(row=0, column=0, pady=2, sticky="e")        
        tk.Label(input_frame, text=f"{self.subject_name.get()}", font=("Tahoma", 12)).grid(row=0, column=1, pady=2, sticky="w")

        # Punishment Duration
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode():
            tk.Label(input_frame, text="Punishment Duration (seconds):", font=("Tahoma", 12)).grid(row=1, column=0, pady=2, sticky="e")
            self.punishment_duration_entry = tk.Entry(input_frame, textvariable=self.punishment_duration, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.punishment_duration_entry.grid(row=1, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.punishment_duration, 1)).grid(row=1, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.punishment_duration, 1)).grid(row=1, column=3, padx=2)
            tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.punishment_duration, 10)).grid(row=1, column=4, padx=2)
            tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.punishment_duration, 10)).grid(row=1, column=5, padx=2)
            self.punishment_duration_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.punishment_duration, 0, 100))

        # Feed Time
        tk.Label(input_frame, text="Feed Time (seconds):", font=("Tahoma", 12)).grid(row=2, column=0, pady=2, sticky="e")
        self.feed_time_entry = tk.Entry(input_frame, textvariable=self.feed_time, validate="key", validatecommand=(self.root.register(self.validate_between_1_and_600), '%P'), width=5)
        self.feed_time_entry.grid(row=2, column=1, pady=2, sticky="w")
        tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.feed_time, 1)).grid(row=2, column=2, padx=2)
        tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.feed_time, 1)).grid(row=2, column=3, padx=2)
        tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.feed_time, 10)).grid(row=2, column=4, padx=2)
        tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.feed_time, 10)).grid(row=2, column=5, padx=2)    
        self.feed_time_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.feed_time, 1, 10))

        # Consecutive Warnings Limit
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode():
            tk.Label(input_frame, text="Consecutive Warnings Limit:", font=("Tahoma", 12)).grid(row=3, column=0, pady=2, sticky="e")
            self.consecutive_warnings_limit_entry = tk.Entry(input_frame, textvariable=self.consecutive_warnings_limit, validate="key", validatecommand=(self.root.register(self.validate_between_1_and_10), '%P'), width=5)
            self.consecutive_warnings_limit_entry.grid(row=3, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.consecutive_warnings_limit, 1)).grid(row=3, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.consecutive_warnings_limit, 1)).grid(row=3, column=3, padx=2)
            self.consecutive_warnings_limit_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.consecutive_warnings_limit, 1, 10))

        # Warning Hits
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode() and not self.is_warning_training_mode():
            tk.Label(input_frame, text="Warning Hits:", font=("Tahoma", 12)).grid(row=4, column=0, pady=2, sticky="e")
            self.warning_hits_entry = tk.Entry(input_frame, textvariable=self.warning_hits, validate="key", validatecommand=(self.root.register(self.validate_between_1_and_10), '%P'), width=5)
            self.warning_hits_entry.grid(row=4, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.warning_hits, 1)).grid(row=4, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.warning_hits, 1)).grid(row=4, column=3, padx=2)
            self.warning_hits_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.warning_hits, 1, 10))

        # Regular Punishment Periodicity
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode() and not self.is_random_warning_mode():
            tk.Label(input_frame, text="Punishment Periodicity:", font=("Tahoma", 12)).grid(row=5, column=0, pady=2, sticky="e")
            self.punishment_periodicity_entry = tk.Entry(input_frame, textvariable=self.punishment_periodicity, validate="key", validatecommand=(self.root.register(self.validate_between_1_and_10), '%P'), width=5)
            self.punishment_periodicity_entry.grid(row=5, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.punishment_periodicity, 1)).grid(row=5, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.punishment_periodicity, 1)).grid(row=5, column=3, padx=2)
            self.punishment_periodicity_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.punishment_periodicity, 1, 10))

        # Warning Duration
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode() and not self.is_random_warning_mode():
            tk.Label(input_frame, text="Warning Duration (seconds):", font=("Tahoma", 12)).grid(row=6, column=0, pady=2, sticky="e")
            self.warning_duration_entry = tk.Entry(input_frame, textvariable=self.warning_duration, validate="key", validatecommand=(self.root.register(self.validate_greater_than_1), '%P'), width=5)
            self.warning_duration_entry.grid(row=6, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.warning_duration, 1)).grid(row=6, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.warning_duration, 1)).grid(row=6, column=3, padx=2)
            tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.warning_duration, 10)).grid(row=6, column=4, padx=2)
            tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.warning_duration, 10)).grid(row=6, column=5, padx=2)
            self.warning_duration_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.warning_duration, 1, 100))

        # Time Before Warning Signal
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode() and not self.is_random_warning_mode():
            tk.Label(input_frame, text="Time Before Warning Signal (seconds):", font=("Tahoma", 12)).grid(row=7, column=0, pady=2, sticky="e")
            self.time_before_warning_signal_entry = tk.Entry(input_frame, textvariable=self.time_before_warning_signal, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.time_before_warning_signal_entry.grid(row=7, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.time_before_warning_signal, 1)).grid(row=7, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.time_before_warning_signal, 1)).grid(row=7, column=3, padx=2)
            self.time_before_warning_signal_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.time_before_warning_signal, 1, 10))

        # Warning Signal Index
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode():
            tk.Label(input_frame, text="Warning Signal Position:", font=("Tahoma", 12)).grid(row=8, column=0, pady=2, sticky="e")
            self.warning_signal_position_entry = tk.Entry(input_frame, textvariable=self.warning_signal_position, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.warning_signal_position_entry.grid(row=8, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.warning_signal_position, 1)).grid(row=8, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.warning_signal_position, 1)).grid(row=8, column=3, padx=2)
            tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.warning_signal_position, 10)).grid(row=8, column=4, padx=2)
            tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.warning_signal_position, 10)).grid(row=8, column=5, padx=2)
            self.warning_signal_position_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.warning_signal_position, 0, 100))

        # Button Height
        if not self.is_basic_training_mode():
            tk.Label(input_frame, text="Button Height:", font=("Tahoma", 12)).grid(row=9, column=0, pady=2, sticky="e")
            self.button_height_entry = tk.Entry(input_frame, textvariable=self.button_height, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.button_height_entry.grid(row=9, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.button_height, 1)).grid(row=9, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.button_height, 1)).grid(row=9, column=3, padx=2)
            tk.Button(input_frame, text="+10", command=lambda: self.increment_value(self.button_height, 10)).grid(row=9, column=4, padx=2)
            tk.Button(input_frame, text="-10", command=lambda: self.decrement_value(self.button_height, 10)).grid(row=9, column=5, padx=2)
            self.button_height_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.button_height, 0, 100))

        # Button Size
        if not self.is_basic_training_mode():
            tk.Label(input_frame, text="Button Size:", font=("Tahoma", 12)).grid(row=10, column=0, pady=2, sticky="e")
            self.button_size_entry = tk.Entry(input_frame, textvariable=self.button_size, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.button_size_entry.grid(row=10, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.button_size, 1)).grid(row=10, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.button_size, 1)).grid(row=10, column=3, padx=2)
            self.button_size_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.button_size, 0, 100))

        # Grace Radius
        if not self.is_basic_training_mode():
            tk.Label(input_frame, text="Grace Radius:", font=("Tahoma", 12)).grid(row=11, column=0, pady=2, sticky="e")
            self.grace_radius_entry = tk.Entry(input_frame, textvariable=self.grace_radius, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.grace_radius_entry.grid(row=11, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.grace_radius, 1)).grid(row=11, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.grace_radius, 1)).grid(row=11, column=3, padx=2)
            self.grace_radius_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.grace_radius, 0, 100))

        # Peck Slide
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode():
            tk.Label(input_frame, text="Peck Slide:", font=("Tahoma", 12)).grid(row=12, column=0, pady=2, sticky="e")
            self.peck_slide_entry = tk.Entry(input_frame, textvariable=self.peck_slide, validate="key", validatecommand=(self.root.register(self.validate_between_0_and_100), '%P'), width=5)
            self.peck_slide_entry.grid(row=12, column=1, pady=2, sticky="w")
            tk.Button(input_frame, text="+", command=lambda: self.increment_value(self.peck_slide, 1)).grid(row=12, column=2, padx=2)
            tk.Button(input_frame, text="-", command=lambda: self.decrement_value(self.peck_slide, 1)).grid(row=12, column=3, padx=2)
            self.peck_slide_entry.bind("<FocusOut>", lambda e: self.validate_entry(self.peck_slide, 0, 100))


        # Highlight Warning Signal
        if not self.is_basic_training_mode() and not self.is_schedule_training_mode() and not self.is_random_warning_mode():
            tk.Label(input_frame, text="Highlight Warning Signal:", font=("Tahoma", 12)).grid(row=13, column=0, pady=2, sticky="e")
            self.highlight_warning_signal_check = tk.Checkbutton(input_frame, variable=self.highlight_warning_signal)
            self.highlight_warning_signal_check.grid(row=13, column=1, pady=2, sticky="w")

        # Add Is Spot On to More Options
        if not self.is_basic_training_mode():
            tk.Label(input_frame, text="Is Spot On:", font=("Tahoma", 12)).grid(row=14, column=0, pady=2, sticky="e")
            self.is_spot_on_check = tk.Checkbutton(input_frame, variable=self.is_spot_on)
            self.is_spot_on_check.grid(row=14, column=1, pady=2, sticky="w")

        # Configure columns to expand and center-align the grid
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(2, weight=1)
        input_frame.grid_columnconfigure(3, weight=1)
        input_frame.grid_columnconfigure(4, weight=1)
        input_frame.grid_columnconfigure(5, weight=1)

        # Move Confirm button to the position of the Next button
        self.next_button.config(text="Confirm", command=self.confirm_more_options)
        self.next_button.pack_forget()  # Hide the confirm button

        self.back_button.config(state="normal", command=self.back_to_step_2)

    def confirm_more_options(self):
        # Handle confirmation of more options
        self.current_step = 2
        self.update_step()
        self.next_button.config(text="Next", command=self.next_step)
        self.next_button.pack(side="right", padx=5, pady=5)  # Show the confirm button again

    def back_to_step_2(self):
        self.current_step = 2
        self.update_step()
        self.next_button.config(text="Next", command=self.next_step)
        self.next_button.pack(side="right", padx=5, pady=5)  # Show the confirm button again

    def validate_integer(self, value):
        return value.isdigit() or value == ""

    def validate_reinforcement_ratio(self, value):
        return value.isdigit() and len(value) <= 3 or value == ""

    def validate_between_0_and_100(self, value):
        if value.isdigit():
            return 0 <= int(value) <= 100
        return  value == "0"

    def validate_greater_than_1(self, value):
        if value.isdigit():
            return int(value) >= 1
        return  value == "1"

    def validate_between_1_and_10(self, value):
        if value.isdigit():
            return 1 <= int(value) <= 10
        return value == "1"

    def validate_between_1_and_600(self, value):
        if value.isdigit():
            return 1 <= int(value) <= 600
        return value == "1"
    
    def validate_entry(self, variable, min_value, max_value):
        try:
            value = int(variable.get())
            if value < min_value:
                variable.set(min_value)
            elif value > max_value:
                variable.set(max_value)
        except ValueError:
            variable.set(min_value)

    def show_step_3(self):
        self.clear_frame()

        tk.Label(self.step_frame, text="Step 3: Review Session Details", font=("Tahoma", 14)).pack(pady=5)

        input_frame = tk.Frame(self.step_frame)
        input_frame.pack(expand=True)

        # Display session data in a multiline Text widget with a scrollbar
        session_data = self.get_session_data()
        details = "\n".join(f"{key.replace('_', ' ').title()}: {value}" for key, value in session_data.items())

        self.details_text = tk.Text(input_frame, wrap="word", height=20, width=80)
        self.details_text.insert("1.0", details)
        self.details_text.tag_configure("center", justify="center")
        self.details_text.tag_add("center", "1.0", "end")
        self.details_text.config(state="normal")
        self.details_text.pack(side="left")

        scrollbar = tk.Scrollbar(input_frame, command=self.details_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.details_text.config(yscrollcommand=scrollbar.set)

        self.back_button.config(state="normal", command=self.back_to_step_2)
        self.next_button.config(text="Submit", command=self.confirm_submission)

    def confirm_submission(self):
        session_data = self.get_session_data()
        required_fields = ['Subject Name', 'Mode', 'Reinforcement Ratio', 'Total Reinforcements', 'Punishment Duration', 'Feed Time', 'Consecutive Warnings Limit', 'Warning Alarm Volume', 'Warning Display Volume', 'Warning Hits', 'Punishment Periodicity', 'Warning Duration', 'Time Before Warning Signal', 'Warning Signal Position', 'Highlight Warning Signal', 'Is Spot On']
        empty_fields = [key for key in required_fields if session_data[key] == ""]
        if empty_fields:
            messagebox.showwarning("Warning", f"The following fields must be filled out: {', '.join(empty_fields)}")
        else:
            if messagebox.askyesno("Confirm Submission", "Are you sure you want to submit?"):
                self.submit()

    def get_session_data(self):
        mode_id = next((mode['mode_id'] for mode in self.modes if mode['mode_name'] == self.mode_id.get()), None)
        return {
            'session_id': self.session_id,  # Generate a new UUID for the session
            'Subject Name': self.subject_name.get(),
            'Mode': mode_id,
            'Reinforcement Ratio': self.reinforcement_ratio.get(),
            'Total Reinforcements': self.total_reinforcements.get(),
            'Punishment Duration': self.punishment_duration.get(),
            'Feed Time': self.feed_time.get(),
            'Consecutive Warnings Limit': self.consecutive_warnings_limit.get(),
            'Warning Alarm Volume': self.warning_alarm_volume.get(),
            'Warning Display Volume': self.warning_display_volume.get(),
            'Warning Hits': self.warning_hits.get(),
            'Punishment Periodicity': self.punishment_periodicity.get(),
            'Warning Duration': self.warning_duration.get(),
            'Time Before Warning Signal': self.time_before_warning_signal.get(),
            'Warning Signal Position': self.warning_signal_position.get(),
            'Button Height': self.button_height.get(),
            'Button Size': self.button_size.get(),
            'Grace Radius': self.grace_radius.get(),
            'Peck Slide': self.peck_slide.get(),
            'Highlight Warning Signal': self.highlight_warning_signal.get(),
            'Is Spot On': self.is_spot_on.get(),
            'Comments': self.comments.get()
        }

    def next_step(self):
        if self.current_step == 1:
            if not self.subject_name.get().strip():
                messagebox.showerror("Error", "Subject name is required.")
                return
            self.load_last_session_data()

        self.current_step += 1
        self.update_step()

    def previous_step(self):
        if self.current_step > 1:
            self.current_step -= 1
        self.update_step()

    def update_step(self, *args):
        if self.current_step == 1:
            self.show_step_1()
        elif self.current_step == 2:
            self.show_step_2()
        elif self.current_step == 3:
            self.show_step_3()

    def clear_frame(self):
        for widget in self.step_frame.winfo_children():
            widget.destroy()

    def load_last_session_data(self):
        subject_name = self.subject_name.get()
        subject = self.pg_controller.select_subject_by_name(subject_name)
        if subject:
            last_session = self.pg_controller.find_last_session_by_subject(subject['subject_id'])
            if last_session:
                if 'reinforcement_ratio' in last_session:
                    self.reinforcement_ratio.set(last_session['reinforcement_ratio'])
                if 'total_reinforcements' in last_session:
                    self.total_reinforcements.set(last_session['total_reinforcements'])
                if 'warning_alarm_volume' in last_session:
                    self.warning_alarm_volume.set(last_session['warning_alarm_volume'])
                if 'warning_display_volume' in last_session:
                    self.warning_display_volume.set(last_session['warning_display_volume'])
                if 'warning_hits' in last_session:
                    self.warning_hits.set(last_session['warning_hits'])                  
                if 'punishment_duration' in last_session:
                    self.punishment_duration.set(last_session['punishment_duration'])
                if 'feed_time' in last_session:
                    self.feed_time.set(last_session['feed_time'])
                if 'consecutive_warnings_limit' in last_session:
                    self.consecutive_warnings_limit.set(last_session['consecutive_warnings_limit'])
                if 'is_spot_on' in last_session:
                    self.is_spot_on.set(last_session['is_spot_on'])
                if 'punishment_periodicity' in last_session:
                    self.punishment_periodicity.set(last_session['punishment_periodicity'])
                if 'warning_duration' in last_session:
                    self.warning_duration.set(last_session['warning_duration'])
                if 'time_before_warning_signal' in last_session:
                    self.time_before_warning_signal.set(last_session['time_before_warning_signal'])
                if 'highlight_warning_signal' in last_session:
                    self.highlight_warning_signal.set(last_session['highlight_warning_signal'])
                if 'warning_signal_position' in last_session:
                    self.warning_signal_position.set(last_session['warning_signal_position'])
                if 'button_height' in last_session:
                    self.button_height.set(last_session['button_height'])
                if 'button_size' in last_session:
                    self.button_size.set(last_session['button_size'])
                if 'grace_radius' in last_session:
                    self.grace_radius.set(last_session['grace_radius'])
                if 'peck_slide' in last_session:
                    self.peck_slide.set(last_session['peck_slide'])
                if 'mode_id' in last_session:
                    mode_name = next((mode['mode_name'] for mode in self.modes if mode['mode_id'] == last_session['mode_id']), None)
                    if mode_name:
                        self.mode_id.set(mode_name)

    def on_subprocess_complete(self):
        print("Subprocess has completed.")

    def submit(self):
        print("Submitting session Data...", self.get_session_data())
        session_data = self.get_session_data()
        session_id = session_data['session_id']
        subject_name = session_data['Subject Name']
        reinforcement_ratio = session_data['Reinforcement Ratio']
        total_reinforcements = session_data['Total Reinforcements']
        punishment_duration = session_data['Punishment Duration']
        feed_time = session_data['Feed Time']
        is_spot_on = session_data['Is Spot On']
        mode_id = session_data['Mode']
        consecutive_warnings_limit = session_data['Consecutive Warnings Limit']
        warning_alarm_volume = session_data['Warning Alarm Volume']
        warning_display_volume = session_data['Warning Display Volume']
        warning_hits = session_data['Warning Hits']
        punishment_periodicity = session_data['Punishment Periodicity']
        warning_duration = session_data['Warning Duration']
        time_before_warning_signal = session_data['Time Before Warning Signal']
        highlight_warning_signal = session_data['Highlight Warning Signal']
        warning_signal_position = session_data['Warning Signal Position']
        button_height = session_data['Button Height']
        button_size = session_data['Button Size']
        grace_radius = session_data['Grace Radius']
        peck_slide = session_data['Peck Slide']
        comments = session_data['Comments']

        subject = self.pg_controller.select_subject_by_name(subject_name)
        # if not subject:
        #     subject_id = self.pg_controller.insert_subject(subject_name)
        # else:
        
        subject_id = subject['subject_id']

        # Precompute warning quartiles for mode 6 (VARIABLE WARNING)
        warning_q1, warning_q2, warning_q3 = None, None, None
        if mode_id == 6:
            from self_control_software.self_control.utils.variable_ratio import compute_warning_quartiles
            warning_q1, warning_q2, warning_q3 = compute_warning_quartiles(int(reinforcement_ratio), int(warning_hits))

        session_data = {
            'session_id': session_id,  # Use the generated UUID
            'reinforcement_ratio': reinforcement_ratio,
            'warning_hits': warning_hits,
            'punishment_duration': punishment_duration,
            'feed_time': feed_time,
            'total_reinforcements': total_reinforcements,
            'consecutive_warnings_limit': consecutive_warnings_limit,
            'warning_alarm_volume': warning_alarm_volume,
            'warning_display_volume': warning_display_volume,
            'subject_id': subject_id,
            'mode_id': mode_id,
            'is_spot_on': is_spot_on,
            'punishment_periodicity': punishment_periodicity,
            'warning_duration': warning_duration,
            'time_before_warning_signal': time_before_warning_signal,
            'highlight_warning_signal': highlight_warning_signal,
            'warning_signal_position': warning_signal_position,
            'button_height': button_height,
            'button_size': button_size,
            'grace_radius': grace_radius,
            'peck_slide': peck_slide,
            'comments': comments,
            'warning_q1': warning_q1,
            'warning_q2': warning_q2,
            'warning_q3': warning_q3
        }
        # Insert the session into the database and get the session_id

        received_session_id = self.pg_controller.insert_session(session_data)
        print("Received session ID:", received_session_id)
        if received_session_id:
            self.root.after(100, self.root.destroy)  # Close the Tkinter window after a short delay
            # Run the subprocess in a new thread and call on_subprocess_complete when done
            threading.Thread(target=self.run_subprocess, args=(received_session_id,)).start()
        else:
            print("Failed to insert session.")
        print()
        

    def run_subprocess(self, session_id):
        app_path = os.path.join(project_root, 'self_control_software','self_control', 'app.py')
        subprocess.run(["python", app_path, str(session_id)])
        
        self.on_subprocess_complete()

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiStepApp(root)
    root.mainloop()