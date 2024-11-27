CREATE TABLE experiments (
    experiment_id SERIAL PRIMARY KEY,                    -- Unique experiment identifier
    reinforcement_ratio INTEGER NOT NULL CHECK (reinforcement_ratio > 0), 
                                                        -- Integer, not null, greater than zero
    warning_signal_points INTEGER NOT NULL,             -- Number of signal points
    warning_pecks INTEGER NOT NULL,                     -- Number of pecks
    punishment_period INTEGER NOT NULL,                 -- Duration of punishment in seconds
    feed_time INTEGER NOT NULL,                         -- Feed time in seconds
    total_reinforcements INTEGER NOT NULL,              -- Total reinforcements given
    skip_to_next_value INTEGER DEFAULT 0,               -- Skip to next value as an integer
    warning_alarm_volume DECIMAL(5, 2) DEFAULT 0.5,     -- Volume of warning alarm
    warning_display_volume DECIMAL(5, 2) DEFAULT 0.5,   -- Volume of warning display
    punishment_condition INTEGER NOT NULL DEFAULT 0,    -- Punishment condition as an integer
    subject VARCHAR(50) NOT NULL,                       -- Subject identifier
    is_spot_on BOOLEAN DEFAULT FALSE,                   -- Flag if spot is on
    random_warning BOOLEAN DEFAULT FALSE,               -- Random warning signal flag
    miliseconds_after_touch INTEGER NOT NULL,           -- Reaction time in milliseconds
    in_warning_signal_training BOOLEAN DEFAULT FALSE,   -- If training in warning signal
    regular_rounds_before_warning_signal_training INTEGER NOT NULL,
    warning_duration INTEGER NOT NULL,                  -- Warning duration in seconds
    time_before_warning_signal INTEGER NOT NULL,        -- Pre-warning time in seconds
    highlight_warning_signal BOOLEAN DEFAULT FALSE,     -- Highlight warning signal
    warning_signal_position DECIMAL(10, 5) NOT NULL,    -- Position of the warning signal
    created_at TIMESTAMP DEFAULT NOW(),                 -- Record creation timestamp
    updated_at TIMESTAMP DEFAULT NOW(),                 -- Record update timestamp
    comments TEXT                                       -- Optional comments
);
