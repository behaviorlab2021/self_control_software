import sys
import os

# Add the parent directory of self_control_software to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from self_control_software.self_control.services.postgres import ExperimentDB
from self_control_software.self_control.services.feeder import Feeder
from self_control_software.self_control.services.clicker import Clicker
from self_control_software.self_control.services.house_light import HouseLight  
from self_control_software.self_control.services.writer import Writer
from self_control_software.self_control.main import MainApp


if __name__ == "__main__":
    # Expecting a JSON string as the first argument from the command line
    experiment_id = sys.argv[1]

    db = ExperimentDB(dbname='postgres', user='postgres', password='pigeon123!')
    db.connect()

    experiment = db.find_experiment_by_id(experiment_id)
    experiment_dict = dict(experiment)  # Convert RealDictRow to a regular dictionary

    
    subject_id = experiment['subject_id']
    subject = db.find_subject_by_id(subject_id)
    subject_name = subject['subject_name']
    
    db.close()

    feeder = Feeder()
    clicker = Clicker()
    houseLight = HouseLight()
    feeder.deactivate()
    houseLight.activate()

    writer = Writer(experiment_dict, subject_name)
    
    # Pass the experiment_arguments object to the main application
    mainApp = MainApp(experiment_arguments=experiment_dict, feeder=feeder, clicker=clicker, houseLight=houseLight, writer=writer)
    mainApp.run()