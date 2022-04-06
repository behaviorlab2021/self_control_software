from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window

class MyApp(App):
   
   def build(self):
       
     window_sizes=Window.size[1]
     
     return Label(text="screen sizes= "+str(window_sizes))

MyApp().run()