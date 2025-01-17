import sys
import os
import subprocess
import random
import datetime
from kivy.config import Config  # Import the Config module
import asyncio

Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'left', '-1440')
Config.set('graphics', 'fullscreen', 'auto')
import time
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.graphics.vertex_instructions import Rectangle
from kivy.core.audio import SoundLoader
from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID
from self_control_software.self_control.services.house_light import HouseLight
from self_control_software.self_control.services.writer import Writer
from self_control_software.self_control.controllers.postgres_sync_controller import PostgresSyncController
from self_control_software.self_control.services.feeder import Feeder
from self_control_software.self_control.utils.functions import distance_from
from self_control_software.self_control.services.clicker import Clicker
from self_control_software.self_control.utils.subject_names import ERMIS, ADAM, SNIK, MOSES
import threading

session_data = None
subject_name = None

class ExperimentLayout(FloatLayout):
    ending = False
    button_height = 0.6
    button_size = 0.6
    consecutive_warnings = 0
    feeding_condition = False
    score = 0
    used_tries = 0
    is_panel_connected = False
    subsequent_punishments = 0
    clicks = 0
    warning_quarter = -1
    warning_variable = False
    warning_signal_training_running = False
    warning_signal_scheduled_event = None
    un_punish_event = None
    un_feed_event = None
    buzzer_file = "assets/audio/buzzer.mp3"
    buzzer = None
    sound = SoundLoader.load(buzzer_file) 
    canvas_picture = ObjectProperty(None)
    button_green = ObjectProperty(None)
    button_red = ObjectProperty(None)
    label_top_left = ObjectProperty(None)
    label_top_right = ObjectProperty(None)
    label_bottom_left = ObjectProperty(None)
    panel_connected_label = ObjectProperty(None)
    session_ended_label = ObjectProperty(None)
    spot = ObjectProperty(None)
    was_warned = False
    warning_signal_index = -1
    round = 0
    round_id = None
    devices_dict = None
    window_x = None
    window_y = None
    aspect_ratio = None
    touch_start_x = None
    touch_start_y = None
    has_ended = False
    cumulative_record_event = None
    sync_pg_controller = PostgresSyncController()


    def check_if_hopper_training(self, dt):
        if (self.session_data["mode_id"] == 1):
            self.button_green.disable_button()
            pass

    def __init__(self, session_arguments, writer, async_pg_controller, clicker, houseLight, feeder, **kwargs):
        # Use the renamed session_arguments object
        self.session_data = session_arguments
        self.writer = writer  # Store writer as an instance variable
        self.async_pg_controller = async_pg_controller  # Store async_pg_controller as an instance variable
        self.houseLight = houseLight  # Store houseLight as an instance variable
        self.feeder = feeder  # Store feeder as an instance variable
        Window.set_icon('self_control_software/self_control/assets/icons/g220.ico')
        # Clock scheduling
        Clock.schedule_once(self.prepare_buttons, 0.8)
        Clock.schedule_once(self.start_session, 0.8)
        self.cumulative_record_event = Clock.schedule_interval(self.add_cumulative_record, 0.5)        # Keyboard event binding
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        # USB MONITORING
        self.usb_monitor = USBMonitor()
        self.usb_monitor.start_monitoring(on_connect=self.usb_add_callback, on_disconnect=self.usb_remove_callback)
        # USB device check
        self.devices_dict = self.usb_monitor.get_available_devices()
        
        self.window_x = Window.size[0]
        self.window_y = Window.size[1]

        self.async_pg_controller.update_session_window_size(self.session_data["session_id"], self.window_x, self.window_y)

        self.button_size = self.session_data["button_size"]/100
        
        self.aspect_ratio = float(self.window_x/self.window_y)

        # if any(device.split("\\")[1] == "VID_0C45&PID_8419" for device in devices_dict):
        #     print("Application started with Touch Panel Connected")
        #     self.is_panel_connected = True
        # else:
        #     print("Application started with Touch Panel DISCONNECTED")
        #     self.is_panel_connected = False

                # Handle subject-specific logic
                
        # Writer update
        self.writer.writer_update(self.session_data)
        # self.async_pg_controller.async_pg_controller_update(self.session_data)
        # Event Start
        self.writer.write_data(self.score, self.warning_quarter, 0, "Start", False,  -1)
        # Inherit initialization
        super(FloatLayout, self).__init__(**kwargs)
        with self.canvas.before:
            self.rect = Rectangle(source="assets/images/panel.png")
    
    def initial_session_ended_text(self):        
        return ''
        # return 'Session ended ' + ('YES' if self.has_ended
        
    def initial_panel_connected_text(self):
            # self.panel_connected_label.text = "Application started with Touch Pannel DISCONNECTED"
            # self.panel_connected_label.color = [1, 0.2, 0.2, 0.2]
        return ''
        # return 'Touch Pannel started ' + ('CONNECTED' if self.is_panel_connected else 'DISCONNECTED')
    
    def session_grace_radius(self):
        return float(self.session_data["grace_radius"]/100)

    def initial_panel_connected_color(self):
        return [0.2, 0.2, 0.2, 0.2] if self.is_panel_connected  else [1, 0.2, 0.2, 1]
    
    def initial_session_ended_color(self):
        return [0.0, 0.0, 0.0, 0.0]
    
    def update_warning_quarter(self):
        self.warning_quarter = (self.warning_signal_index//( self.session_data["reinforcement_ratio"]/4))+1


    def randomize_array(self):
        if self.session_data["mode_id"] == 4:
            self.warning_signal_index = random.randint(1, self.session_data["reinforcement_ratio"] - self.session_data["warning_hits"] - 1)
            self.update_warning_quarter()
        else:
            self.warning_signal_index = -1

    def on_touch_up(self,touch):
        #Event Touch
        if self.button_green.opacity == 0:
            self.writer.write_peck_data_blind( self.score, self.warning_quarter, self.clicks, touch.sx, touch.sy, "blind-peck", not self.button_red.disabled, self.warning_signal_index)
            self.async_pg_controller.inject_peck(self.touch_start_x, self.touch_start_y, touch.sx, touch.sy, self.rect.source !="assets/images/black_panel.png" , False, not self.button_red.disabled, self.round_id)
        else:
            self.writer.write_peck_data( self.score, self.warning_quarter, self.clicks, touch.sx, touch.sy,  not self.button_red.disabled, self.warning_signal_index)
            self.async_pg_controller.inject_peck(self.touch_start_x, self.touch_start_y, touch.sx, touch.sy, self.rect.source !="assets/images/black_panel.png", not self.button_green.disabled, not self.button_red.disabled, self.round_id)
        if self.session_data["is_spot_on"]:
            self.spot.pos_hint = {'center_x':touch.sx, 'center_y':touch.sy}
        
        return super(FloatLayout, self).on_touch_up(touch)

    def on_touch_down(self,touch):
        if (not self.has_ended):
            self.async_pg_controller.inject_cumulative_record(self.clicks, self.session_data["session_id"])            
        self.touch_start_x = touch.sx
        self.touch_start_y = touch.sy
        return super(FloatLayout, self).on_touch_down(touch)

    def check_reinforcement_condition(self):
        if (self.button_green.button_count >= self.session_data["reinforcement_ratio"]):
            self.positive_reinforcement()

    def end_session(self):
        self.turn_off_screen()
        self.close_last_round()
        self.async_pg_controller.inject_event(self.round_id, "session_end", not self.button_red.disabled, self.clicks)        
        self.houseLight.deactivate()
        print("Deactivating house light")

        #Event End of Session
        self.async_pg_controller.trigger_check_session(self.session_data["session_id"])
        self.async_pg_controller.trigger_session_results(self.session_data["session_id"])
        self.writer.write_data(self.score, self.warning_quarter, self.clicks, "end_of_session", False, self.warning_signal_index)
        self.session_ended_label.text = "Results are being generated. Please wait."
        self.session_ended_label.color = [0.3, 0.2, 0.2, 0.6]
        Clock.unschedule(self.cumulative_record_event)
        threading.Thread(target=self.create_results_pdf, args=(self.after_graceful_end_pdf_creation,)).start()
    
    def terminate_session(self):

        self.feeder.deactivate()
        self.unschedule_all_pending_events()
        print("Terminating session")

        self.turn_off_screen()
        self.close_last_round()
        self.async_pg_controller.inject_event(self.round_id, "session_terminated", not self.button_red.disabled, self.clicks)        
        self.houseLight.deactivate()
        print("Deactivating house light")
        #Event End of Session
        self.async_pg_controller.trigger_check_session(self.session_data["session_id"])
        self.async_pg_controller.trigger_session_results(self.session_data["session_id"])
        self.writer.write_data(self.score, self.warning_quarter, self.clicks, "end_of_session", False, self.warning_signal_index)
        self.session_ended_label.text = "Results are being generated. Please wait."
        self.session_ended_label.color = [0.3, 0.2, 0.2, 0.6]
        threading.Thread(target=self.create_results_pdf, args=(self.after_termination_pdf_creation,)).start()

    def create_results_pdf(self, callback=None):
        print("Creating results PDF!!!")
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        print("Current file path:", current_file_path)
        script_path = os.path.join(current_file_path, '..', '..', 'r_scripts', 'make_and_send.py')
        result = subprocess.run(
            [
                sys.executable,  # Use the current Python interpreter
                script_path,
                self.session_data['session_id']
            ]
        )

        # Print output for debugging
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        if callback:
            callback()
        pass

    def after_termination_pdf_creation(self):
        self.ending = False
        self.has_ended = True
        self.session_ended_label.text = "Session terminated by user."
        self.session_ended_label.color = [0.2, 0.2, 0.2, 0.6]
        print("PDF creation completed. Executing callback function.")
        # Add the code you want to execute after PDF creation here
    def after_graceful_end_pdf_creation(self):
        self.ending = False
        self.has_ended = True
        self.session_ended_label.text = "Session ended gracefully."
        self.session_ended_label.color = [0.2, 0.2, 0.2, 0.6]
        print("PDF creation completed. Executing callback function.")

    def check_if_warning_signal_training(self):
        if self.session_data["mode_id"] == 3 and self.score % self.session_data["punishment_periodicity"] == 0:  
            if self.consecutive_warnings < self.session_data["consecutive_warnings_limit"]:    
                self.warning_signal_training_running = True
                self.warning_signal_scheduled_event = Clock.schedule_once(self.start_warning_signal_training, self.session_data["time_before_warning_signal"])
            else :
                self.consecutive_warnings = 0

    def start_warning_signal_training(self, dt):
        if self.warning_signal_training_running :
            self.consecutive_warnings = self.consecutive_warnings + 1
            self.play_sound()
            if self.session_data["highlight_warning_signal"]:
                self.houseLight.deactivate()  
            self.buzzer = Clock.schedule_interval(self.sound_buzzer, 0.5)
            self.button_red.enable_button()
            self.button_green.disable_button()
            self.warning_signal_scheduled_event = Clock.schedule_once(self.warning_signal_training_punishment, self.session_data["warning_duration"])
            self.writer.write_data(self.score, self.warning_quarter, self.clicks, "warning-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
            self.async_pg_controller.inject_event(self.round_id, "warning", not self.button_red.disabled, self.clicks)
        pass

    def stop_warning_signal_training(self):
        self.houseLight.activate()
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
        if not self.was_warned and self.button_green.button_count == self.warning_signal_index:
            self.play_sound()
            self.buzzer = Clock.schedule_interval(self.sound_buzzer, 0.5)
            self.button_red.enable_button()
            self.was_warned = True
            self.warning_variable = True
            #Event warning
            self.writer.write_data(self.score, self.warning_quarter, self.clicks, "warning-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
            self.async_pg_controller.inject_event(self.round_id, "warning", not self.button_red.disabled, self.clicks)
        
    def sound_buzzer(self, dt):
        self.play_sound()
        #Buzzer
        
    def play_sound(self):
        def play():
            if self.sound:
                self.sound.volume = self.session_data["warning_alarm_volume"] / 100
                self.sound.play()
        threading.Thread(target=play).start()
        pass
        
    def check_if_end(self):
        if (self.score >= self.session_data["total_reinforcements"]):
            self.end_session()
            return True
        else: 
            return False

    def turn_feeding_condition_off(self, dt):
        self.async_pg_controller.inject_event(self.round_id, "feeding_end", not self.button_red.disabled, self.clicks)
        if not self.check_if_end():
            self.check_if_warning_signal_training()
            self.houseLight.activate()
            self.feeding_condition = False
            self.warning_variable = False
            #Event Starting after reinforcement
            self.writer.write_data(self.score, self.warning_quarter, self.clicks, "starting-again", not self.button_red.disabled, self.warning_signal_index)
            self.turn_on_screen()

        pass

    def feed(self):
        if not self.feeding_condition:
            self.writer.write_data(self.score, self.warning_quarter, self.clicks, "feeding", not self.button_red.disabled, self.warning_signal_index)
            self.async_pg_controller.inject_event(self.round_id, "feeding", not self.button_red.disabled, self.clicks)
            self.async_pg_controller.inject_cumulative_record(self.clicks, self.session_data["session_id"])            
            self.button_green.zeroing()
            self.feeding_condition = True
            self.houseLight.deactivate()
            self.feeder.activate()
            self.feeder.create_deactivate_feeder_event(self.session_data["feed_time"])
            self.un_feed_event = Clock.schedule_once(self.turn_feeding_condition_off, self.session_data["feed_time"])
            #Event Reinforcement

            self.turn_off_screen()

    def check_if_punishment(self):
        if self.used_tries > self.session_data["warning_hits"]:
            self.punish()
    
    def turn_off_screen(self):
        print("Turning off screen")
        self.update_button_count()
        self.rect.source ="assets/images/black_panel.png"
        self.button_red.disable_button()
        self.button_green.disable_button()
        self.spot.opacity = 0
        self.panel_connected_label.opacity = 0.3
        self.label_top_left.opacity = 0
        self.label_top_right.opacity = 0
        self.label_bottom_left.opacity = 0
    
    def start_session(self,dt):
        self.turn_on_screen()

    def turn_on_screen(self):
        self.rect.source ="assets/images/panel.png"
        if not self.session_data["mode_id"] == 1:
            self.button_green.enable_button()
        else:
            self.button_green.disable_button()
        # self.button_red_shadow.enable_button()
        self.spot.opacity = 1
        self.panel_connected_label.opacity = 1
        self.label_top_left.opacity = 1
        self.label_top_right.opacity = 1
        self.label_bottom_left.opacity = 1
        if self.round_id: self.close_last_round()
        self.start_new_round()

    def punish(self):

        self.writer.write_data(self.score, self.warning_quarter, self.clicks, "punishment", not self.button_red.disabled, self.warning_signal_index)
        self.async_pg_controller.inject_cumulative_record(self.clicks, self.session_data["session_id"])
        self.async_pg_controller.inject_event(self.round_id, "punishment", not self.button_red.disabled, self.clicks)
        self.houseLight.deactivate()
        self.buzzer.cancel() 
        self.subsequent_punishments += 1 
        self.button_green.zeroing()
        self.un_punish_event = Clock.schedule_once(self.un_punish, self.session_data["punishment_duration"])
        #Event Punishment
        self.turn_off_screen()

    def un_punish(self, dt):
        Clock.unschedule(self.warning_signal_scheduled_event)
        self.stop_warning_signal_training()
        self.check_if_warning_signal_training()
        self.houseLight.activate()
        self.used_tries = 0
        # self.button_red_shadow.enable_button()
        self.was_warned = True
        self.warning_variable = False
        self.async_pg_controller.inject_event(self.round_id, "punishment_end", not self.button_red.disabled, self.clicks)
        self.turn_on_screen()

        #Event Staring Over
        self.writer.write_data(self.score, self.warning_quarter, self.clicks, "starting-over", not self.button_red.disabled, self.warning_signal_index) 

    def update_button_count(self):
        self.clicks = self.button_green.button_count  # Updates the number of clicks the green button has
        self.async_pg_controller.inject_cumulative_record(self.clicks, self.session_data["session_id"])
        self.update_labels() # Updates the labels
        # Update the writer and async_pg_controller
        self.writer.write_data(self.score, self.warning_quarter, self.clicks, "score_updated", not self.button_red.disabled, self.warning_signal_index)
    
    def make_checks(self):
        self.check_if_punishment() # Checks if the punishment condition is met
        self.check_reinforcement_condition() # Checks if the reinforcement condition is met
        self.check_if_red() # Checks if the red button should be enabled
        
    def update_labels(self):
        self.label_top_left.text = str(self.score).zfill(2)
        self.label_top_right.text = str(self.clicks).zfill(2)
        self.label_bottom_left.text = str(self.round - self.score - 1).zfill(2)

    def update_used_tries(self):
        if self.button_red.disabled == False:
            self.used_tries += 1

    def usb_remove_callback(self, device_id, device_info):
        if device_info[ID_VENDOR_ID] == "0c45":
            print(f"{device_info[ID_VENDOR_ID]}")
            self.panel_connected_label.text = "Touch Pannel is DISCONNECTED"
            self.panel_connected_label.color = [1, 0.2, 0.2, 1]
    

    def usb_add_callback(self, device_id, device_info):
        if device_info[ID_VENDOR_ID] == "0c45":
            print(f"{device_info[ID_VENDOR_ID]}")
            self.panel_connected_label.text = "Touch Pannel is RECONNECTED"
            self.panel_connected_label.color = [0.2, 0.2, 0.2, 0.2]
            
    def on_pos(self, *args):
        # update Rectangle position when MazeSolution position changes
        self.rect.pos = self.pos

    def on_size(self, *args):
        # update Rectangle size when MazeSolution size changes
        self.rect.size = self.size

    def prepare_buttons(self, dt):
        self.button_green.source = "assets/images/green_light.png"
        self.button_green.source_file = "assets/images/green_light.png"
        self.button_green.source_file_press = "assets/images/green_dark.png"
        self.button_green.enable_button()
        self.button_red.source = "assets/images/red_light.png"
        self.button_red.source_file = "assets/images/red_light.png"
        self.button_red.source_file_press = "assets/images/red_dark.png"
        self.button_red.disable_button()
        if self.session_data["is_spot_on"]:
            self.spot.pos_hint = {'center_x':.3, 'center_y':.75}
        else:
            self.spot.pos_hint = {'center_x': 3, 'center_y':.75}
        # self.button_red_shadow.source = "assets/images/grey_light.png"
        # self.button_red_shadow.source_file = "assets/images/grey_light.png"
        # self.button_red_shadow.source_file_press = "assets/images/grey_dark.png"
        self.houseLight.activate()

    def _keyboard_closed(self):
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'escape':
            if not self.ending:
                self.turn_off_screen()
                if not self.has_ended:    
                    self.terminate_session()
                else:
                    self.stop_app()


        elif keycode[1] == 'spacebar':
            print("spacebar")
            if self.button_red.disabled == True :
                #Event free-food
                self.writer.write_data(self.score, self.warning_quarter, self.clicks, "free-food", not self.button_red.disabled, self.warning_signal_index) 
                self.async_pg_controller.inject_event(self.round_id, "free_food", not self.button_red.disabled, self.clicks)
                self.positive_reinforcement()
            
        elif keycode[1] == 'enter':
            print("enter")
            # Event gratis-red
            if self.button_red.disabled == False : 
                self.writer.write_data(self.score, self.warning_quarter, self.clicks, "gratis-red-"+str(int(self.warning_quarter)), not self.button_red.disabled, self.warning_signal_index)
                self.async_pg_controller.inject_event(self.round_id, "gratis_red", not self.button_red.disabled, self.clicks)
                self.negative_reinforcement()
                if self.warning_signal_training_running:
                    self.stop_warning_signal_training()
        return True

    def positive_reinforcement(self):
        self.stop_warning_signal_training()
        self.consecutive_warnings = 0
        self.score = self.score + 1
        self.subsequent_punishments = 0
        self.button_green.button_count = 0
        self.feed()
        self.writer.write_data(self.score, self.warning_quarter, self.clicks, "reinforcement", not self.button_red.disabled, self.warning_signal_index)
        pass

    def negative_reinforcement(self):
        self.button_red.source = self.button_red.source_file
        self.button_red.disable_button()
        self.buzzer.cancel()
        # Clock.schedule_once(self.button_red_shadow.enable_button_delayed, 0.2)

    def add_cumulative_record(self, dt):
        self.async_pg_controller.inject_cumulative_record(self.clicks, self.session_data["session_id"])
        pass

    def start_new_round(self):
        print("Starting new round")
        #Increase round by ons
        if self.subsequent_punishments == 0:
            self.randomize_array()
            self.subsequent_punishments = 0
        elif self.subsequent_punishments >= self.session_data["consecutive_warnings_limit"]:
            self.randomize_array()
            self.async_pg_controller.inject_event(self.round_id, "warning_switch", not self.button_red.disabled, self.clicks)
            self.subsequent_punishments = 0
        self.round += 1
        self.update_button_count()
        #Inject the new round in the database
        new_round = not self.round_id
        self.round_id = self.sync_pg_controller.inject_round_data(self.session_data["session_id"], self.round, self.warning_signal_index, self.warning_quarter, self.score)
        
        print("Round ID IS:", self.round_id, "SESSION ID IS:", self.session_data["session_id"])
        if new_round:
            self.async_pg_controller.inject_event(self.round_id, "session_start", not self.button_red.disabled, self.clicks)
        self.async_pg_controller.inject_event(self.round_id, "new_round", not self.button_red.disabled, self.clicks)
        pass

    def close_last_round(self):
        self.async_pg_controller.inject_event(self.round_id, "round_end", not self.button_red.disabled, self.clicks)
        self.async_pg_controller.trigger_check_round(self.round_id)
        self.async_pg_controller.trigger_round_results(self.round_id)
        pass
    def stop_app(self):
        # Run the stop_async_tasks coroutine and then stop the app
        asyncio.run(self.stop_async_tasks())
        App.get_running_app().stop()
        
    async def stop_async_tasks(self):
        # Cancel all running asyncio tasks
        tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    def unschedule_all_pending_events(self):
        Clock.unschedule(self.button_green.green_button_scheduled_event) if self.button_green.green_button_scheduled_event else None
        Clock.unschedule(self.button_red.red_button_scheduled_event) if self.button_red.red_button_scheduled_event else None
        Clock.unschedule(self.warning_signal_scheduled_event) if self.warning_signal_scheduled_event else None
        Clock.unschedule(self.cumulative_record_event) if self.cumulative_record_event else None
        Clock.unschedule(self.un_punish_event) if self.un_punish_event else None
        Clock.unschedule(self.un_feed_event) if self.un_feed_event else None
        self.buzzer.cancel()
