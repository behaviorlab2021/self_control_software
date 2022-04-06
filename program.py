from kivy.uix.behaviors import ButtonBehavior  
from kivy.uix.image import Image  
from kivy.lang import Builder    
from kivy.uix.floatlayout import FloatLayout  
import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from experiment import Experiment
from feeder import Feeder
from functions import distance_from_center
from kivy.uix.widget import Widget
from kivy.properties import StringProperty


Window.fullscreen = True
# Window.show_cursor = False

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class ImageButton(ButtonBehavior, Image):

    def __init__(self, **kwargs):
        self.is_active = True
        self.counter = 0
        print("In init....")
        
        super(ImageButton, self).__init__(**kwargs)

        Clock.schedule_once(self.update_button, 0.5)
        Clock.schedule_interval(experiment.change_case, experiment.case_change_time)
        Clock.schedule_interval(self.update_button, experiment.case_change_time)


    def on_touch_down(self, touch):
        if self.touch_on_button(touch):
            self.change_button_color(experiment.button_image_dark)
            Clock.schedule_once(self.update_button, 0.1)
            if feeder.is_active or not experiment.feeding_condition:
                # todo: write "extra" position data...
                pass
            else: 
                experiment.increase_btn_count()
                if experiment.check_condition():
                    experiment.increase_score_count()
                    feeder.activate()
                    feeder.create_deactivate_feeder_event(experiment.feed_time)
                pass              
        else:
            # todo: write "miss" position data...
            # print("miss")
            pass


    
    def change_button_color(self, image_source):
        self.source = image_source
    
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
    

    def update_button(self, dt):
        self.change_button_color(experiment.button_image_light)

class MyFloatLayout(FloatLayout):
    score = StringProperty()
    def __init__(self, **kwargs):
        self.score = "00"
        self.schedule_score_update()
        super(FloatLayout, self).__init__(**kwargs)

    def update_score(self, dt):
        self.score = str(experiment.score_counter).zfill(2)

    def schedule_score_update(self):
        Clock.schedule_interval(self.update_score, 0.5)


class MainApp(App):

    def __init__(self, **kwargs):
        self.load_kv("program.kv")
        self.layout = MyFloatLayout()
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        return self.layout

if __name__ == "__main__":
  feeder = Feeder()
  experiment = Experiment()
  mainApp = MainApp()
  mainApp.run()
