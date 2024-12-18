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
from self_control_software.self_control.services.injector import Injector

from self_control_software.self_control.main import MainApp


if __name__ == "__main__":
    # Expecting a JSON string as the first argument from the command line
    session_id = sys.argv[1]

    db = ExperimentDB()
    db.connect()

    session = db.find_session_by_id(session_id)
    session_dict = dict(session)  # Convert RealDictRow to a regular dictionary

    
    subject_id = session['subject_id']
    subject = db.find_subject_by_id(subject_id)
    subject_name = subject['subject_name']
    
    db.close()

    feeder = Feeder()
    clicker = Clicker()
    houseLight = HouseLight()
    feeder.deactivate()
    houseLight.activate()

    writer = Writer(session_dict, subject_name)
    injector = Injector(session_dict)
    
    # Pass the session_arguments object to the main application
    mainApp = MainApp(session_arguments=session_dict, feeder=feeder, clicker=clicker, houseLight=houseLight, writer=writer, injector=injector)
    mainApp.run()
    sys.exit()  # Ensure the script terminates properly