import sys
from self_control.services.postgres import ExperimentDB
from self_control.utils.serializer import datetime_serializer

if __name__ == "__main__":
    experiment_id = sys.argv[1]
    print("experiment_id is:", experiment_id)
    
    db = ExperimentDB()
    db.connect()
    
    experiment = db.find_experiment_by_id(experiment_id)
    experiment_dict = dict(experiment)  # Convert RealDictRow to a regular dictionary
    print("Experiment dict:", experiment_dict)
    print("Experiment highlight_warning_signal:", experiment_dict['highlight_warning_signal'])
    
    subject_id = experiment['subject_id']
    subject = db.find_subject_by_id(subject_id)
    print("Subject name:", subject['subject_name'])
    
    db.close()