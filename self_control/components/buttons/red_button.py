from kivy.uix.behaviors import ButtonBehavior  
from kivy.uix.image import Image  
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty
import datetime
from self_control_software.self_control.components.buttons.basic_image_button import BasicImageButton
from self_control_software.self_control.utils.functions import distance_from

class BasicImageButtonRed(BasicImageButton):

    red_button_changed = False
    red_button_scheduled_event = None  # To keep track of the scheduled event

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

    def on_touch_up(self, touch):
        window_x = Window.size[0]
        window_y = Window.size[1]
        aspect_ratio = float(window_x/window_y)
        if self.touch_start_x:
            slide = distance_from(self.touch_start_x, self.touch_start_y, touch.sx, touch.sy)
            if slide>0.05:
                print("Feather", slide , datetime.datetime.now())
                return
            else: 
                if self.touch_on_button(touch) and not self.disabled:
                    # if  not self.disabled and (datetime.datetime.now()-self.last_seen_outside > datetime.timedelta(milliseconds=300)):
                        
                    if not self.red_button_changed:
                        self.red_button_changed = True
                        self.source = self.source_file_press
                    
                    else:
                        self.red_button_changed = True
                        Clock.unschedule(self.red_button_scheduled_event)
        
                    self.red_button_scheduled_event = Clock.schedule_once(self.change_button_image, .3)
                    self.clicker.click()
                    self.button_count = self.button_count + 1
                    parent = self.parent

                    # Event Red
                    self.writer.write_data(parent.score, parent.warning_quarter, parent.clicks, "red-"+str(int(parent.warning_quarter)), not parent.button_red.disabled, parent.warning_signal_index) 
                    self.injector.inject_event(parent.round_id, "red", True)
                    parent.used_tries = 0

                    parent.negative_reinforcement()
                    if parent.warning_signal_training_running: 
                        parent.stop_warning_signal_training()
                    # else:
                    #     pass
        
                # else:
                #     if self.touch_close_to_button(touch):
                #         pass
                #     else:
                #         self.last_seen_outside = datetime.datetime.now()

    def disable_button(self):
        parent = self.parent
        self.disabled = True
        self.opacity= 0
        self.pos_hint = self.calculate_warning_signal_position(parent)
            
    def enable_button(self):
        
        parent = self.parent
        self.disabled = False
        self.opacity= (parent.session_data["warning_display_volume"] / 100)
        #Warning Volume
        self.pos_hint = self.calculate_warning_signal_position(parent)

    def calculate_warning_signal_position(self, parent):
        return {'center_x':0.3 + parent.session_data["warning_signal_position"]/100*0.4, 'center_y':parent.session_data["button_height"] / 100}
        
        