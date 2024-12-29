
library(mailR)
sender <- Sys.getenv("EMAIL_USER")
password <- Sys.getenv("EMAIL_PASSWORD")
recipients <- c("smanoliadis@gmail.com")

send.mail(from = sender,
          to = recipients,
          subject = paste("Lab Results for ", subject_name, current_date),
          body = "Please find the attached file.",
          smtp = list(host.name = "smtp.gmail.com", port = 465, 
                      user.name = sender,            
                      passwd = password, ssl = TRUE),
          authenticate = TRUE,
          send = TRUE,
          )  # Add the path to your file here
