CREATE TABLE experiments (
    experiment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reinforcement_ratio INTEGER NOT NULL CHECK (reinforcement_ratio > 0),                                                     -- Integer, not null, greater than zero
    warning_hits INTEGER,                     -- Number of hits
    punishment_duration INTEGER NOT NULL,                 -- Duration of punishment in seconds
    feed_time INTEGER NOT NULL,                         -- Feed time in seconds
    total_reinforcements INTEGER NOT NULL,              -- Total reinforcements given
    consecutive_warnings_limit INTEGER,       -- Skip to next value as an integer
    warning_alarm_volume INTEGER ,     -- Volume of warning alarm
    warning_display_volume INTEGER,   -- Volume of warning display
    subject_id INTEGER NOT NULL REFERENCES subjects(subject_id), -- Foreign key to subjects table
    mode_id INTEGER NOT NULL REFERENCES experiment_modes(mode_id), -- Foreign key to experiment_modes table
    is_spot_on BOOLEAN DEFAULT TRUE,                   -- Flag if spot is on
    punishment_periodicity INTEGER,
    warning_duration INTEGER NOT NULL,                  -- Warning duration in seconds
    time_before_warning_signal INTEGER,        -- Pre-warning time in seconds
    highlight_warning_signal BOOLEAN DEFAULT FALSE,     -- Highlight warning signal
    warning_signal_position INTEGER NOT NULL,    -- Position of the warning signal
    created_at TIMESTAMP DEFAULT NOW(),                 -- Record creation timestamp
    updated_at TIMESTAMP DEFAULT NOW(),                 -- Record update timestamp
    comments TEXT                                       -- Optional comments
);


