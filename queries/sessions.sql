CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reinforcement_ratio INTEGER NOT NULL CHECK (reinforcement_ratio > 0),                                                     -- Integer, not null, greater than zero
    warning_hits INTEGER,                                           -- Number of hits
    punishment_duration INTEGER NOT NULL,                           -- Duration of punishment in seconds
    feed_time INTEGER NOT NULL,                                     -- Feed time in seconds
    total_reinforcements INTEGER NOT NULL,                          -- Total reinforcements given
    consecutive_warnings_limit INTEGER,                             -- Skip to next value as an integer
    warning_alarm_volume INTEGER ,                                  -- Volume of warning alarm
    warning_display_volume INTEGER,                                 -- Volume of warning display
    subject_id INTEGER NOT NULL REFERENCES subjects(subject_id),    -- Foreign key to subjects table
    mode_id INTEGER NOT NULL REFERENCES experiment_modes(mode_id),  -- Foreign key to experiment_modes table
    is_spot_on BOOLEAN DEFAULT TRUE,                    -- Flag if spot is on
    punishment_periodicity INTEGER,
    warning_duration INTEGER NOT NULL,                  -- Warning duration in seconds
    time_before_warning_signal INTEGER,                 -- Pre-warning time in seconds
    highlight_warning_signal BOOLEAN,                   -- Highlight warning signal
    warning_signal_position INTEGER NOT NULL,           -- Position of the warning signal
    button_height INTEGER NOT NULL,                     -- Height of the button
    created_at TIMESTAMP DEFAULT NOW(),                 -- Record creation timestamp
    updated_at TIMESTAMP DEFAULT NOW(),                 -- Record update timestamp
    comments TEXT                                       -- Optional comments
);


INSERT INTO sessions (
    reinforcement_ratio,
    warning_hits,
    punishment_duration,
    feed_time,
    total_reinforcements,
    consecutive_warnings_limit,
    warning_alarm_volume,
    warning_display_volume,
    subject_id,
    mode_id,
    is_spot_on,
    rounds_before_warning,
    warning_duration,
    time_before_warning_signal,
    highlight_warning_signal,
    warning_signal_position,
    comments
) VALUES (
    10,                -- reinforcement_ratio
    3,                 -- warning_hits
    60,                -- punishment_duration (in seconds)
    120,               -- feed_time (in seconds)
    15,                -- total_reinforcements
    1,                 -- consecutive_warnings_limit
    0.75,              -- warning_alarm_volume
    0.80,              -- warning_display_volume
    1,                 -- subject_id (example value)
    1,                 -- mode_id (example value)
    TRUE,              -- is_spot_on
    10,                -- rounds_before_warning
    30,                -- warning_duration (in seconds)
    10,                -- time_before_warning_signal (in seconds)
    TRUE,              -- highlight_warning_signal
    2.34567,           -- warning_signal_position
    'First experiment run' -- comments
);

SELECT *
FROM sessions
ORDER BY created_at DESC
LIMIT 1;
