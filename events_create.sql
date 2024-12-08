CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,                 -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(), -- Time of the event
    reinforcers INTEGER NOT NULL,                -- Number of reinforcers
    quarter INTEGER NOT NULL,                    -- Quarter of the session or event
    pecks INTEGER NOT NULL,                      -- Number of pecks
    event_type VARCHAR(50) NOT NULL,             -- Type of event (e.g., "stimulus", "response")
    x_pos DECIMAL(10, 5) NOT NULL,               -- X-coordinate position
    y_pos DECIMAL(10, 5) NOT NULL,               -- Y-coordinate position
    warning_present BOOLEAN DEFAULT FALSE        -- Whether a warning was present
);


INSERT INTO experiments (
    reinforcement_ratio, warning_signal_points, warning_pecks, punishment_period, 
    feed_time, total_reinforcements, skip_to_next_value, warning_alarm_volume, 
    warning_display_volume, punishment_condition, subject, is_spot_on, 
    random_warning, miliseconds_after_touch, in_warning_signal_training, 
    rounds_before_warning, warning_duration, 
    time_before_warning_signal, highlight_warning_signal, warning_signal_position, 
    comments
) VALUES (
    60, 0, 3, 60, 
    30, 60, 3, 0.5, 
    0.5, 1, 'Adam', TRUE, 
    TRUE, 500, TRUE, 
    1, 5, 
    10, TRUE, 0.3, 
    'Test experiment'
);