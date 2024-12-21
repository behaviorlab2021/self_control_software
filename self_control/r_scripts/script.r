library(DBI)

dsn_database = "postgres"   # Specify the name of your Database
# Specify host name e.g.:"aws-us-east-1-portal.4.dblayer.com"
dsn_hostname = "localhost"  
dsn_port = "5432"                # Specify your port number. e.g. 98939
dsn_uid = "postgres"         # Specify your username. e.g. "admin"
dsn_pwd = "pigeon123!"        # Specify your password. e.g. "xxx"

# Ensure you have an active database connection:
tryCatch({
  conn <- dbConnect(
    RPostgres::Postgres(),
    dbname = dsn_database,
    host = dsn_hostname,
    port = dsn_port,
    user = dsn_uid,
    password = dsn_pwd
  )
  cat("Connected successfully!\n")
}, error = function(e) {
  cat("Error: ", e$message, "\n")
})

# Query the database to get the subjects table 
subjects <- dbGetQuery(conn, "SELECT * FROM subjects;")

# Query the database to get the sessions table
sessions <- dbGetQuery(conn, "SELECT * FROM sessions WHERE session_id = ''d798207f-5fc4-4c07-ac95-c70310549c2a'';")

# Get the subject_id from the sessions table
subject_id <- sessions$subject_id

# Console log the subject_id
cat("Subject ID: ", subject_id, "\n")

# Find the subject name in the subjects table
subject_name <- subjects[subjects$subject_id == subject_id, "subject_name"]
cat("Subject Name: ", subject_name, "\n")