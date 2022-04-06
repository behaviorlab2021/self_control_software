from ast import Pass
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

Window.fullscreen = True
# Window.show_cursor = False

Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

phase_time = 15

class ExperimentLayout(FloatLayout):

    reinforcement_ratio = 10
    feeding_condition = False
    feed_time = 3
    end_score = 28

    score_label = StringProperty()
    score = 0
    clicks_label = StringProperty()
    
    phase = 1 

    button_left = ObjectProperty(None)
    button_right = ObjectProperty(None)
    label_left = ObjectProperty(None)
    label_right = ObjectProperty(None)
    
    def calculate_score(self):

        if (self.button_left.button_count >= self.reinforcement_ratio):
            self.score = self.score + 1
            self.feed()
            self.button_left.button_count = 0

        pass

    def check_if_end(self):
        if (self.score >= self.end_score and not self.feeding_condition):
            App. get_running_app().stop()
        pass


    def turn_feeding_condition_off(self, dt):
        self.feeding_condition = False
        self.check_if_end()
        pass


    def feed(self):
        if self.feeding_condition:
            pass
        else: 
            self.feeding_condition = True
            feeder.activate()
            feeder.create_deactivate_feeder_event(self.feed_time)
            Clock.schedule_once(self.turn_feeding_condition_off, self.feed_time+1)
            pass 
        pass

    def change_case(self, dt):
        pass


    def update_score(self, dt):
        self.clicks = self.button_left.button_count
        self.calculate_score()
        self.score_label = str(self.score).zfill(2)
        self.clicks_label = str(self.clicks).zfill(2)
        self.label_right.text = self.score_label
        self.label_left.text = self.clicks_label
        

    def __init__(self, **kwargs):
        self.score_label = "00"

        Clock.schedule_once(self.prepare_buttons, 0.8)
        Clock.schedule_interval(self.update_score, 0.1)

        super(FloatLayout, self).__init__(**kwargs)

    def prepare_buttons(self, dt):

        self.button_left.source = "assets/images/green_light.png"
        self.button_left.source_file = "assets/images/green_light.png"
        self.button_left.source_file_press = "assets/images/green_dark.png"

        self.button_right.source = "assets/images/no_button.png"
        self.button_right.source_file = "assets/images/no_button.png"
        self.button_right.source_file_press = "assets/images/no_button.png"
        
        pass

    pass

class BasicImageButton(ButtonBehavior, Image):

    button_count = 0

    def on_press(self):

        self.button_count = self.button_count + 1
        # self.parent.ids.label.text ...
        self.source = self.source_file_press
    
    def on_release(self):
        self.source = self.source_file

class BasicImageButtonLeft(BasicImageButton):

    
    pass


class BasicImageButtonRight(BasicImageButton):

    pass


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