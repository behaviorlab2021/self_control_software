import subprocess
import os
from dotenv import load_dotenv  # Add this import

# Load environment variables from the .env file
load_dotenv('self_control_software/self_control/.env')  # Specify the path to your .env file

def run_rmd(rmd_path, session_id):
    """Run the Rmd file to generate output."""
    command = ['Rscript', '-e', f'rmarkdown::render("{rmd_path}", params=list(session_id="{session_id}"))']
    subprocess.run(command, check=True)

def send_email(subject, body, to_email, attachment_path):
    """Send email with the Rmd output attached using mailR."""
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender or not password:
        raise ValueError("EMAIL_USER and EMAIL_PASSWORD environment variables must be set")

    print(f"Sending email to {to_email} with attachment {attachment_path}")
    print(f"Sender: {sender}")
    
    # Construct the R script command to send email using mailR
    r_script = f"""
    library(mailR)
    send.mail(from = "{sender}",
              to = "{to_email}",
              subject = "{subject}",
              body = "{body}",
              smtp = list(host.name = "smtp.gmail.com", port = 465, 
                          user.name = "{sender}",            
                          passwd = "{password}", ssl = TRUE),
              authenticate = TRUE,
              send = TRUE,
              attach.files = "{attachment_path}")
    """
    
    # Run the R script
    command = ['Rscript', '-e', r_script]
    subprocess.run(command, check=True)

def on_subprocess_complete():
    """Run Rmd and send the result via email."""
    rmd_file = "self_control_software/self_control/r_scripts/session_results.Rmd"
    session_id = 'd798207f-5fc4-4c07-ac95-c70310549c2a'  # Example session_id, replace with actual value
    
    # Run the Rmd file
    run_rmd(rmd_file, session_id)
    
    # Assume the output file is saved as output.pdf (adjust as needed)
    output_file = "self_control_software/self_control/r_scripts/session_results.pdf"
    
    # Send the email with the result
    send_email(
        subject="R Markdown Output",
        body="Please find the R Markdown output attached.",
        to_email="smanoliadis@gmail.com",
        attachment_path=output_file
    )

if __name__ == "__main__":
    # Call the function that will run the Rmd and send the result via email
    on_subprocess_complete()
