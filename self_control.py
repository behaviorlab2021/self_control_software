from ast import Pass
from cProfile import run
from logging import warning
from kivy.config import Config  # Import the Config module
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'left', '-1440')
Config.set('graphics', 'fullscreen', 'auto')

from kivy.core.window import Window
from xml.dom.pulldom import parseString
from kivy.uix.behaviors import ButtonBehavior  
from kivy.uix.image import Image  
from kivy.lang import Builder    
from kivy.uix.floatlayout import FloatLayout
from house_light import HouseLight  
from writer import Writer
import kivy
from kivy.app import App
from kivy.clock import Clock
from numpy import True_
from experiment import Experiment
from feeder import Feeder
from functions import distance_from_center
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.graphics.vertex_instructions import Rectangle
from kivy.core.audio import SoundLoader
import random
import sys
import os 
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID
from clicker import Clicker
import datetime
from kivy.properties import NumericProperty


constant_data =  {
    'reinforcement_ratio' :30,
    'warning_signal_points' :[],
    'warning_pecks' :3,
    'punishment_period' :30,
    'feed_time' :5,
    'total_reinforcements' :35,
    'skip_to_next_value' :3,
    'warning_alarm_volume' :100,
    'warning_display_volume' :100,
    'punishment_condition' :0,
    'subject' :"Pigeon",
    'is_spot_on' :False,
    'random_warning' :False,
    'miliseconds_after_touch': 1000
}


[ADAM, SNIK, MOSES, ERMIS]  = ["Adam", "Snik", "Moses", "Ermis" ] 

class ExperimentLayout(FloatLayout):


    reinforcement_ratio = constant_data["reinforcement_ratio"]
    warning_signal_points = constant_data['warning_signal_points']
    warning_pecks = constant_data["warning_pecks"]
    punishment_period = constant_data["punishment_period"]
    feed_time = constant_data["feed_time"]
    total_reinforcements = constant_data["total_reinforcements"]
    skip_to_next_value = constant_data["skip_to_next_value"]
    warning_alarm_volume = constant_data["warning_alarm_volume"]
    warning_display_volume = constant_data["warning_display_volume"]
    punishment_condition = constant_data["punishment_condition"]
    subject = constant_data["subject"]
    is_spot_on = constant_data["is_spot_on"]
    random_warning = constant_data["random_warning"]
    button_height = 0.5
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

    buzzer_file = "assets/audio/buzzer.mp3"
    sound = SoundLoader.load(buzzer_file) 


    canvas_picture = ObjectProperty(None)
    button_left = ObjectProperty(None)
    button_right = ObjectProperty(None)
    label_left = ObjectProperty(None)
    label_right = ObjectProperty(None)
    panel_connected_label = ObjectProperty(None)
    button_right_shadow = ObjectProperty(None)
    spot = ObjectProperty(None)
    was_warned = False


    def initial_pannel_connected_text(self):
            # self.panel_connected_label.text = "Application started with Touch Pannel DISCONNECTED"
            # self.panel_connected_label.color = [1, 0.2, 0.2, 0.2]
        return ''
        # return 'Touch Pannel started ' + ('CONNECTED' if self.is_panel_connected else 'DISCONNECTED')


    
    def initial_pannel_connected_color(self):

        return [0.2, 0.2, 0.2, 0.2] if self.is_panel_connected  else [1, 0.2, 0.2, 1]
    


    def update_quarter(self):
        if self.clicks>= self.reinforcement_ratio:
            self.quarter = 0
        else:
            self.quarter = (self.clicks//( self.reinforcement_ratio/4))+1

    def update_warning_quarter(self):
        self.warning_quarter = self.quarter

    def reset_quarters(self):
        self.quarter = 1
        self.warning_quarter = 0


    def randomize_array(self):
        if self.random_warning:
            self.warning_signal_points = [random.randint(1, self.reinforcement_ratio - self.warning_pecks - 1)]
        else:
            self.warning_signal_points = []

    def on_touch_down(self,touch):
        #Event Touch
        if self.button_left.opacity == 0:
            writer.write_peck_data_blind( self.score, self.quarter, self.clicks, touch.sx, touch.sy, "blind-peck", not self.button_right.disabled)
        else:
            writer.write_peck_data( self.score, self.quarter, self.clicks, touch.sx, touch.sy,  not self.button_right.disabled)

        if self.is_spot_on:
            self.spot.pos_hint = {'center_x':touch.sx, 'center_y':touch.sy}
        return super(FloatLayout, self).on_touch_down(touch)

    def check_reinforcement_condition(self):

        if (self.button_left.button_count >= self.reinforcement_ratio):
            self.positive_reinforcement()

    def end_experiment(self):
        houseLight.deactivate()
        self.turn_off_screen()
        #Event End of Experiment
        writer.write_data(self.score, self.quarter, self.clicks, "end_of_experiment", False)

        pass

    def check_if_red(self):
        if not self.was_warned and self.button_left.button_count in self.warning_signal_points:
            self.play_sound()
            self.buzzer = Clock.schedule_interval(self.sound_buzzer, 0.5)
            self.button_right.enable_button()
            self.button_right_shadow.disable_button_100()
            self.was_warned = True
            self.warning_variable = True
            self.update_warning_quarter()
            #Event warning
            writer.write_data(self.score, self.quarter, self.clicks, "warning-"+str(self.warning_quarter), not self.button_right.disabled)
        
    def sound_buzzer(self, dt):
        self.play_sound()
        #Buzzer
        
    def play_sound(self):
        if self.sound:
            self.sound.volume = self.warning_alarm_volume ** 3 / 1000000
            self.sound.play()
        pass
        
    def check_if_end(self):
        if (self.score >= self.total_reinforcements):
            self.end_experiment()
            return True
        else: 
            return False


    def turn_feeding_condition_off(self, dt):
               
        if not self.check_if_end():
            self.randomize_array()
            houseLight.activate()
            self.turn_on_screen()
            self.feeding_condition = False
            self.label_right.text = "00"
            self.reset_quarters()
            self.warning_variable = False
            #Event Starting after reinforcement
            writer.write_data(self.score, self.quarter, self.clicks, "starting-again", not self.button_right.disabled)
        pass


    def feed(self):
        if not self.feeding_condition:
            self.feeding_condition = True
            self.turn_off_screen() 
            houseLight.deactivate()
            feeder.activate()
            feeder.create_deactivate_feeder_event(self.feed_time)
            Clock.schedule_once(self.turn_feeding_condition_off, self.feed_time)
            #Event Reinforcement
            writer.write_data(self.score, self.quarter, self.clicks, "reinforcement", not self.button_right.disabled)

    def check_if_punishment(self):
        if self.used_tries > self.warning_pecks:
            self.punish()
    
    def turn_off_screen(self):
        self.rect.source ="assets/images/black_panel.png"
        self.button_right.disable_button()
        self.button_left.disable_button()
        self.button_right_shadow.disable_button_0()
        self.spot.opacity = 0
        self.label_left.opacity = 0
        self.panel_connected_label.opacity = 0.3
        self.label_right.opacity = 0

    def turn_on_screen(self):
        self.rect.source ="assets/images/panel.png"
        self.button_left.enable_button()
        self.button_right_shadow.enable_button()
        self.spot.opacity = 1
        self.label_left.opacity = 1
        self.panel_connected_label.opacity = 1
        self.label_right.opacity = 1

    def punish(self):
        houseLight.deactivate()
        self.buzzer.cancel() 
        self.turn_off_screen()
        self.subsequent_punishments += 1 
        self.button_left.zeroing()
        Clock.schedule_once(self.un_punish, self.punishment_period)
        #Event Punishment
        writer.write_data(self.score, self.quarter, self.clicks, "punishment", not self.button_right.disabled)

    def un_punish(self, dt):
        houseLight.activate()
        self.turn_on_screen()
        self.used_tries = 0
        self.button_right_shadow.enable_button()
        self.label_right.text = "00"
        self.was_warned = True
        self.reset_quarters()
        self.warning_variable = False
        #Event Staring Over
        if self.subsequent_punishments >= self.skip_to_next_value:
            self.randomize_array()
            self.subsequent_punishments = 0

        writer.write_data(self.score, self.quarter, self.clicks, "starting-over", not self.button_right.disabled) 

    def update_score(self):
        self.clicks = self.button_left.button_count
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


    def update_used_tries(self):
        if self.button_right.disabled == False:
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
    
    def __init__(self, my_arg1=None, my_arg2=None, my_arg3=None, my_arg4=None , my_arg5=None , **kwargs):


        self.score_label = "77"
        Clock.schedule_once(self.prepare_buttons, 0.8)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        # USB MONITORING
        self.usb_monitor = USBMonitor()
        self.usb_monitor.start_monitoring(on_connect=self.usb_add_callback, on_disconnect=self.usb_remove_callback)

        self.reset_quarters()
        if my_arg1:
            self.reinforcement_ratio = int(my_arg1)
        if my_arg2:
            self.total_reinforcements = int(my_arg2)
        if my_arg3:
            self.subject = str(my_arg3)

            if self.subject == ERMIS:
                print("Here is ERMIS !!!!!!!!")
                self.button_height = 0.45
            else:
                self.button_height = 0.55 
            
        if my_arg4 == "True":
            self.random_warning = True
            print("T self.random_warning" , self.random_warning)        
        elif my_arg4 == "False":
            self.random_warning = False
            print("F self.random_warning" , self.random_warning)        
        if my_arg5:
            self.warning_alarm_volume= int(my_arg5)
            self.warning_display_volume= int(my_arg5)


        devices_dict = self.usb_monitor.get_available_devices()
        if any(device.split("\\")[1] == "VID_0C45&PID_8419" for device in devices_dict):
            print("Application started with Touch Pannel Connected")
            self.is_panel_connected = True  

            # self.panel_connected_label.text = "Application started with Touch Pannel Connected"
            # self.panel_connected_label.color = [0.2, 0.2, 0.2, 0.2]
        else:
            print("Application started with Touch Pannel DISCONNECTED")
            self.is_panel_connected = False


        #Event Start
        writer.write_data(self.score, self.quarter, 0, "Start", False) 
        super(FloatLayout, self).__init__(**kwargs)
        with self.canvas.before:
            self.rect = Rectangle(source="assets/images/panel.png")
        
        
    
    def on_pos(self, *args):
        # update Rectangle position when MazeSolution position changes
        self.rect.pos = self.pos

    def on_size(self, *args):
        # update Rectangle size when MazeSolution size changes
        self.rect.size = self.size

    def prepare_buttons(self, dt):

        self.randomize_array()

        self.button_left.source = "assets/images/green_light.png"
        self.button_left.source_file = "assets/images/green_light.png"
        self.button_left.source_file_press = "assets/images/green_dark.png"

        self.button_right.source = "assets/images/red_light.png"
        self.button_right.source_file = "assets/images/red_light.png"
        self.button_right.source_file_press = "assets/images/red_dark.png"
        self.button_right.disable_button()
        if self.is_spot_on:
            self.spot.pos_hint = {'center_x':.3, 'center_y':.75}
        else:
            self.spot.pos_hint = {'center_x': 3, 'center_y':.75}

        self.button_right_shadow.source = "assets/images/grey_light.png"
        self.button_right_shadow.source_file = "assets/images/grey_light.png"
        self.button_right_shadow.source_file_press = "assets/images/grey_dark.png"
        houseLight.activate()

    def _keyboard_closed(self):
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):

        if keycode[1] == 'escape':
            houseLight.deactivate()
            App.get_running_app().stop()


        elif keycode[1] == 'spacebar':

            print("spacebar")
            if self.button_right.disabled == True :
                #Event free-food
                writer.write_data(self.score, self.quarter, self.clicks, "free-food", not self.button_right.disabled) 
                self.positive_reinforcement()
            
        elif keycode[1] == 'enter':
            print("enter")
            # Event gratis-red
            writer.write_data(self.score, self.quarter, self.clicks, "gratis-red-"+str(self.warning_quarter), not self.button_right.disabled)
            if self.button_right.disabled == False :
                self.negative_reinforcement()

        return True


    def positive_reinforcement(self):
        self.score = self.score + 1
        self.feed()
        self.subsequent_punishments = 0
        self.button_left.button_count = 0
        self.update_quarter()
        self.update_labels()
        pass

    def negative_reinforcement(self):
        self.button_right.source = self.button_right.source_file
        self.button_right.disable_button()
        self.buzzer.cancel()
        Clock.schedule_once(self.button_right_shadow.enable_button_delayed, 0.2)

class BasicImageButton(ButtonBehavior, Image):

    button_count = 0
    last_seen_outside = datetime.datetime.strptime('26 Aug 2023', '%d %b %Y')

    def on_touch_down(self, touch):
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
        button_radius = float(self.size_hint[0] / 2)       
        aspect_ratio = float(window_x/window_y)

        # touch.sx and touch.sy are the relative coordinates of tfhe touch to the window, between 0 and 1 
        dist_from_center  = distance_from_center(touch.sx, touch.sy, button_center_x, button_center_y, aspect_ratio)
        return  dist_from_center < button_radius
    def touch_close_to_button(self, touch):
        window_x = Window.size[0]
        window_y = Window.size[1]
        button_center_x = self.pos_hint['center_x']
        button_center_y = self.pos_hint['center_y']
        button_radius = float(self.size_hint[0] / 2)       
        aspect_ratio = float(window_x/window_y)

        # touch.sx and touch.sy are the relative coordinates of tfhe touch to the window, between 0 and 1 
        dist_from_center  = distance_from_center(touch.sx, touch.sy, button_center_x, button_center_y, aspect_ratio)
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
            if  not self.disabled and (datetime.datetime.now()-self.last_seen_outside > datetime.timedelta(milliseconds=300)):
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
                writer.write_data(parent.score, parent.quarter, self.button_count, "green", not parent.button_right.disabled)
                parent.update_score()
                self.disabled = False
            else:
                print("INVALID: ", (datetime.datetime.now()-self.last_seen_outside).total_seconds())   
   
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

    def on_touch_up(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            self.button_count = self.button_count + 1
            parent = self.parent
            # Event Red
            writer.write_data(parent.score, parent.quarter, parent.clicks, "red-"+str(parent.warning_quarter), not parent.button_right.disabled) 
            parent.negative_reinforcement()

    def disable_button(self):
        parent = self.parent
        self.disabled = True
        self.opacity= 0
        self.pos_hint = {'center_x': .3, 'center_y':parent.button_height}
            
    def enable_button(self):
        
        parent = self.parent
        self.disabled = False
        self.opacity= (parent.warning_display_volume / 100)
        print(f'self.opacity {self.opacity}')
        print(f'parent.warning_display_volume {parent.warning_display_volume}')
        #Warning Volume
        self.pos_hint = {'center_x':.3, 'center_y':self.button_height}

class BasicImageButtonGrey(BasicImageButton):

    def on_touch_up(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            self.source = self.source_file
            parent = self.parent
            if not parent.warning_variable:
                # Event Before
                writer.write_data(parent.score, parent.quarter, parent.clicks, "before", not parent.button_right.disabled) 
                pass 
            else:    
                # Event After
                writer.write_data(parent.score, parent.quarter, parent.clicks, "after", not parent.button_right.disabled) 
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
    def __init__(self,  my_arg1=None, my_arg2=None, my_arg3=None, my_arg4=None, my_arg5=None, **kwargs):
        self.my_arg1 = my_arg1
        self.my_arg2 = my_arg2
        self.my_arg3 = my_arg3
        self.my_arg4 = my_arg4
        self.my_arg5 = my_arg5

        super(MainApp, self).__init__(**kwargs)

    def build(self):
        Builder.load_file("self_control.kv")
        layout = ExperimentLayout(my_arg1=self.my_arg1, my_arg2=self.my_arg2, my_arg3=self.my_arg3, my_arg4=self.my_arg4, my_arg5=self.my_arg5 )
        return layout

if __name__ == "__main__":
  my_arg1 = sys.argv[1] if len(sys.argv) > 1 else None
  my_arg2 = sys.argv[2] if len(sys.argv) > 2 else None
  my_arg3 = sys.argv[3] if len(sys.argv) > 3 else None
  my_arg4 = sys.argv[4] if len(sys.argv) > 4 else None
  my_arg5 = sys.argv[5] if len(sys.argv) > 5 else None

  feeder = Feeder()
  clicker = Clicker()
  houseLight = HouseLight()
  feeder.deactivate()
  houseLight.activate()
  subject_name = "None" 
  if my_arg3: subject_name = my_arg3 
  writer = Writer(constant_data, subject_name)
  print("my_arg5", my_arg5) 
  mainApp = MainApp(my_arg1, my_arg2, my_arg3, my_arg4, my_arg5)
  mainApp.run()
