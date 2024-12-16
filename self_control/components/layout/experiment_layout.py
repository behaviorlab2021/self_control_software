import sys
import os
import subprocess
import random
import datetime
from kivy.config import Config  # Import the Config module

Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'left', '-1440')
Config.set('graphics', 'fullscreen', 'auto')

from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.graphics.vertex_instructions import Rectangle
from kivy.core.audio import SoundLoader
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID
from self_control_software.self_control.services.house_light import HouseLight
from self_control_software.self_control.services.writer import Writer
from self_control_software.self_control.services.injector import Injector
from self_control_software.self_control.services.feeder import Feeder
from self_control_software.self_control.utils.functions import distance_from
from self_control_software.self_control.services.clicker import Clicker
from self_control_software.self_control.services.postgres import ExperimentDB
from self_control_software.self_control.utils.subject_names import ERMIS, ADAM, SNIK, MOSES



experiment_data = None
subject_name = None



class ExperimentLayout(FloatLayout):

    button_height = 0.6
    consecutive_warnings = 0
    feeding_condition = False
    score = 0
    used_tries = 0

    is_panel_connected = False
    subsequent_punishments = 0
    clicks = 0
    quarter = 1
    warning_quarter = 0
    warning_variable = False
    warning_signal_training_running = False
    warning_signal_scheduled_event = None
    buzzer_file = "assets/audio/buzzer.mp3"
    sound = SoundLoader.load(buzzer_file) 
    canvas_picture = ObjectProperty(None)
    button_green = ObjectProperty(None)
    button_red = ObjectProperty(None)
    label_top_left = ObjectProperty(None)
    label_top_right = ObjectProperty(None)
    label_bottom_left = ObjectProperty(None)
    panel_connected_label = ObjectProperty(None)
    spot = ObjectProperty(None)
    was_warned = False
    warning_signal_index = None
    round = 0


    def check_if_hopper_training(self, dt):
        if (self.experiment_data["mode_id"] == 1):
            print("-------------------- Mode 1 ----------------------")
            self.button_green.disable_button()
            pass

    def __init__(self, experiment_arguments, writer, injector, clicker, houseLight, feeder, **kwargs):

        # Use the renamed experiment_arguments object
        self.experiment_data = experiment_arguments
        self.writer = writer  # Store writer as an instance variable
        self.injector = injector  # Store injector as an instance variable
        self.houseLight = houseLight  # Store houseLight as an instance variable
        self.feeder = feeder  # Store feeder as an instance variable


        # Clock scheduling
        Clock.schedule_once(self.prepare_buttons, 0.8)
        Clock.schedule_once(self.check_if_hopper_training, 0.8)

        Clock.schedule_interval(self.add_cumulative_record, 0.5)  





        # Keyboard event binding
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        # USB MONITORING
        self.usb_monitor = USBMonitor()
        self.usb_monitor.start_monitoring(on_connect=self.usb_add_callback, on_disconnect=self.usb_remove_callback)


        # Initialize experiment data
        self.reset_quarters()
        

        # USB device check
        devices_dict = self.usb_monitor.get_available_devices()
        # if any(device.split("\\")[1] == "VID_0C45&PID_8419" for device in devices_dict):
        #     print("Application started with Touch Panel Connected")
        #     self.is_panel_connected = True
        # else:
        #     print("Application started with Touch Panel DISCONNECTED")
        #     self.is_panel_connected = False

                # Handle subject-specific logic
        print("Subject name: ", subject_name)
        if subject_name:
            self.adjust_button_height_based_on_subject()


        # Writer update
        self.writer.writer_update(self.experiment_data)
        self.injector.injector_update(self.experiment_data)


        # Event Start
        self.writer.write_data(self.score, self.quarter, 0, "Start", False,  -1)
        self.injector.inject_data(self.score, self.quarter, 0, "Start", False,  -1)

        # Inherit initialization
        super(FloatLayout, self).__init__(**kwargs)
        with self.canvas.before:
            self.rect = Rectangle(source="assets/images/panel.png")
        
        
    def initial_pannel_connected_text(self):
            # self.panel_connected_label.text = "Application started with Touch Pannel DISCONNECTED"
            # self.panel_connected_label.color = [1, 0.2, 0.2, 0.2]
        return ''
        # return 'Touch Pannel started ' + ('CONNECTED' if self.is_panel_connected else 'DISCONNECTED')


    
    def initial_pannel_connected_color(self):
        return [0.2, 0.2, 0.2, 0.2] if self.is_panel_connected  else [1, 0.2, 0.2, 1]
    


    def update_quarter(self):
        if self.clicks>= self.experiment_data["reinforcement_ratio"]:
            self.quarter = 0
        else:
            self.quarter = (self.clicks//( self.experiment_data["reinforcement_ratio"]/4))+1

    def update_warning_quarter(self):
        self.warning_quarter = self.quarter

    def reset_quarters(self):
        self.quarter = 1
        self.warning_quarter = 0


    def randomize_array(self):
        if self.experiment_data["mode_id"] == 4:
            self.warning_signal_index = random.randint(1, self.experiment_data["reinforcement_ratio"] - self.experiment_data["warning_hits"] - 1)
        else:
            self.warning_signal_index = None

    def on_touch_down(self,touch):
        #Event Touch
        if self.button_green.opacity == 0:
            self.writer.write_peck_data_blind( self.score, self.quarter, self.clicks, touch.sx, touch.sy, "blind-peck", not self.button_red.disabled, self.warning_signal_index)
            self.injector.inject_peck_data_blind( self.score, self.quarter, self.clicks, touch.sx, touch.sy, "blind-peck", not self.button_red.disabled, self.warning_signal_index)
        else:
            self.writer.write_peck_data( self.score, self.quarter, self.clicks, touch.sx, touch.sy,  not self.button_red.disabled, self.warning_signal_index)
            self.injector.inject_peck_data( self.score, self.quarter, self.clicks, touch.sx, touch.sy,  not self.button_red.disabled, self.warning_signal_index)

        if self.experiment_data["is_spot_on"]:
            self.spot.pos_hint = {'center_x':touch.sx, 'center_y':touch.sy}
        return super(FloatLayout, self).on_touch_down(touch)

    def check_reinforcement_condition(self):
        if (self.button_green.button_count >= self.experiment_data["reinforcement_ratio"]):
            self.positive_reinforcement()

    def end_experiment(self):
        self.houseLight.deactivate()
        self.create_results_pdf()
        #Event End of Experiment
        self.writer.write_data(self.score, self.quarter, self.clicks, "end_of_experiment", False, self.warning_signal_index)
        self.injector.inject_data(self.score, self.quarter, self.clicks, "end_of_experiment", False, self.warning_signal_index)    
        self.turn_off_screen()
        self.update_experiment_conditions()

    def create_results_pdf(self):
        # Call the R script
        result = subprocess.run(['Rscript', 'self_control_software/self_control/utils/create_pdf.R', self.writer.filename], capture_output=True, text=True)
        # Print the output from the R script
        print("Output from R script:")
        print(result.stdout)
        pass

    def check_if_warning_signal_training(self):
        if self.experiment_data["mode_id"] == 3 and self.score % self.experiment_data["punishment_periodicity"] == 0:  
            if self.consecutive_warnings <= self.experiment_data["consecutive_warnings_limit"]:    

                self.warning_signal_training_running = True
                self.warning_signal_scheduled_event = Clock.schedule_once(self.start_warning_signal_training, self.experiment_data["time_before_warning_signal"])
            else :
                self.consecutive_warnings = 0


    def start_warning_signal_training(self, dt):
        if self.warning_signal_training_running :
            self.consecutive_warnings = self.consecutive_warnings + 1
            self.play_sound()
            if self.experiment_data["highlight_warning_signal"]:
                self.houseLight.deactivate()  
            self.buzzer = Clock.schedule_interval(self.sound_buzzer, 0.5)
            self.button_red.enable_button()
            self.button_green.disable_button()
            self.warning_signal_scheduled_event = Clock.schedule_once(self.warning_signal_training_punishment, self.experiment_data["warning_duration"])
            self.writer.write_data(self.score, self.quarter, self.clicks, "warning-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
            self.injector.inject_data(self.score, self.quarter, self.clicks, "warning-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
        
        

        # self.button_green.di
        self.update_warning_quarter()
        #Event warning
        pass

    def stop_warning_signal_training(self):
        self.houseLight.activate()
        self.warning_signal_training_running = False
        Clock.unschedule(self.warning_signal_scheduled_event)
        self.button_green.enable_button()
        print("In stop_warning_signal_training")
        pass

    def warning_signal_training_punishment(self, dt):
        self.warning_signal_training_running = False
        self.punish()
        pass

    def check_if_red(self):
        if not self.was_warned and self.button_green.button_count == self.warning_signal_index:
            self.play_sound()
            self.buzzer = Clock.schedule_interval(self.sound_buzzer, 0.5)
            self.button_red.enable_button()
            self.was_warned = True
            self.warning_variable = True
            self.update_warning_quarter()
            #Event warning
            self.writer.write_data(self.score, self.quarter, self.clicks, "warning-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
            self.injector.inject_data(self.score, self.quarter, self.clicks, "warning-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
        
    def sound_buzzer(self, dt):
        self.play_sound()
        #Buzzer
        
    def play_sound(self):
        if self.sound:
            self.sound.volume = self.experiment_data["warning_alarm_volume"] / 100
            self.sound.play()
        pass
        
    def check_if_end(self):
        if (self.score >= self.experiment_data["total_reinforcements"]):
            self.end_experiment()
            return True
        else: 
            return False


    def turn_feeding_condition_off(self, dt):
               
        if not self.check_if_end():
            self.check_if_warning_signal_training()
            self.randomize_array()
            self.houseLight.activate()
            self.turn_on_screen()
            self.feeding_condition = False
            self.reset_quarters()
            self.warning_variable = False
            #Event Starting after reinforcement
            self.writer.write_data(self.score, self.quarter, self.clicks, "starting-again", not self.button_red.disabled, self.warning_signal_index)
            self.injector.inject_data(self.score, self.quarter, self.clicks, "starting-again", not self.button_red.disabled, self.warning_signal_index)
        pass


    def feed(self):
        if not self.feeding_condition:
            self.feeding_condition = True
            self.houseLight.deactivate()
            self.feeder.activate()

            self.feeder.create_deactivate_feeder_event(self.experiment_data["feed_time"])
            Clock.schedule_once(self.turn_feeding_condition_off, self.experiment_data["feed_time"])
            #Event Reinforcement
            self.writer.write_data(self.score, self.quarter, self.clicks, "feeding", not self.button_red.disabled, self.warning_signal_index)
            self.injector.inject_data(self.score, self.quarter, self.clicks, "feeding", not self.button_red.disabled, self.warning_signal_index)   
            self.turn_off_screen()
            self.update_experiment_conditions()

    def check_if_punishment(self):
        if self.used_tries > self.experiment_data["warning_hits"]:
            self.punish()
    
    def turn_off_screen(self):

        self.rect.source ="assets/images/black_panel.png"
        self.button_red.disable_button()
        self.button_green.disable_button()
        self.spot.opacity = 0
        self.panel_connected_label.opacity = 0.3
        self.label_top_left.opacity = 0
        self.label_top_right.opacity = 0
        self.label_bottom_left.opacity = 0


    def turn_on_screen(self):
        self.rect.source ="assets/images/panel.png"
        if not self.experiment_data["mode_id"] == 1:
            self.button_green.enable_button()
        # self.button_red_shadow.enable_button()
        self.spot.opacity = 1
        self.panel_connected_label.opacity = 1
        self.round += 1
        self.label_top_left.opacity = 1
        self.label_top_right.opacity = 1
        self.label_bottom_left.opacity = 1

    def punish(self):
        self.houseLight.deactivate()
        self.buzzer.cancel() 
        self.subsequent_punishments += 1 
        self.button_green.zeroing()
        Clock.schedule_once(self.un_punish, self.experiment_data["punishment_duration"])
        #Event Punishment
        self.writer.write_data(self.score, self.quarter, self.clicks, "punishment", not self.button_red.disabled, self.warning_signal_index)
        self.injector.inject_data(self.score, self.quarter, self.clicks, "punishment", not self.button_red.disabled, self.warning_signal_index)
        self.clicks = 0
        self.turn_off_screen()
        self.update_experiment_conditions()



    def un_punish(self, dt):
        Clock.unschedule(self.warning_signal_scheduled_event)
        self.stop_warning_signal_training()

        self.check_if_warning_signal_training()
        self.houseLight.activate()
        self.turn_on_screen()
        self.used_tries = 0
        # self.button_red_shadow.enable_button()
        self.was_warned = True
        self.reset_quarters()
        self.warning_variable = False
        #Event Staring Over
        if self.subsequent_punishments > self.experiment_data["consecutive_warnings_limit"]:
            self.randomize_array()
            self.subsequent_punishments = 0

        self.writer.write_data(self.score, self.quarter, self.clicks, "starting-over", not self.button_red.disabled, self.warning_signal_index) 
        self.injector.inject_data(self.score, self.quarter, self.clicks, "starting-over", not self.button_red.disabled, self.warning_signal_index)

    def update_experiment_conditions(self):


        self.clicks = self.button_green.button_count  # Updates the number of clicks the green button has
        self.update_used_tries() # Updates the number of green clicks while red is enabled.
        self.check_if_punishment() # Checks if the punishment condition is met
        self.check_reinforcement_condition() # Checks if the reinforcement condition is met
        self.check_if_red() # Checks if the red button should be enabled
        self.update_quarter() # Updates the quarter
        self.update_labels() # Updates the labels

        # Update the writer and injector
        self.writer.write_data(self.score, self.quarter, self.clicks, "score_updated", not self.button_red.disabled, self.warning_signal_index)
        self.injector.inject_data(self.score, self.quarter, self.clicks, "score_updated", not self.button_red.disabled, self.warning_signal_index)

    def update_labels(self):

        self.label_top_left.text = str(self.score).zfill(2)
        self.label_top_right.text = str(self.clicks).zfill(2)
        self.label_bottom_left.text = str(self.round).zfill(2)

    def update_used_tries(self):
        if self.button_red.disabled == False:
            self.used_tries += 1
        else:   
            self.used_tries = 0

    def usb_remove_callback(self, device_id, device_info):
        if device_info[ID_VENDOR_ID] == "0c45":
            print(f"{device_info[ID_VENDOR_ID]}")
            self.panel_connected_label.text = "Touch Pannel is DISCONNECTED"
            self.panel_connected_label.color = [1, 0.2, 0.2, 1]

    def usb_add_callback(self, device_id, device_info):
        if device_info[ID_VENDOR_ID] == "0c45":
            print(f"{device_info[ID_VENDOR_ID]}")
            self.panel_connected_label.text = "Touch Pannel is RECONNECTED"
            self.panel_connected_label.color = [0.2, 0.2, 0.2, 0.2]
    

    def adjust_button_height_based_on_subject(self):
        """Adjust button height based on the subject."""
        if subject_name == ERMIS:
            self.button_height = 0.75
        elif subject_name  == MOSES:
            self.button_height = 0.65
        elif subject_name == SNIK:
            self.button_height = 0.85
        elif subject_name == ADAM:
            self.button_height = 0.6
        else:
            print("No specific subject found.")


            
    def on_pos(self, *args):
        # update Rectangle position when MazeSolution position changes
        self.rect.pos = self.pos

    def on_size(self, *args):
        # update Rectangle size when MazeSolution size changes
        self.rect.size = self.size

    def prepare_buttons(self, dt):

        self.randomize_array()

        self.button_green.source = "assets/images/green_light.png"
        self.button_green.source_file = "assets/images/green_light.png"
        self.button_green.source_file_press = "assets/images/green_dark.png"

        self.button_red.source = "assets/images/red_light.png"
        self.button_red.source_file = "assets/images/red_light.png"
        self.button_red.source_file_press = "assets/images/red_dark.png"
        self.button_red.disable_button()
        if self.experiment_data["is_spot_on"]:
            self.spot.pos_hint = {'center_x':.3, 'center_y':.75}
        else:
            self.spot.pos_hint = {'center_x': 3, 'center_y':.75}

        # self.button_red_shadow.source = "assets/images/grey_light.png"
        # self.button_red_shadow.source_file = "assets/images/grey_light.png"
        # self.button_red_shadow.source_file_press = "assets/images/grey_dark.png"
        self.houseLight.activate()

    def _keyboard_closed(self):
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):

        if keycode[1] == 'escape':
            # self.end_experiment()
            self.houseLight.deactivate()
            App.get_running_app().stop()


        elif keycode[1] == 'spacebar':

            print("spacebar")
            if self.button_red.disabled == True :
                #Event free-food
                self.writer.write_data(self.score, self.quarter, self.clicks, "free-food", not self.button_red.disabled, self.warning_signal_index) 
                self.injector.inject_data(self.score, self.quarter, self.clicks, "free-food", not self.button_red.disabled, self.warning_signal_index)
                self.positive_reinforcement()
            
        elif keycode[1] == 'enter':
            print("enter")
            # Event gratis-red
            self.writer.write_data(self.score, self.quarter, self.clicks, "gratis-red-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
            self.injector.inject_data(self.score, self.quarter, self.clicks, "gratis-red-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
            if self.button_red.disabled == False :
                self.negative_reinforcement()
                if self.warning_signal_training_running:
                    self.stop_warning_signal_training()
                
        return True


    def positive_reinforcement(self):
        self.stop_warning_signal_training()
        self.consecutive_warnings = 0
        self.score = self.score + 1
        self.subsequent_punishments = 0
        self.button_green.button_count = 0
        self.feed()

        self.writer.write_data(self.score, self.quarter, self.clicks, "reinforcement", not self.button_red.disabled, self.warning_signal_index)
        self.injector.inject_data(self.score, self.quarter, self.clicks, "reinforcement", not self.button_red.disabled, self.warning_signal_index)
        pass
    def negative_reinforcement(self):
        self.button_red.source = self.button_red.source_file
        self.button_red.disable_button()
        self.buzzer.cancel()
        # Clock.schedule_once(self.button_red_shadow.enable_button_delayed, 0.2)

    def add_cumulative_record(self, dt):
        self.injector.inject_cumulative_record(self.clicks)
        pass