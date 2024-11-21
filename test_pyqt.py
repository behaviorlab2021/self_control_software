import sys
import subprocess
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QCheckBox, QFormLayout, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt


# Function to validate if the input is a number
def is_number(input_text):
    try:
        float(input_text)
        return True
    except ValueError:
        return False


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_subject = None  # Variable to store the selected subject
        self.init_ui()

    def init_ui(self):
        # Set up window title and layout
        self.setWindowTitle("Open Experiment")
        self.setFixedSize(400, 600)  # Set fixed size for the window

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)  # Align everything to the top

        # Subject selection (buttons)
        self.subject_label = QLabel("Select subject:", self)
        main_layout.addWidget(self.subject_label, alignment=Qt.AlignCenter)

        subject_buttons_layout = QHBoxLayout()  # Layout to hold the subject buttons
        self.subject_buttons = {}

        for subject in ["Adam", "Snik", "Moses", "Ermis"]:
            button = QPushButton(subject)
            button.clicked.connect(lambda checked, s=subject: self.subject_selected(s))
            subject_buttons_layout.addWidget(button)
            self.subject_buttons[subject] = button

        main_layout.addLayout(subject_buttons_layout)

        # Form layout for all inputs
        form_layout = QFormLayout()

        # Reinforcing ratio (empty initially)
        self.number_entry = QLineEdit("")
        self.number_entry.textChanged.connect(self.check_inputs)  # Connect to input checker
        form_layout.addRow(QLabel("Enter reinforcing ratio:"), self.number_entry)

        # Number of trials (empty initially)
        self.trials_entry = QLineEdit("")
        self.trials_entry.textChanged.connect(self.check_inputs)  # Connect to input checker
        form_layout.addRow(QLabel("Enter number of trials:"), self.trials_entry)

        # Visual warning level (empty initially)
        self.visual_warning_entry = QLineEdit("")
        self.visual_warning_entry.textChanged.connect(self.check_inputs)  # Connect to input checker
        form_layout.addRow(QLabel("Enter visual warning level %:"), self.visual_warning_entry)

        # Sound warning level (empty initially)
        self.sound_warning_entry = QLineEdit("")
        self.sound_warning_entry.textChanged.connect(self.check_inputs)  # Connect to input checker
        form_layout.addRow(QLabel("Enter sound warning level %:"), self.sound_warning_entry)

        # Warning signal horizontal position (empty initially)
        self.warning_signal_position_entry = QLineEdit("")
        self.warning_signal_position_entry.textChanged.connect(self.check_inputs)  # Connect to input checker
        form_layout.addRow(QLabel("Enter warning signal horizontal position (0.3 < x < 0.6):"), self.warning_signal_position_entry)

        # Warning duration (empty initially)
        self.warning_duration_entry = QLineEdit("")
        self.warning_duration_entry.textChanged.connect(self.check_inputs)  # Connect to input checker
        form_layout.addRow(QLabel("Enter warning duration (1-30 sec):"), self.warning_duration_entry)

        # Add form layout to the main layout
        main_layout.addLayout(form_layout)

        # Spacer item to push the button to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        # Open button (disabled initially)
        self.open_button = QPushButton("Open")
        self.open_button.setDisabled(True)  # Disable the button initially
        self.open_button.clicked.connect(self.start_kivy_app)
        main_layout.addWidget(self.open_button, alignment=Qt.AlignBottom)

        self.setLayout(main_layout)

    def subject_selected(self, subject_name):
        # When a subject is selected, call this function with the subject name
        print(f"Subject selected: {subject_name}")
        self.selected_subject = subject_name
        self.subject_label.setText(f"Selected subject: {subject_name}")

        # Reset all buttons to default color
        self.reset_button_colors()

        # Highlight the selected button
        self.subject_buttons[subject_name].setStyleSheet("border: 2px solid red; border-ra")
        # Check if inputs are valid and enable the "Open" button if so
        self.check_inputs()

    def reset_button_colors(self):
        # Reset all buttons to their default color
        for button in self.subject_buttons.values():
            button.setStyleSheet("")  # Reset stylesheet to default

    def check_inputs(self):
        # Enable the "Open" button only if all required fields are filled and a subject is selected
        if self.selected_subject and all([
            self.number_entry.text().strip(),
            self.trials_entry.text().strip(),
            self.visual_warning_entry.text().strip(),
            self.sound_warning_entry.text().strip(),
            self.warning_signal_position_entry.text().strip(),
            self.warning_duration_entry.text().strip(),
        ]):
            self.open_button.setEnabled(True)
        else:
            self.open_button.setEnabled(False)

    def start_kivy_app(self):
        # Gather all input values
        number_argument = self.number_entry.text().strip()
        trials_argument = self.trials_entry.text().strip()
        visual_warning_level_argument = self.visual_warning_entry.text().strip()
        sound_warning_level_argument = self.sound_warning_entry.text().strip()
        warning_signal_position_argument = self.warning_signal_position_entry.text().strip()
        warning_duration_argument = self.warning_duration_entry.text().strip()

        # Validation
        if not is_number(number_argument):
            self.show_error("Please enter a valid number for reinforcing ratio.")
            return
        if not is_number(trials_argument):
            self.show_error("Please enter a valid number for trials.")
            return
        if not is_number(visual_warning_level_argument):
            self.show_error("Please enter a valid visual warning level percentage.")
            return
        if not is_number(sound_warning_level_argument):
            self.show_error("Please enter a valid sound warning level percentage.")
            return
        if not is_number(warning_signal_position_argument) or not (0.3 <= float(warning_signal_position_argument) <= 0.6):
            self.show_error("Warning signal position must be between 0.3 and 0.6.")
            return
        if not is_number(warning_duration_argument) or not (1 <= int(warning_duration_argument) <= 30):
            self.show_error("Warning duration must be between 1 and 30 seconds.")
            return

        # Create the experiment arguments object
        experiment_arguments = {
            'reinforcement_ratio': number_argument,
            'total_reinforcements': trials_argument,
            'subject': self.selected_subject,  # Use the selected subject
            'mode': "2",
            'warning_display_volume': visual_warning_level_argument,
            'warning_alarm_volume': sound_warning_level_argument,
            'warning_signal_position': warning_signal_position_argument,
            'warning_duration': warning_duration_argument,
        }

        # Convert the experiment arguments to JSON
        experiment_arguments_json = json.dumps(experiment_arguments)

        # Call the Kivy app using subprocess
        subprocess.Popen(["python", "c:/Users/SKINNER BOX/Documents/self_control_software/self_control.py", experiment_arguments_json])

        # Close the PyQt5 window
        self.close()

    def show_error(self, message):
        # Show an error message in a message box
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()


# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
