from house_light import HouseLight  
from feeder import Feeder

class MainApp(App):
    def __init__(self,  my_arg1=None, my_arg2=None, **kwargs):
        self.my_arg1 = my_arg1
        self.my_arg2 = my_arg2
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        Builder.load_file("self_control.kv")
        layout = ExperimentLayout(my_arg1=self.my_arg1, my_arg2=self.my_arg2)
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
  writer = Writer(constant_data, subject_name)
  mainApp = TrainingApp(my_arg1, my_arg2)
  mainApp.run()
