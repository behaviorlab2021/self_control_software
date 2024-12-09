import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ast import Pass
from cProfile import run
from logging import warning
from kivy.config import Config  # Import the Config module
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'left', '-1440')
Config.set('graphics', 'fullscreen', 'auto')
import subprocess

from kivy.core.window import Window
from xml.dom.pulldom import parseString
from kivy.uix.behaviors import ButtonBehavior  
from kivy.uix.image import Image  
from kivy.lang import Builder    
from kivy.uix.floatlayout import FloatLayout
from self_control.services.house_light import HouseLight  
from self_control.services.writer import Writer
import kivy
from kivy.app import App
from kivy.clock import Clock
from numpy import True_
from self_control.services.feeder import Feeder
from self_control.utils.functions import distance_from
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.graphics.vertex_instructions import Rectangle
from kivy.core.audio import SoundLoader
import random
import sys
import os 
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID
from self_control.services.clicker import Clicker
import datetime
from kivy.properties import NumericProperty
import json
from self_control.services.postgres import ExperimentDB


constant_data =  {}

subject_name = None


class ExperimentLayout(FloatLayout):

    experiment_data = constant_data

    button_height = 0.6
    consecutive_warnings = 0
    feeding_condition = False
    score = 0
    used_tries = 0
    clicks_label = StringProperty()
    score_label = StringProperty()
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
    label_left = ObjectProperty(None)
    label_right = ObjectProperty(None)
    panel_connected_label = ObjectProperty(None)
    spot = ObjectProperty(None)
    was_warned = False

    warning_signal_points = []


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
            self.warning_signal_points = [random.randint(1, self.experiment_data["reinforcement_ratio"] - self.experiment_data["warning_pecks"] - 1)]
        else:
            self.warning_signal_points = []

    def on_touch_down(self,touch):
        #Event Touch
        if self.button_green.opacity == 0:
            writer.write_peck_data_blind( self.score, self.quarter, self.clicks, touch.sx, touch.sy, "blind-peck", not self.button_red.disabled)
        else:
            writer.write_peck_data( self.score, self.quarter, self.clicks, touch.sx, touch.sy,  not self.button_red.disabled)

        if self.experiment_data["is_spot_on"]:
            self.spot.pos_hint = {'center_x':touch.sx, 'center_y':touch.sy}
        return super(FloatLayout, self).on_touch_down(touch)

    def check_reinforcement_condition(self):
        if (self.button_green.button_count >= self.experiment_data["reinforcement_ratio"]):
            self.positive_reinforcement()

    def end_experiment(self):
        houseLight.deactivate()
        self.turn_off_screen()
        self.create_results_pdf()
        #Event End of Experiment
        writer.write_data(self.score, self.quarter, self.clicks, "end_of_experiment", False)
    
    def create_results_pdf(self):
        # Call the R script
        result = subprocess.run(['Rscript', 'create_pdf.R', writer.filename], capture_output=True, text=True)
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
            print("In start_warning_signal_training")
            self.play_sound()
            if self.experiment_data["highlight_warning_signal"]:
                houseLight.deactivate()  
            self.buzzer = Clock.schedule_interval(self.sound_buzzer, 0.5)
            self.button_red.enable_button()
            self.button_green.disable_button()
            self.warning_signal_scheduled_event = Clock.schedule_once(self.warning_signal_training_punishment, self.experiment_data["warning_duration"])
            writer.write_data(self.score, self.quarter, self.clicks, "warning-"+str(int(self.warning_quarter)), not self.button_red.disabled)
        
        

        # self.button_green.di
        self.update_warning_quarter()
        #Event warning
        pass

    def stop_warning_signal_training(self):
        houseLight.activate()
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
        if not self.was_warned and self.button_green.button_count in self.warning_signal_points:
            self.play_sound()
            self.buzzer = Clock.schedule_interval(self.sound_buzzer, 0.5)
            self.button_red.enable_button()
            self.was_warned = True
            self.warning_variable = True
            self.update_warning_quarter()
            #Event warning
            writer.write_data(self.score, self.quarter, self.clicks, "warning-"+str(int(self.warning_quarter)), not self.button_red.disabled)
        
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
            houseLight.activate()
            self.turn_on_screen()
            self.feeding_condition = False
            self.label_right.text = "00"
            self.reset_quarters()
            self.warning_variable = False
            #Event Starting after reinforcement
            writer.write_data(self.score, self.quarter, self.clicks, "starting-again", not self.button_red.disabled)
        pass


    def feed(self):
        if not self.feeding_condition:
            self.feeding_condition = True
            self.turn_off_screen() 
            houseLight.deactivate()
            feeder.activate()

            feeder.create_deactivate_feeder_event(self.experiment_data["feed_time"])
            Clock.schedule_once(self.turn_feeding_condition_off, self.experiment_data["feed_time"])
            #Event Reinforcement
            writer.write_data(self.score, self.quarter, self.clicks, "feeding", not self.button_red.disabled)

    def check_if_punishment(self):
        if self.used_tries > self.experiment_data["warning_pecks"]:
            self.punish()
    
    def turn_off_screen(self):
        self.rect.source ="assets/images/black_panel.png"
        self.button_red.disable_button()
        self.button_green.disable_button()
        self.spot.opacity = 0
        self.label_left.opacity = 0
        self.panel_connected_label.opacity = 0.3
        self.label_right.opacity = 0

    def turn_on_screen(self):
        self.rect.source ="assets/images/panel.png"
        self.button_green.enable_button()
        # self.button_red_shadow.enable_button()
        self.spot.opacity = 1
        self.label_left.opacity = 1
        self.panel_connected_label.opacity = 1
        self.label_right.opacity = 1

    def punish(self):
        houseLight.deactivate()
        self.buzzer.cancel() 
        self.turn_off_screen()
        self.subsequent_punishments += 1 
        self.button_green.zeroing()
        Clock.schedule_once(self.un_punish, self.experiment_data["punishment_duration"])
        #Event Punishment
        writer.write_data(self.score, self.quarter, self.clicks, "punishment", not self.button_red.disabled)

    def un_punish(self, dt):
        Clock.unschedule(self.warning_signal_scheduled_event)
        self.stop_warning_signal_training()

        self.check_if_warning_signal_training()
        houseLight.activate()
        self.turn_on_screen()
        self.used_tries = 0
        # self.button_red_shadow.enable_button()
        self.label_right.text = "00"
        self.was_warned = True
        self.reset_quarters()
        self.warning_variable = False
        #Event Staring Over
        if self.subsequent_punishments > self.experiment_data["consecutive_warnings_limit"]:
            self.randomize_array()
            self.subsequent_punishments = 0

        writer.write_data(self.score, self.quarter, self.clicks, "starting-over", not self.button_red.disabled) 

    def update_score(self):
        writer.write_data(self.score, self.quarter, self.clicks, "score_updated", not self.button_red.disabled)
        self.clicks = self.button_green.button_count
        self.update_used_tries()
        self.check_if_punishment()
        self.check_reinforcement_condition()
        self.check_if_red()
        self.update_quarter()
        self.update_labels()

    def update_labels(self):

        self.score_label = str(self.score).zfill(2)
        self.clicks_label = str(self.clicks).zfill(2)
        self.label_right.text = self.clicks_label
        self.label_left.text = self.score_label
#test

    def update_used_tries(self):
        if self.button_red.disabled == False:
            self.used_tries += 1
        else:   
            self.used_tries = 0

    def usb_remove_callback(self, device_id, device_info):
        if device_info[ID_VENDOR_ID] == "0c45":
            print(f"{device_info[ID_VENDOR_ID]}")
            print("Touch Pannel if DISCONNECTED")
            self.panel_connected_label.text = "Touch Pannel is DISCONNECTED"
            self.panel_connected_label.color = [1, 0.2, 0.2, 1]

    def usb_add_callback(self, device_id, device_info):
        if device_info[ID_VENDOR_ID] == "0c45":
            print(f"{device_info[ID_VENDOR_ID]}")
            print("Touch Pannel is RECONNECTED")
            self.panel_connected_label.text = "Touch Pannel is RECONNECTED"
            self.panel_connected_label.color = [0.2, 0.2, 0.2, 0.2]
    
    def __init__(self, experiment_arguments, **kwargs):

        # Use the renamed experiment_arguments object
        self.experiment_data = experiment_arguments


        # Clock scheduling
        Clock.schedule_once(self.prepare_buttons, 0.8)

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
        writer.writer_update(self.experiment_data)


        # Event Start
        writer.write_data(self.score, self.quarter, 0, "Start", False)

        # Inherit initialization
        super(FloatLayout, self).__init__(**kwargs)
        with self.canvas.before:
            self.rect = Rectangle(source="assets/images/panel.png")
        
        
    def adjust_button_height_based_on_subject(self):
        """Adjust button height based on the subject."""
        if subject_name == "Ermis":
            self.button_height = 0.75
        elif subject_name  == "Moses":
            self.button_height = 0.65
        elif subject_name == "Snik":
            self.button_height = 0.85
        elif subject_name == "Adam":
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
        houseLight.activate()

    def _keyboard_closed(self):
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):

        if keycode[1] == 'escape':
            # self.end_experiment()
            houseLight.deactivate()
            App.get_running_app().stop()


        elif keycode[1] == 'spacebar':

            print("spacebar")
            if self.button_red.disabled == True :
                #Event free-food
                writer.write_data(self.score, self.quarter, self.clicks, "free-food", not self.button_red.disabled) 
                self.positive_reinforcement()
            
        elif keycode[1] == 'enter':
            print("enter")
            # Event gratis-red
            writer.write_data(self.score, self.quarter, self.clicks, "gratis-red-"+str(int(self.warning_quarter)), not self.button_red.disabled)
            if self.button_red.disabled == False :
                self.negative_reinforcement()
                if self.warning_signal_training_running:
                    self.stop_warning_signal_training()
                

        return True


    def positive_reinforcement(self):
        self.stop_warning_signal_training()
        self.consecutive_warnings = 0
        self.score = self.score + 1
        self.feed()
        self.subsequent_punishments = 0
        self.button_green.button_count = 0
        self.update_quarter()
        self.update_labels()
        self.update_score()
        writer.write_data(self.score, self.quarter, self.clicks, "reinforcement", not self.button_red.disabled)

        pass

    def negative_reinforcement(self):
        self.button_red.source = self.button_red.source_file
        self.button_red.disable_button()
        self.buzzer.cancel()
        # Clock.schedule_once(self.button_red_shadow.enable_button_delayed, 0.2)

class BasicImageButton(ButtonBehavior, Image):

    button_count = 0
    last_seen_outside = datetime.datetime.strptime('26 Aug 2023', '%d %b %Y')
    touch_start_x = None
    touch_start_y = None


    def on_touch_down(self, touch):
        self.touch_start_x = touch.sx
        self.touch_start_y = touch.sy
        if self.touch_on_button(touch) and not self.disabled:
            # self.parent.ids.label.text ...
            pass

    def change_button_image(self, dt):
        self.source = self.source_file

    def on_touch_up(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            self.button_count = self.button_count + 1
            self.source = self.source_file

    def disable_button(self):
        self.disabled = True
        self.opacity= 0
    
    def enable_button_delayed(self, dt):
        self.disabled = False
        self.opacity= 1

    def enable_button(self):
        self.disabled = False
        self.opacity= 1

    def touch_on_button(self, touch):

        window_x = Window.size[0]
        window_y = Window.size[1]
        button_center_x = self.pos_hint['center_x']
        button_center_y = self.pos_hint['center_y']
        button_radius = float(self.size_hint[0] / 2) + 0.01
        aspect_ratio = float(window_x/window_y)

        # touch.sx and touch.sy are the relative coordinates of tfhe touch to the window, between 0 and 1 
        dist_from_center  = distance_from(touch.sx, touch.sy, button_center_x, button_center_y, aspect_ratio)
        return  dist_from_center < button_radius
    def touch_close_to_button(self, touch):
        window_x = Window.size[0]
        window_y = Window.size[1]
        button_center_x = self.pos_hint['center_x']
        button_center_y = self.pos_hint['center_y']
        button_radius = float(self.size_hint[0] / 2) + 0.01   
        aspect_ratio = float(window_x/window_y)

        # touch.sx and touch.sy are the relative coordinates of tfhe touch to the window, between 0 and 1 
        dist_from_center  = distance_from(touch.sx, touch.sy, button_center_x, button_center_y, aspect_ratio)
        return  dist_from_center < (button_radius + (button_radius / 3))

class BasicImageButtonGreen(BasicImageButton):

    green_button_changed = False
    green_button_scheduled_event = None  # To keep track of the scheduled event


    def on_touch_down(self, touch):

        
        if self.touch_on_button(touch) and not self.disabled:
        # self.parent.ids.label.text ...
            pass

    def on_touch_up(self, touch):

        if self.touch_on_button(touch):
            print("IN", end=", ")
            # if  not self.disabled and (datetime.datetime.now()-self.last_seen_outside > datetime.timedelta(milliseconds=300)):
            print("VALID")
            if not self.green_button_changed:
                self.green_button_changed = True
                self.source = self.source_file_press
            
            else:
                self.green_button_changed = True
                Clock.unschedule(self.green_button_scheduled_event)

            self.green_button_scheduled_event = Clock.schedule_once(self.change_button_image, .3)
            clicker.click()
            self.disabled = True
            parent = self.parent
            # self.source = self.source_file
            parent.was_warned = False
            self.button_count = self.button_count + 1
            #Event Green
            writer.write_data(parent.score, parent.quarter, self.button_count, "green", not parent.button_red.disabled)
            parent.update_score()
            self.disabled = False
            # else:
            #     print("INVALID: ", (datetime.datetime.now()-self.last_seen_outside).total_seconds())   
   
        else:
            if self.touch_close_to_button(touch):
                print("MISSED")
            else:
                print("OUT")
                self.last_seen_outside = datetime.datetime.now()
    
    def change_button_image(self, dt):
        
        self.green_button_changed = False
        self.source = self.source_file


    def disable_button(self):
        self.disabled = True
        self.opacity= 0
        self.pos_hint = {'center_x': 4, 'center_y':self.parent.button_height}

    def enable_button_delayed(self, dt):
        print("Enabling Button delayed")
        self.disabled = False
        self.opacity= 1
        self.pos_hint = {'center_x': .7, 'center_y':self.parent.button_height}


    def enable_button(self):
        print("Enabling Button ")

        self.disabled = False
        self.opacity= 1
        self.pos_hint = {'center_x': .7, 'center_y':self.parent.button_height}

    def zeroing(self):
        self.button_count = 0

class BasicImageButtonRed(BasicImageButton):

    red_button_changed = False
    red_button_scheduled_event = None  # To keep track of the scheduled event

    def on_touch_up(self, touch):
        window_x = Window.size[0]
        window_y = Window.size[1]
        aspect_ratio = float(window_x/window_y)

        if self.touch_start_x:
            slide = distance_from(self.touch_start_x, self.touch_start_y, touch.sx, touch.sy, aspect_ratio)
            if slide>0.05:
                print("Feather")
                return
            else:
                if self.touch_on_button(touch) and not self.disabled:
                    self.button_count = self.button_count + 1
                    parent = self.parent
                    # Event Red
                    writer.write_data(parent.score, parent.quarter, parent.clicks, "red-"+str(int(parent.warning_quarter)), not parent.button_red.disabled) 
                    parent.negative_reinforcement()
                    if parent.warning_signal_training_running: 
                        parent.stop_warning_signal_training()
            # touch_start_x = None
            # touch_start_y = None



    def on_touch_up(self, touch):
        
        window_x = Window.size[0]
        window_y = Window.size[1]
        aspect_ratio = float(window_x/window_y)
        if self.touch_start_x:
            slide = distance_from(self.touch_start_x, self.touch_start_y, touch.sx, touch.sy, aspect_ratio)
            if slide>0.05:
                print("Feather")
                return
            else: 
                if self.touch_on_button(touch):
                    if  not self.disabled and (datetime.datetime.now()-self.last_seen_outside > datetime.timedelta(milliseconds=300)):
                        print("VALID")
                        if not self.red_button_changed:
                            self.red_button_changed = True
                            self.source = self.source_file_press
                        
                        else:
                            self.red_button_changed = True
                            Clock.unschedule(self.red_button_scheduled_event)
            
                        self.red_button_scheduled_event = Clock.schedule_once(self.change_button_image, .3)
                        clicker.click()
                        self.button_count = self.button_count + 1
                        parent = self.parent
                        # Event Red
                        writer.write_data(parent.score, parent.quarter, parent.clicks, "red-"+str(int(parent.warning_quarter)), not parent.button_red.disabled) 
                        parent.negative_reinforcement()
                        if parent.warning_signal_training_running: 
                            parent.stop_warning_signal_training()
                    else:
                        print("INVALID: ", (datetime.datetime.now()-self.last_seen_outside).total_seconds())   
        
                else:
                    if self.touch_close_to_button(touch):
                        pass
                    else:
                        self.last_seen_outside = datetime.datetime.now()

    def disable_button(self):
        parent = self.parent
        self.disabled = True
        self.opacity= 0
        self.pos_hint = {'center_x': parent.experiment_data["warning_signal_position"], 'center_y':parent.button_height}
            
    def enable_button(self):
        
        parent = self.parent
        self.disabled = False
        self.opacity= (parent.experiment_data["warning_display_volume"] / 100)
        #Warning Volume
        self.pos_hint = {'center_x':parent.experiment_data["warning_signal_position"], 'center_y':parent.button_height}

class BasicImageButtonGrey(BasicImageButton):

    def on_touch_up(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            self.source = self.source_file
            parent = self.parent
            if not parent.warning_variable:
                # Event Before
                writer.write_data(parent.score, parent.quarter, parent.clicks, "before", not parent.button_red.disabled) 
                pass 
            else:    
                # Event After
                writer.write_data(parent.score, parent.quarter, parent.clicks, "after", not parent.button_red.disabled) 
                pass

    def disable_button_100(self):
        self.disabled = True
        #Warning Volume
        self.opacity= 1
        self.pos_hint = {'center_x':.3, 'center_y':self.parent.button_height}

    def disable_button_0(self):
        self.disabled = True
        #Warning Volume
        self.opacity= 0
        self.pos_hint = {'center_x':.3, 'center_y':self.parent.button_height}

    def enable_button(self):
        self.disabled = False
        #Warning Volume
        self.opacity= 1
        self.pos_hint = {'center_x':.3, 'center_y':self.parent.button_height}

    
class MainApp(App):

    def __init__(self, experiment_arguments, **kwargs):
        self.my_experiment_arguments = experiment_arguments
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        Builder.load_file("kv/self_control.kv")
        layout = ExperimentLayout(experiment_arguments=self.my_experiment_arguments)
        return layout

if __name__ == "__main__":
    # Expecting a JSON string as the first argument from the command line
    experiment_id = sys.argv[1]

    db = ExperimentDB(dbname='postgres', user='postgres', password='pigeon123!')
    db.connect()

    experiment = db.find_experiment_by_id(experiment_id)
    experiment_dict = dict(experiment)  # Convert RealDictRow to a regular dictionary

    
    subject_id = experiment['subject_id']
    subject = db.find_subject_by_id(subject_id)
    subject_name = subject['subject_name']
    
    db.close()

    feeder = Feeder()
    clicker = Clicker()
    houseLight = HouseLight()
    feeder.deactivate()
    houseLight.activate()

    writer = Writer(experiment_dict, subject_name)
    
    # Pass the experiment_arguments object to the main application
    mainApp = MainApp(experiment_arguments=experiment_dict)
    mainApp.run()