from ast import Pass
from logging import warning
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
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from numpy import True_
from experiment import Experiment
from feeder import Feeder
from functions import distance_from_center
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.graphics.vertex_instructions import Rectangle
import random
import time
import os

Window.fullscreen = True
Window.show_cursor = False

Config.set('input', 'mouse', 'mouse, multitouch_on_demand')

constant_data =  {
    'reinforcement_ratio' :10,
    'warning_signal_points' :[],
    'warning_pecks' :3,
    'punishment_period' :3,
    'feed_time' :3,
    'total_reinforcements' :28,
    'take_a_break_from_punishment' :3,
    'warning_alarm_volume' : 90,
    'warning_display_volume' :20,
    'punishment_condition' :1,
    'subject' :"",
    'is_spot_on' :True,
    'random_warning' :True,
}

class ExperimentLayout(FloatLayout):

    reinforcement_ratio = constant_data["reinforcement_ratio"]
    warning_signal_points = constant_data['warning_signal_points']
    warning_pecks = constant_data["warning_pecks"]
    punishment_period = constant_data["punishment_period"]
    feed_time = constant_data["feed_time"]
    total_reinforcements = constant_data["total_reinforcements"]
    take_a_break_from_punishment = constant_data["take_a_break_from_punishment"]
    warning_alarm_volume = constant_data["warning_alarm_volume"]
    warning_display_volume = constant_data["warning_display_volume"]
    punishment_condition = constant_data["punishment_condition"]
    subject = constant_data["subject"]
    is_spot_on = constant_data["is_spot_on"]
    random_warning = constant_data["random_warning"]

    feeding_condition = False
    score = 0
    used_tries = 0
    clicks_label = StringProperty()
    score_label = StringProperty()
    subsequent_punishments = 0
    clicks = 0
    quarter = 1
    warning_quarter = 0
    warning_variable = False



    buzzer_file = "assets/audio/buzzer.mp3"

    canvas_picture = ObjectProperty(None)
    button_left = ObjectProperty(None)
    button_right = ObjectProperty(None)
    label_left = ObjectProperty(None)
    label_right = ObjectProperty(None)
    button_right_shadow = ObjectProperty(None)
    spot = ObjectProperty(None)

    was_warned = False

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
            writer.write_peck_data_blind( self.score, self.quarter, self.clicks, touch.sx, touch.sy, "blind-peck")
        else:
            writer.write_peck_data( self.score, self.quarter, self.clicks, touch.sx, touch.sy)

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
        writer.write_data(self.score, self.quarter, self.clicks, "end_of_experiment")

        pass

    def check_if_red(self):
        if not self.was_warned and self.button_left.button_count in self.warning_signal_points and self.subsequent_punishments < self.take_a_break_from_punishment:

            os.system("mpg321 -g " + str(self.warning_alarm_volume) + " " + self.buzzer_file)
            self.buzzer = Clock.schedule_interval(self.sound_buzzer, 0.5)
            self.button_right.enable_button()
            self.button_right_shadow.disable_button_100()
            self.was_warned = True
            self.warning_variable = True
            self.update_warning_quarter()
            #Event warning
            writer.write_data(self.score, self.quarter, self.clicks, "warning-"+str(self.warning_quarter))

        
    def sound_buzzer(self, dt):
        #Buzzer
        os.system("mpg321 -g " + str(self.warning_alarm_volume) + " " + self.buzzer_file)

 

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
            writer.write_data(self.score, self.quarter, self.clicks, "starting-again")
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
            writer.write_data(self.score, self.quarter, self.clicks, "reinforcement")

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
        self.label_right.opacity = 0

    def turn_on_screen(self):
        self.rect.source ="assets/images/panel.png"
        self.button_left.enable_button()
        self.button_right_shadow.enable_button()
        self.spot.opacity = 1
        self.label_left.opacity = 1
        self.label_right.opacity = 1

    def punish(self):
        houseLight.deactivate()
        self.buzzer.cancel() 
        self.turn_off_screen()
        self.subsequent_punishments += 1 
        self.button_left.zeroing()
        Clock.schedule_once(self.un_punish, self.punishment_period)
        #Event Punishment
        writer.write_data(self.score, self.quarter, self.clicks, "punishment")

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
        writer.write_data(self.score, self.quarter, self.clicks, "starting-over") 

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

    def __init__(self, **kwargs):
        self.score_label = "00"
        Clock.schedule_once(self.prepare_buttons, 0.8)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.reset_quarters()
        self.warning_variable = False
        #Event Start
        writer.write_data(self.score, self.quarter, 0, "Start") 

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
                writer.write_data(self.score, self.quarter, self.clicks, "free-food") 
                self.positive_reinforcement()
            

            
        elif keycode[1] == 'enter':
            print("enter")
            # Event gratis-red
            writer.write_data(self.score, self.quarter, self.clicks, "gratis-red-"+str(self.warning_quarter))
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
        self.button_right_shadow.enable_button()

class BasicImageButton(ButtonBehavior, Image):

    button_count = 0

    def on_touch_down(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            self.button_count = self.button_count + 1
            # self.parent.ids.label.text ...
            self.source = self.source_file_press
            
    def on_touch_up(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            self.source = self.source_file
    
    def disable_button(self):
        self.disabled = True
        self.opacity= 0
    
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

class BasicImageButtonLeft(BasicImageButton):

    def on_touch_up(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            parent = self.parent
            self.source = self.source_file
            parent.was_warned = False

            #Event Green
            writer.write_data(parent.score, parent.quarter, self.button_count, "green")
            
            parent.update_score()


    def zeroing(self):
        self.button_count = 0

class BasicImageButtonRight(BasicImageButton):

    def on_touch_up(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            parent = self.parent
            # Event Red
            writer.write_data(parent.score, parent.quarter, parent.clicks, "red-"+str(parent.warning_quarter)) 
            parent.negative_reinforcement()

    def disable_button(self):
        self.disabled = True
        self.opacity= 0
        self.pos_hint = {'center_x': .7, 'center_y':.75}
            
    def enable_button(self):
        parent = self.parent
        self.disabled = False
        self.opacity= (parent.warning_display_volume / 100)
        print(f'self.opacity {self.opacity}')
        print(f'parent.warning_display_volume {parent.warning_display_volume}')
        #Warning Volume
        self.pos_hint = {'center_x':.7, 'center_y':.75}

class BasicImageButtonGrey(BasicImageButton):

    def on_touch_up(self, touch):
        if self.touch_on_button(touch) and not self.disabled:
            self.source = self.source_file
            parent = self.parent
            if not parent.warning_variable:
                # Event Before
                writer.write_data(parent.score, parent.quarter, parent.clicks, "before") 
                pass 
            else:    
                # Event After
                writer.write_data(parent.score, parent.quarter, parent.clicks, "after") 
                pass


    def disable_button_100(self):
        self.disabled = True
        #Warning Volume
        self.opacity= 1
        self.pos_hint = {'center_x':.7, 'center_y':.75}

            
    def disable_button_0(self):
        self.disabled = True
        #Warning Volume
        self.opacity= 0
        self.pos_hint = {'center_x':.7, 'center_y':.75}

    def enable_button(self):
        self.disabled = False
        #Warning Volume
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
  houseLight = HouseLight()
  writer = Writer(constant_data)
  mainApp = MainApp()
  mainApp.run()


