import os
import sys

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Append the parent directory of the script directory to sys.path
sys.path.append(os.path.abspath(os.path.join(script_dir, '../..')))

print("PATH IS THIS:", sys.path, "LEN:", len(sys.path))

from self_control.services.postgres import ExperimentDB

from self_control.utils.serializer import datetime_serializer
import subprocess
import os
import time
from datetime import datetime

def check_rscript():
    """Check if Rscript is available in the system PATH."""
    result = subprocess.run(['Rscript', '--version'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Warning: Rscript is not found in the system PATH. Please ensure R is installed and Rscript is accessible.")

def generate_file_name(experiment_date, subject_name, suffix):
    return f"{experiment_date}_{subject_name}_{suffix}"

def send_email(report_path, cumulative_record_path, subject_name, session_date):
    mail_result = subprocess.run(
        [
            'Rscript',
            os.path.join(script_dir, 'send_mail.R'),  # Make path relative
            report_path,
            cumulative_record_path,
            subject_name,  # Add this argument
            session_date  # Add this argument
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
        mode_id = session_info['mode_id']
        return subject_name, experiment_date, mode_id
    finally:
        db.close()

def main(session_id):
    check_rscript()  # Check if Rscript is available
    subject_name, experiment_date, mode_id = get_experiment_details(session_id)
    output_dir = os.path.join(script_dir, "../data")  # Specify the output directory

    print("Mode ID:", mode_id)

    report_file_name = generate_file_name(experiment_date, subject_name, "report.pdf")
    cumulative_record_file_name = generate_file_name(experiment_date, subject_name, "cumulative_record.pdf")

    result = subprocess.run(
        [
            'Rscript',
            '-e',
            f"rmarkdown::render(r'{os.path.join(script_dir, f'mode_{str(mode_id)}_session_results.Rmd')}', params = list(session_id = '{session_id}'), output_file = r'{os.path.join(output_dir, report_file_name)}')"
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
            os.path.join(script_dir, 'cumulative_record.R'),  # Make path relative
            session_id,
            output_dir,
            cumulative_record_file_name
        ],
        capture_output=True,
        text=True
    )

    def on_files_created():
        print(f"Files have been created: {os.path.join(output_dir, report_file_name)} and {os.path.join(output_dir, cumulative_record_file_name)}")

    # Check if the files were created successfully
    report_path = os.path.join(output_dir, report_file_name)
    cumulative_record_path = os.path.join(output_dir, cumulative_record_file_name)

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
            send_email(report_path, cumulative_record_path, subject_name, experiment_date)  # Pass new arguments
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