import sys
import os

# Add the parent directory of self_control_software to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from kivy.app import App
from kivy.lang import Builder
from self_control_software.self_control.components.layout.experiment_layout import ExperimentLayout

from self_control_software.self_control.components.buttons.green_button import BasicImageButtonGreen
from self_control_software.self_control.components.buttons.red_button import BasicImageButtonRed


class MainApp(App):

    def __init__(self, session_arguments, feeder, clicker, houseLight, writer, async_pg_controller, **kwargs):
        self.session_arguments = session_arguments
        self.writer = writer  # Store writer as an instance variable
        self.async_pg_controller = async_pg_controller  # Store async_pg_controller as an instance variable
        self.clicker = clicker  # Store clicker as an instance variable
        self.houseLight = houseLight  # Store houseLight as an instance variable
        self.feeder = feeder  # Store feeder as an instance variable
        super(MainApp, self).__init__(**kwargs)
        self.icon = 'self_control_software/self_control/assets/icons/pigeon.png'  # Set the path to your icon file

    def build(self):
        Builder.load_file("kv/experiment.kv")
        layout = ExperimentLayout(session_arguments=self.session_arguments, feeder=self.feeder, clicker=self.clicker, houseLight=self.houseLight, writer=self.writer, async_pg_controller=self.async_pg_controller)
        return layout
    
    def set_clicker(self,button):
        button.clicker = self.clicker
    
    def set_writer(self, button):
        button.set_writer(self.writer)
        
    def set_async_pg_controller(self, button):
        button.set_async_pg_controller(self.async_pg_controller)

