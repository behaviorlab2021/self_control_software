from house_light import HouseLight  
from feeder import Feeder
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder    
from kivy.clock import Clock
from kivy.config import Config  # Import the Config module
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'left', '-1440')
Config.set('graphics', 'fullscreen', 'auto')
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.vertex_instructions import Rectangle

import sys
class TrainingLayout(FloatLayout):

    def __init__(self, my_arg1=None, my_arg2=None,**kwargs):

        self.my_arg1 =  my_arg1
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        if my_arg1:
            self.reinforcement_ratio = int(my_arg1)
        if my_arg2:
            self.subject = my_arg2
        super(FloatLayout, self).__init__(**kwargs)
        with self.canvas.before:
            self.rect = Rectangle(source="c:/Users/SKINNER BOX/Documents/self_control_software/assets/images/panel.png", size=self.size, pos=self.pos)
            
    def on_pos(self, *args):
        # update Rectangle position when MazeSolution position changes
        self.rect.pos = self.pos

    def on_size(self, *args):
        # update Rectangle size when MazeSolution size changes
        self.rect.size = self.size


    def turn_off_screen(self):
        self.rect.source ="c:/Users/SKINNER BOX/Documents/self_control_software/assets/images/black_panel.png"

    def turn_on_screen(self):
        self.rect.source ="c:/Users/SKINNER BOX/Documents/self_control_software/assets/images/panel.png"

    def _keyboard_closed(self):
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):

        if keycode[1] == 'escape':
            houseLight.deactivate()
            feeder.deactivate()
            App.get_running_app().stop()


        elif keycode[1] == 'spacebar':


          self.turn_off_screen()
          if feeder.switch(): 
            houseLight.deactivate()
            self.turn_off_screen() 

          else:
            houseLight.activate()
            self.turn_on_screen() 



        return True

class TrainingApp(App):
    def __init__(self,  my_arg1=None, my_arg2=None, **kwargs):
        self.my_arg1 = my_arg1
        self.my_arg2 = my_arg2
        super(TrainingApp, self).__init__(**kwargs)

    def build(self):
        Builder.load_file("hopper_training.kv")
        layout = TrainingLayout(my_arg1=self.my_arg1, my_arg2=self.my_arg2)
        return layout

if __name__ == "__main__":
  my_arg1 = sys.argv[1] if len(sys.argv) > 1 else None
  my_arg2 = sys.argv[2] if len(sys.argv) > 2 else None
  feeder = Feeder()
  houseLight = HouseLight()
  feeder.deactivate()
  houseLight.activate()
  subject_name = "None" 
  if my_arg2: subject_name = my_arg2 
  mainApp = TrainingApp(my_arg1, my_arg2)
  mainApp.run()
