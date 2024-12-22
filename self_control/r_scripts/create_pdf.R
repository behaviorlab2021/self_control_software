# Load required libraries
library(grDevices)

# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Access the string argument
string_arg <- args[1]
cat("String argument:", string_arg, "\n")

# Create the directory path for the PDF file
output_dir <- "../data/"  # Relative path to store the PDF

# Ensure the directory exists (create it if it doesn't)
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
  cat("Created directory:", output_dir, "\n")
} else {
  cat("Directory already exists:", output_dir, "\n")
}

library(ggplot2)
library(lubridate)
library(dplyr)
library(readr)
library(stringr)   # For str_detect
library(ggplot2)
library(qpdf) 
library(grid)
library(gridExtra)
library(tidyr)


file_name <- string_arg
file_path <- paste0(output_dir, file_name)
cat("Reading data from file:", file_path, "\n")
data <- read.csv(file_path)
cat("Data read successfully. Number of rows:", nrow(data), "\n")

data$Time <- hms(data$Time)
subject_name <- data$subject[1]
current_date <- Sys.Date()

pdf_name  <- paste(strsplit(file_path, split = ".csv"),".pdf", sep = "")
curve_pdf_name <- paste(strsplit(file_path, split = ".csv"),"_curve.pdf", sep = "")
stats_pdf_name <- paste(strsplit(file_path, split=".csv"), "_stats.pdf", sep="")
table_pdf_name <- paste(strsplit(file_path, split = ".csv"),"_table.pdf", sep = "")

df <- data %>% 
  select(Reinforcers,Time, Event) %>%
  distinct(Reinforcers, Event) %>%
  filter(str_detect(Event,"red") | str_detect(Event,"warning") ) %>%
  mutate(Event = str_replace(Event, "red-", "Warning Signal Eliminated in Quarter no.")) %>%
  mutate(Event = str_replace(Event, "warning-0", "Warning Signal Presented in Quarter no.1")) %>%
  count(Event)

cat("Generating stats PDF:", stats_pdf_name, "\n")
pdf(stats_pdf_name, height=2, width=4)
# Create the table without row numbering
table_plot <- tableGrob(df, rows = NULL)  # Set rows = NULL to remove row numbers
grid.draw(table_plot)
dev.off()

end_time <- data[data$Event == "end_of_experiment", ][1, ]
start_time <- data[data$Event == "green", ][1, ]

print(paste("end time",end_time$Time))
print(paste("start time",start_time$Time))

# Check if "end of experiment" exists and get the first occurrence
if (any(grepl("end_of_experiment", data$Event))) {
  # Get the first "end of experiment" time if there are multiple
  data <- data[data$Time <= end_time$Time, ]
  print(paste("Dim data after 1"))
  print(dim(data))
}

# Define a function to convert seconds to "mm:ss" format
seconds_to_mmss <- function(seconds) {
  minutes <- floor(seconds / 60)
  secs <- seconds %% 60
  sprintf("%02d:%02d", minutes, secs)
}

data$Time <- as.numeric(data$Time)

# Calculate the range of the 'Time' variable
time_range <- max(data$Time, na.rm = TRUE) - min(data$Time, na.rm = TRUE)

print(paste("time range, ", time_range))

# Set dynamic width based on the range of 'Time', with a scaling factor
scaling_factor <- 0.01  # Adjust this scaling factor as needed for proportionality
dynamic_width <- time_range * scaling_factor

# Ensure a minimum width to avoid too narrow plots
min_width <- 6  # Set a minimum width for the PDF

dynamic_width <- max(dynamic_width, min_width)
print(paste("time dynamic_width, ", dynamic_width))

# Set the fixed height for the PDF
pdf_height <- 4

cat("Generating curve PDF:", curve_pdf_name, "\n")
# Open a PDF device to save the plot
pdf(curve_pdf_name, width = dynamic_width, height = pdf_height)  # Change the file name and path as needed

# Plot the data without the default x-axis (xaxt = "n")
line = data %>% filter(Event != "score_updated")

plot(line$Time, line$hit_count, type = "l", col = "black",
     xlab = "Time (mm:ss)", ylab = "Cumulative Events",
     main = "Cumulative Record",
     lwd = 2, xaxt = "n")  # Suppress the x-axis

# Define x-axis ticks at 5-minute intervals (300 seconds)
x_ticks <- seq(0, max(data$Time, na.rm = TRUE), by = 300)  # Ticks every 5 minutes

# Convert x-axis ticks to "mm:ss" format
x_labels <- seconds_to_mmss(x_ticks)
print(x_ticks)
# Add custom x-axis with formatted labels
axis(1, at = x_ticks, labels = x_labels)

punishment = data[data$Event == "punishment",]
feeding = data[data$Event == "feeding",]
warning = data[grepl("^warning", data$Event), ]
red = data[grepl("^red-", data$Event), ]

points(punishment$Time, punishment$hit_count, pch = 16, col = "red")  # pch = 16 for solid circle
points(feeding$Time, feeding$hit_count, pch = 12, col = "blue")  # pch = 12 for square
points(warning$Time, warning$hit_count, pch = 1, col = "red")  # pch = 1 for circle
points(red$Time, red$hit_count, pch = 2, col = "red")  # pch = 1 for circle

# Close the PDF device to save the plot
dev.off()

# Step 2: Filter rows where the event is "peck", "green", and events starting with "red-"
peck_events <- data %>%
  filter(Event == "peck")

green_events <- data %>%
  filter(Event == "green")

# Count events starting with "red-"
red_events <- data %>%
  filter(str_detect(Event, "^red-"))

# Step 3: Group by reinforcers and count peck, green, and red events
peck_counts_per_reinforcer <- peck_events %>%
  group_by(Reinforcers) %>%
  summarise(Peck_Counts = n(), .groups = 'drop')

green_counts_per_reinforcer <- green_events %>%
  group_by(Reinforcers) %>%
  summarise(Green_Counts = n(), .groups = 'drop')

red_counts_per_reinforcer <- red_events %>%
  group_by(Reinforcers) %>%
  summarise(Red_Counts = n(), .groups = 'drop')

# Step 4: Merge the counts by Reinforcers
reinforcer_summary <- peck_counts_per_reinforcer %>%
  left_join(green_counts_per_reinforcer, by = "Reinforcers") %>%
  left_join(red_counts_per_reinforcer, by = "Reinforcers")

# Replace NA values with 0 for Red_Counts
reinforcer_summary$Red_Counts[is.na(reinforcer_summary$Red_Counts)] <- 0

# Step 5: Add a column for the ratio of reinforcers to hit_count with rounded decimals
reinforcer_summary <- reinforcer_summary %>%
  mutate(Ratio_Reinforcers_to_Pecks = ifelse(Peck_Counts > 0, 
                                             round((Green_Counts) / Peck_Counts, 2), 
                                             NA))

# Step 6: Calculate Sum and Mean for Summary Row
sum_red_counts <- sum(reinforcer_summary$Red_Counts, na.rm = TRUE)
mean_ratio <- round(mean(reinforcer_summary$Ratio_Reinforcers_to_Pecks, na.rm = TRUE), 2)

# Add a summary row to the data frame
summary_row <- data.frame(
  Reinforcers = as.numeric(NA),  # Ensure the type matches the original data frame
  Peck_Counts = NA,
  Green_Counts = NA,
  Red_Counts = sum_red_counts,
  Ratio_Reinforcers_to_Pecks = mean_ratio
)

# Append the summary row to the reinforcer_summary data frame
reinforcer_summary <- bind_rows(reinforcer_summary, summary_row)

# Step 7: Set dynamic page size based on the number of rows
row_count <- nrow(reinforcer_summary)
page_height <- max(6, row_count * 0.3)  # Adjust page height based on rows
page_width <- 8  # You can adjust width similarly if needed

cat("Generating table PDF:", table_pdf_name, "\n")
# Step 8: Export the table to a PDF with dynamic size
pdf(table_pdf_name, width = page_width, height = page_height)

# Create the table without row numbering
table_plot <- tableGrob(reinforcer_summary, rows = NULL)  # Set rows = NULL to remove row numbers
grid.draw(table_plot)

# Close the PDF
dev.off()

cat("Combining PDFs into:", pdf_name, "\n")
# qpdf::pdf_combine(c(stats_pdf_name, curve_pdf_name), pdf_name)
qpdf::pdf_combine(input = c(stats_pdf_name, curve_pdf_name, table_pdf_name),
                  output = pdf_name)

cat("Removing temporary PDFs\n")
file.remove(curve_pdf_name)
file.remove(table_pdf_name)
file.remove(stats_pdf_name)

cat("Sending email with attachment:", pdf_name, "\n")
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
          attach.files = pdf_name
          )  # Add the path to your file here
