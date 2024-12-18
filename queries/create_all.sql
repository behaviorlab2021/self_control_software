CREATE TABLE experiment_modes (
    mode_id SERIAL PRIMARY KEY,
    mode_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE subjects (
    subject_id SERIAL PRIMARY KEY,
    subject_name VARCHAR(255) NOT NULL UNIQUE
);


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

CREATE TABLE cumulative_record (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),          -- Time of the event
    hit_count INTEGER,                                    -- Number of hit_count
    session_id UUID REFERENCES sessions(session_id) -- Foreign key to experiments table
);

CREATE TABLE rounds (
    session_id UUID REFERENCES sessions(session_id),
    round_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    round_index INTEGER NOT NULL,
    warning_index INTEGER NOT NULL,
    warning_quarter INTEGER NOT NULL,
    reinforcers_count INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE events (
    round_id UUID REFERENCES rounds(round_id),              -- Round Index
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),   -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),            -- Time of the event
    event_type VARCHAR(50) NOT NULL,                        -- Type of event (e.g., "stimulus", "response")
    warning_signal_present BOOLEAN NOT NULL                 -- Whether a warning signal was present
);

-- Create pecks table
CREATE TABLE pecks (
    peck_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    x_pos INTEGER NOT NULL,
    y_pos INTEGER NOT NULL,
    screen_on BOOLEAN NOT NULL,
    peck_time TIMESTAMP NOT NULL DEFAULT NOW(),
    round_id UUID REFERENCES rounds(round_id)
);



CREATE TABLE round_tests (
    round_test_id UUID PRIMARY KEY,
    round_id UUID REFERENCES rounds(round_id),
    green_number_accurate BOOLEAN,
    red_number_accurate BOOLEAN,
    valid_green_clicks_equal_hits BOOLEAN,
    valid_red_clicks_equal_warning_terminations BOOLEAN,
    punishment_time_valid BOOLEAN,
    feeding_time_valid BOOLEAN,
    clicks_until_reinforcement BOOLEAN,
    clicks_until_warning BOOLEAN,
    accurate_punishment_time BOOLEAN,
    accurate_feeding_time BOOLEAN
);



CREATE TABLE session_tests (
    session_test_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    green_number_accurate BOOLEAN,
    red_number_accurate BOOLEAN,
    valid_green_clicks_equal_hits BOOLEAN,
    valid_red_clicks_equal_warning_terminations BOOLEAN,
    punishment_time_valid BOOLEAN,
    feeding_time_valid BOOLEAN,
    clicks_until_reinforcement BOOLEAN,
    clicks_until_warning BOOLEAN,
    accurate_punishment_time BOOLEAN,
    accurate_feeding_time BOOLEAN,
    total_reinforcements_test BOOLEAN,
    total_warnings_test BOOLEAN
);


INSERT INTO subjects (subject_name, subject_id)
VALUES 
    ('Adam', 1),
    ('Moses', 2),
    ('Snik', 3),
    ('Ermis', 4);


INSERT INTO experiment_modes (mode_name, mode_id) VALUES
('HOPPER TRAINING', 1),
('SHEDULE TRAINING', 2),
('WARNING TRAINING', 3),
('RANDOM WARNING', 4);

