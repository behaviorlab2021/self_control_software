library(mailR) # Add this line to load mailR library

# Ensure JAVA_HOME is set correctly
Sys.setenv(JAVA_HOME = "/path/to/your/java/home")

args <- commandArgs(trailingOnly = TRUE)
report_path <- args[1]
cumulative_record_path <- args[2]
subject_name <- args[3]  # Add this line to get subject_name from arguments
session_date <- args[4]  # Add this line to get session_date from arguments

sender <- Sys.getenv("EMAIL_USER")
password <- Sys.getenv("EMAIL_PASSWORD")
recipients <- strsplit(Sys.getenv("EMAIL_RECIPIENTS"), ",")[[1]]  # Get recipients from environment variable

cat("Sending email...", subject_name, session_date, "\n")

send.mail(from = sender,
          to = recipients,
          subject = paste("Lab Results for", subject_name, "on", session_date),
          body = "Please find the attached files.",
          smtp = list(host.name = "smtp.gmail.com", port = 465,
                      user.name = sender,            
                      passwd = password, ssl = TRUE),
          authenticate = TRUE,
          attach.files = c(report_path, cumulative_record_path),
          send = TRUE)