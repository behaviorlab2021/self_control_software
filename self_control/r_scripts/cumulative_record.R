library(DBI)
library(dotenv)

# Get command-line arguments
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("Usage: Rscript cumulative_record.R <session_id> <output_dir> <output_name>")
}

session_id <- args[1]
output_dir <- args[2]
output_name <- args[3]

curve_pdf_name <- paste0(output_dir, "/", output_name)

# Determine the script directory
args_full <- commandArgs(trailingOnly = FALSE)
script_path <- sub("--file=", "", args_full[grep("--file=", args_full)])
if (length(script_path) == 0) {
  script_dir <- getwd()
} else {
  script_dir <- dirname(normalizePath(script_path))
}
cat("Script directory:", script_dir, "\n")
setwd(script_dir)
cat("Current working directory:", getwd(), "\n")

env_file <- "../.env"
cat("Environment file path:", env_file, "\n")
if (!file.exists(env_file)) {
  stop(paste("Error: .env file does not exist at", env_file))
}
cat("Loading environment variables from", env_file, "\n")
suppressWarnings(dotenv::load_dot_env(env_file))

dsn_database <- Sys.getenv("DB_NAME")
dsn_hostname <- Sys.getenv("DB_HOST")
dsn_port <- Sys.getenv("DB_PORT")
dsn_uid <- Sys.getenv("DB_USER")
dsn_pwd <- Sys.getenv("DB_PASSWORD")

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

cat("Fetching session details...\n")
session_details <- dbGetQuery(conn, paste0("
  SELECT 
    subject_name,
    created_at
  FROM sessions 
  JOIN subjects ON sessions.subject_id = subjects.subject_id
  JOIN experiment_modes ON sessions.mode_id = experiment_modes.mode_id
  WHERE session_id = '", session_id, "';"))
cat("Session details fetched.\n")

# Convert created_at to Date class
session_details$created_at <- as.Date(session_details$created_at)

cat("Fetching cumulative record...\n")
cumulative_record <- dbGetQuery(conn, paste0("
SELECT * FROM cumulative_record
WHERE session_id = '", session_id, "'
ORDER BY event_time DESC;"))
cat("Cumulative record fetched.\n")

cat("Fetching events...\n")
events <- dbGetQuery(conn, paste0("
SELECT event_time, event_type, hit_count
FROM events e
JOIN rounds r ON e.round_id = r.round_id
WHERE r.session_id = '", session_id, "'
ORDER BY event_time;"))
cat("Events fetched.\n")

# Ensure event_time is numeric
cumulative_record$event_time <- as.numeric(cumulative_record$event_time)

# Calculate elapsed time in seconds from the start
start_time <- min(cumulative_record$event_time, na.rm = TRUE)
cumulative_record$elapsed_time <- cumulative_record$event_time - start_time

# Define a function to convert seconds to "mm:ss" format
seconds_to_mmss <- function(seconds) {
  minutes <- floor(seconds / 60)
  secs <- seconds %% 60
  sprintf("%02d:%02d", minutes, secs)
}

# Calculate the range of the 'elapsed_time' variable
time_range <- max(cumulative_record$elapsed_time, na.rm = TRUE) - min(cumulative_record$elapsed_time, na.rm = TRUE)
print(paste("time range, ", time_range))

# Set dynamic width based on the range of 'elapsed_time', with a scaling factor
scaling_factor <- 0.05  # Adjust this scaling factor as needed for proportionality
dynamic_width <- time_range * scaling_factor
print(paste("time dynamic_width, ", dynamic_width))

# Ensure a minimum width to avoid too narrow plots
min_width <- 12  # Set a minimum width for the PDF
dynamic_width <- max(dynamic_width, min_width)

# Set the fixed height for the PDF and the figure
pdf_height <- 5  # Increase the overall height for the legend
figure_height <- 4  # Height for the figure itself

cat("Output directory:", output_dir, "\n")

# Ensure the output directory exists
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

cat("Generating curve PDF:", curve_pdf_name, "\n")

# Define event properties
event_properties <- list(
  "feeding" = list(symbol = 16, color = "blue"),  # Changed from "feeding"
  "red" = list(symbol = 16, color = "red"),  # Changed from "red"
  "warning" = list(symbol = 1, color = "red"),
  "punishment" = list(symbol = 16, color = "black"),
  "new_round" = list(symbol = 124, color = "blue"),
  "session_start" = list(symbol = 8, color = "blue"),
  "session_end" = list(symbol = 8, color = "purple"),
  "session_terminated" = list(symbol = 8, color = "red")
)

# Open a PDF device to save the plot
pdf(curve_pdf_name, width = dynamic_width, height = pdf_height)  # Change the file name and path as needed

# Set up the layout to allocate space for the legend
layout(matrix(c(1, 2), nrow = 2), heights = c(figure_height, 1))  # Allocate space for the legend

# Plot the data without the default x-axis (xaxt = "n")
par(mar = c(5, 4, 4, 2) + 0.1)  # Adjust margins for the plot
plot(cumulative_record$elapsed_time, cumulative_record$hit_count, type = "l", col = "black",
     xlab = "Time from start (mm:ss)", 
     ylab = "Cumulative Events",
     main = "Cumulative Record",
     lwd = 2, xaxt = "n")  # Suppress the x-axis

# Add points for each event type
for (event_type in names(event_properties)) {
  event_data <- events[events$event_type == event_type, ]
  points(event_data$event_time - start_time, event_data$hit_count,
         pch = event_properties[[event_type]]$symbol,
         col = event_properties[[event_type]]$color)
}

# Define x-axis ticks at 1-minute intervals (60 seconds)
x_ticks <- seq(0, max(cumulative_record$elapsed_time, na.rm = TRUE), by = 60)  # Ticks every 1 minute

# Convert x-axis ticks to "mm:ss" format
x_labels <- seconds_to_mmss(x_ticks)
# Add custom x-axis with formatted labels
axis(1, at = x_ticks, labels = x_labels, las = 2)  # Rotate labels 90 degrees

# Add legend below the plot
par(mar = c(0, 0, 0, 0))  # Adjust margins for the legend
plot.new()
legend("center", legend = c("reinforcement", "termination", "warning", "punishment", "new_round", "session_start", "session_end", "session_terminated"), 
       pch = sapply(event_properties, function(x) x$symbol), 
       col = sapply(event_properties, function(x) x$color), 
       horiz = TRUE, bty = "o")  # Add box around the legend

# Close the PDF device to save the plot with the legend
dev.off()
