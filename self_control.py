from ast import Pass
from xml.dom.pulldom import parseString
from kivy.uix.behaviors import ButtonBehavior  
from kivy.uix.image import Image  
from kivy.lang import Builder    
from kivy.uix.floatlayout import FloatLayout  
import kivy
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from experiment import Experiment
from feeder import Feeder
from functions import distance_from_center
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.graphics.vertex_instructions import Rectangle

Window.fullscreen = True
# Window.show_cursor = False

Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

phase_time = 15

class ExperimentLayout(FloatLayout):

    reinforcement_ratio = 60
    warning_signal_points = []
    feeding_condition = False
    warning_period = 3
    punishment_period = 30

    feed_time = 3
    end_score = 28

    score_label = StringProperty()
    score = 0
    used_tries = 0
    clicks_label = StringProperty()
    
    phase = 1 

    canvas_picture = ObjectProperty(None)
    button_left = ObjectProperty(None)
    button_right = ObjectProperty(None)
    label_left = ObjectProperty(None)
    label_right = ObjectProperty(None)
    
    was_warned = False

    def calculate_score(self):

        if (self.button_left.button_count >= self.reinforcement_ratio):
            self.score = self.score + 1
            self.feed()
            self.button_left.button_count = 0

    def end_experiment(self):
        self.button_left.disable_button()
        self.button_right.disable_button()
        pass

    def check_if_red(self):
        if not self.was_warned and self.button_left.button_count in self.warning_signal_points:
            self.button_right.enable_button()
            self.button_right_shadow.disable_button()
            self.was_warned = True
        pass

    def check_if_end(self):
        if (self.score >= self.end_score):
            self.end_experiment()
        pass


    def turn_feeding_condition_off(self, dt):
        self.feeding_condition = False
       
        pass


    def feed(self):
        if not self.feeding_condition:
            self.feeding_condition = True
            feeder.activate()
            feeder.create_deactivate_feeder_event(self.feed_time)
            Clock.schedule_once(self.turn_feeding_condition_off, self.feed_time+1)
             

    def change_case(self, dt):
        pass

    def check_if_punishment(self):

        if self.used_tries > self.warning_period:
            self.punish()
    
    def punish(self):

        self.rect.source ="assets/images/punishment_panel.png"
        self.button_right.disable_button()
        self.button_left.disable_button()
        self.label_left.opacity = 0
        self.label_right.opacity = 0
        Clock.schedule_once(self.un_punish, self.punishment_period)
        pass

    def un_punish(self, dt):
        self.rect.source ="assets/images/panel.png"
        self.button_left.enable_button()
        self.label_left.opacity = 1
        self.label_right.opacity = 1
        self.used_tries = 0
        self.button_left.zeroing()
        self.button_right_shadow.enable_button()
        self.label_right.text = "00"
        self.was_warned = True 

    def update_score(self):
        self.clicks = self.button_left.button_count
        self.update_used_tries()
        self.check_if_punishment()
        self.check_if_red()
        self.calculate_score()
        self.score_label = str(self.score).zfill(2)
        self.clicks_label = str(self.clicks).zfill(2)
        self.label_right.text = self.clicks_label
        self.label_left.text = self.score_label
        self.check_if_end()
    
    def update_used_tries(self):
        if self.button_right.opacity == 1:
            self.used_tries += 1
        else:   
            self.used_tries = 0

    def __init__(self, **kwargs):
        self.score_label = "00"
        Clock.schedule_once(self.prepare_buttons, 0.8)
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



        self.button_left.source = "assets/images/green_light.png"
        self.button_left.source_file = "assets/images/green_light.png"
        self.button_left.source_file_press = "assets/images/green_dark.png"
        self.button_right.source = "assets/images/red_light.png"
        self.button_right.source_file = "assets/images/red_light.png"
        self.button_right.source_file_press = "assets/images/red_dark.png"
        self.button_right.disable_button()
        
        self.button_right_shadow.source = "assets/images/grey_light.png"
        self.button_right_shadow.source_file = "assets/images/grey_light.png"
        self.button_right_shadow.source_file_press = "assets/images/grey_dark.png"
        

class BasicImageButton(ButtonBehavior, Image):

    button_count = 0

    def on_press(self):
        self.button_count = self.button_count + 1
        # self.parent.ids.label.text ...
        self.source = self.source_file_press
        
    
    def on_release(self):
        self.source = self.source_file
    
    def disable_button(self):
        self.disabled = True
        self.opacity= 0
    
    def enable_button(self):
        self.disabled = False
        self.opacity= 1

class BasicImageButtonLeft(BasicImageButton):

    def on_release(self):
        self.source = self.source_file
        parent = self.parent
        parent.was_warned = False
        parent.update_score()

    def zeroing(self):
        self.button_count = 0

class BasicImageButtonRight(BasicImageButton):

    def on_release(self):
        self.source = self.source_file
        self.disable_button()
        self.parent.button_right_shadow.enable_button()
    
    def disable_button(self):
        self.disabled = True
        self.opacity= 0
        self.pos_hint = {'center_x': 2, 'center_y':.75}
            
    def enable_button(self):
        self.disabled = False
        self.opacity= 1
        self.pos_hint = {'center_x':.7, 'center_y':.75}

class BasicImageButtonGrey(BasicImageButton):
    
    def disable_button(self):
        self.disabled = True
        self.opacity= 0
        self.pos_hint = {'center_x':2, 'center_y':.75}
            
    def enable_button(self):
        self.disabled = False
        self.opacity= 1
        self.pos_hint = {'center_x':.7, 'center_y':.75}

class MainApp(App):

    def __init__(self, **kwargs):

        self.load_kv("self_control.kv")
        self.layout = ExperimentLayout()
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        return self.layout

if __name__ == "__main__":
  feeder = Feeder()
  mainApp = MainApp()
  mainApp.run()