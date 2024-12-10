from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
import datetime
from self_control_software.self_control.utils.functions import distance_from
from self_control_software.self_control.services.clicker import Clicker
from self_control_software.self_control.services.writer import Writer
from self_control_software.self_control.services.injector import Injector

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

