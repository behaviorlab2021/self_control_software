from kivy.clock import Clock
from self_control_software.self_control.utils.functions import distance_from
from kivy.core.window import Window
import datetime

from self_control_software.self_control.components.buttons.basic_image_button import BasicImageButton

class BasicImageButtonGreen(BasicImageButton):


    green_button_changed = False
    green_button_scheduled_event = None  # To keep track of the scheduled event
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clicker = None  # Initialize clicker
        self.writer = None  # Initialize writer
        self.injector = None  # Initialize injector

    def set_clicker(self, clicker):
        self.clicker = clicker

    def set_writer(self, writer):
        self.writer = writer

    def set_injector(self, injector):
        self.injector = injector   

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
            self.clicker.click()
            self.disabled = True
            parent = self.parent
            # self.source = self.source_file
            parent.was_warned = False
            self.button_count = self.button_count + 1
            #Event Green
            self.writer.write_data(parent.score, parent.quarter, self.button_count, "green", not parent.button_red.disabled, parent.warning_signal_index)
            self.injector.inject_data(parent.score, parent.quarter, self.button_count, "green", not parent.button_red.disabled, parent.warning_signal_index)
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
