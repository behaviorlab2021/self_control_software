import sys
sys.path.append('/Users/stammanol/Documents/code/MY_APPS/skinner_box/self_control_software')  # Add this line to include the module path
from self_control.services.postgres import ExperimentDB
from self_control.utils.serializer import datetime_serializer
import subprocess
import os
import time
from datetime import datetime

def generate_file_name(experiment_date, subject_name, suffix):
    return f"{experiment_date}_{subject_name}_{suffix}"

def send_email(report_path, cumulative_record_path):
    mail_result = subprocess.run(
        [
            'Rscript',
            'self_control_software/self_control/r_scripts/send_mail.R',
            report_path,
            cumulative_record_path
        ],
        capture_output=True,
        text=True
    )
    print("Mail STDOUT:", mail_result.stdout)
    print("Mail STDERR:", mail_result.stderr)

def get_experiment_details(session_id):
    db = ExperimentDB()
    db.connect()
    try:
        session_info = db.get_session_basic_info(session_id)
        if session_info is None:
            raise ValueError(f"No session found with ID {session_id}")
        subject_name = session_info['subject_name']
        experiment_date = session_info['experiment_date'].strftime('%Y.%m.%d_%H.%M.%S')
        return subject_name, experiment_date
    finally:
        db.close()

def main(session_id):
    subject_name, experiment_date = get_experiment_details(session_id)
    output_dir = "../data"  # Specify the output directory

    report_file_name = generate_file_name(experiment_date, subject_name, "report.pdf")
    cumulative_record_file_name = generate_file_name(experiment_date, subject_name, "cumulative_record.pdf")

    result = subprocess.run(
        [
            'Rscript',
            '-e',
            f"rmarkdown::render('self_control_software/self_control/r_scripts/session_results.Rmd', params = list(session_id = '{session_id}'), output_file = '{output_dir}/{report_file_name}')"
        ],
        capture_output=True,
        text=True
    )

    # Print output for debugging
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    # Run cumulative_record.R
    cumulative_result = subprocess.run(
        [
            'Rscript',
            'self_control_software/self_control/r_scripts/cumulative_record.R',
            session_id,
            output_dir,
            cumulative_record_file_name
        ],
        capture_output=True,
        text=True
    )

    def on_files_created():
        print(f"Files have been created: {output_dir}/{report_file_name} and {output_dir}/{cumulative_record_file_name}")

    # Check if the files were created successfully
    absolute_output_dir = '/Users/stammanol/Documents/code/MY_APPS/skinner_box/self_control_software/self_control/data'

    report_path = f"{absolute_output_dir}/{report_file_name}"
    cumulative_record_path = f"{absolute_output_dir}/{cumulative_record_file_name}"


    def wait_for_files(paths, timeout=60):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if all(os.path.exists(path) for path in paths):
                return True
            time.sleep(1)
        return False

    try:
        if wait_for_files([report_path, cumulative_record_path]):
            on_files_created()
            time.sleep(1)
            send_email(report_path, cumulative_record_path)
        else:
            print("Error: One or both files were not created within the timeout period.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_and_send.py <session_id>")
        sys.exit(1)
    
    session_id = sys.argv[1]
    
    main(session_id)