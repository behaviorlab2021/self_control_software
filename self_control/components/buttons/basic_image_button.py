from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
import datetime
from self_control_software.self_control.utils.functions import distance_from, is_within_ellipse
from self_control_software.self_control.services.clicker import Clicker
from self_control_software.self_control.services.writer import Writer

class BasicImageButton(ButtonBehavior, Image):

    button_count = 0
    last_seen_outside = datetime.datetime.strptime('26 Aug 2023', '%d %b %Y')
    touch_start_x = None
    touch_start_y = None
    grace_radius = 0
    
    def __init__(self, **kwargs):
        super(BasicImageButton, self).__init__(**kwargs)
        self.grace_radius = kwargs.get('grace_radius', 0)

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

        aspect_ratio = float(Window.size[0] / Window.size[1])
        center_x_norm = self.pos_hint['center_x']
        center_y_norm = self.pos_hint['center_y']
        radius_norm = float(self.size_hint[0] / 2) 
        # touch.sx and touch.sy are the relative coordinates of tfhe touch to the window, between 0 and 1 
        return  is_within_ellipse(touch.sx, touch.sy, center_x_norm, center_y_norm, radius_norm + self.grace_radius, aspect_ratio)
  
    
    def touch_close_to_button(self, touch):
        aspect_ratio = float(Window.size[0] / Window.size[1])
        center_x_norm = self.pos_hint['center_x']
        center_y_norm = self.pos_hint['center_y']
        radius_norm = float(self.size_hint[0] / 2) 

        # touch.sx and touch.sy are the relative coordinates of tfhe touch to the window, between 0 and 1 
        return  is_within_ellipse(touch.sx, touch.sy, center_x_norm, center_y_norm, radius_norm + radius_norm/3, aspect_ratio)