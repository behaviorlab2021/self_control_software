library(mailR) # Add this line to load mailR library

# Ensure JAVA_HOME is set correctly
Sys.setenv(JAVA_HOME = "/path/to/your/java/home")

args <- commandArgs(trailingOnly = TRUE)
report_path <- args[1]
cumulative_record_path <- args[2]

sender <- Sys.getenv("EMAIL_USER")
password <- Sys.getenv("EMAIL_PASSWORD")
recipients <- strsplit(Sys.getenv("EMAIL_RECIPIENTS"), ",")[[1]]  # Get recipients from environment variable
subject_name <- "Lab Results"  # Modify as needed
current_date <- Sys.Date()

send.mail(from = sender,
          to = recipients,
          subject = paste("Lab Results for ", subject_name, current_date),
          body = "Please find the attached files.",
          smtp = list(host.name = "smtp.gmail.com", port = 465,
                      user.name = sender,            
                      passwd = password, ssl = TRUE),
          authenticate = TRUE,
          attach.files = c(report_path, cumulative_record_path),
          send = TRUE)