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
    x_pos FLOAT NOT NULL,
    y_pos FLOAT NOT NULL,
    screen_on BOOLEAN NOT NULL,
    green_on BOOLEAN NOT NULL,
    red_on BOOLEAN NOT NULL,
    peck_time TIMESTAMP NOT NULL DEFAULT NOW(),
    round_id UUID REFERENCES rounds(round_id) NOT NULL
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

-- Index for JOIN
CREATE INDEX idx_events_round_id ON events(round_id);
CREATE INDEX idx_rounds_round_id ON rounds(round_id);

-- Index for Subquery Sorting
CREATE INDEX idx_rounds_started_at ON rounds(started_at);

-- Index for Filtering
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_warning_signal_present ON events(warning_signal_present);

-- Composite Index for Filtering
CREATE INDEX idx_events_round_event_type ON events(round_id, event_type);

CREATE TABLE round_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID UNIQUE REFERENCES rounds(round_id),
    warning_terminated BOOLEAN,
    result_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE OR REPLACE FUNCTION insert_round_results(p_round_id UUID) RETURNS VOID AS $$
BEGIN
    WITH warning_check AS (
        SELECT 
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM events 
                    WHERE round_id = p_round_id
                    AND event_type = 'red'
                ) THEN TRUE
                ELSE FALSE
            END AS warning_terminated
    )
    INSERT INTO round_results (round_id, warning_terminated)
    SELECT p_round_id, warning_terminated
    FROM warning_check;
END;
$$ LANGUAGE plpgsql;



CREATE TABLE round_checks (
    round_check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID UNIQUE REFERENCES rounds(round_id),
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    outcome_valid BOOLEAN NOT NULL,
    green_pecks_valid BOOLEAN NOT NULL,
    red_pecks_valid BOOLEAN NOT NULL,
    feedback_period_valid BOOLEAN NOT NULL,
    pecks_until_warning_valid BOOLEAN NOT NULL,
    quarter_valid BOOLEAN NOT NULL,
    pecks_in_green INT,
    risky_green_events INT,
    green_events INT,
    pecks_in_red INT,
    red_events INT,
    green_count_until_warning INT,
    warning_index INT,
    warning_quarter INT,
    feeding_time TIMESTAMP,
    feeding_end_time TIMESTAMP,
    punishment_time TIMESTAMP,
    punishment_end_time TIMESTAMP,
    punishment_duration INT ,
    feed_time INT
);


CREATE OR REPLACE FUNCTION is_in_circle(
    x_position DOUBLE PRECISION,
    y_position DOUBLE PRECISION,
    radius DOUBLE PRECISION,
    center_x DOUBLE PRECISION,
    center_y DOUBLE PRECISION,
    aspect_ratio FLOAT DEFAULT 1.0
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (POWER((x_position - center_x) * aspect_ratio , 2)+ POWER(y_position - center_y, 2)) <= POWER(radius, 2);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION distance_between(
    x_start FLOAT,
    y_start FLOAT,
    x_end FLOAT,
    y_end FLOAT
) RETURNS FLOAT AS $$
BEGIN
    RETURN SQRT(POWER(x_end - x_start, 2) + POWER(y_end - y_start, 2));
END;
$$ LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION check_round(round_uuid UUID, aspect_ratio FLOAT)
RETURNS VOID AS $$
BEGIN
    WITH 
    round_id AS (
        SELECT round_uuid AS id
    ),
    sessions_info AS (
        SELECT s.reinforcement_ratio, s.button_height, s.warning_signal_position
        FROM rounds r
        JOIN sessions s ON r.session_id = s.session_id
        JOIN round_id ON r.round_id = round_id.id
    ),
    pecks_in_green AS (
        SELECT COUNT(*) AS peck_count
        FROM (
            SELECT is_in_circle(p.x_pos, p.y_pos, 0.075, 0.7, 
                                (SELECT button_height FROM sessions_info)/100.0, 
                                aspect_ratio) AS in_circle, 
                   p.screen_on AS screen_on,
                   p.green_on AS green_on
            FROM pecks p
            JOIN round_id ON p.round_id = round_id.id
        ) subquery
        WHERE subquery.in_circle AND subquery.screen_on AND subquery.green_on 
    ),
    pecks_in_red AS (
        SELECT COUNT(*) AS peck_count
        FROM (
            SELECT is_in_circle(p.x_pos, p.y_pos, 0.075, 
                                0.3 + (SELECT warning_signal_position FROM sessions_info)/100.0 * 0.4, 
                                (SELECT button_height FROM sessions_info)/100.0, 
                                aspect_ratio) AS in_circle, 
                   distance_between(p.x_start, p.y_start, p.x_pos, p.y_pos) > 0.05 AS peck_slides,
                   p.screen_on AS screen_on,
                   p.red_on AS red_on
            FROM pecks p
            JOIN round_id ON p.round_id = round_id.id
        ) subquery
        WHERE subquery.in_circle AND subquery.screen_on AND subquery.red_on AND NOT peck_slides
    ),
    timely_events AS (
        SELECT 
            round_id, 
            MAX(CASE WHEN event_type = 'punishment' THEN event_time END) AS punishment_time,
            MAX(CASE WHEN event_type = 'punishment_end' THEN event_time END) AS punishment_end_time,
            MAX(CASE WHEN event_type = 'feeding' THEN event_time END) AS feeding_time,
            MAX(CASE WHEN event_type = 'feeding_end' THEN event_time END) AS feeding_end_time
        FROM events
        GROUP BY round_id
    ),
    warning_event_time AS (
        SELECT event_time
        FROM events
        WHERE event_type = 'warning'
        AND round_id = (SELECT id FROM round_id)
        LIMIT 1
    ),
    green_events_until_warning AS (
        SELECT
            COUNT(*) AS green_count_until_warning
        FROM events
        WHERE event_type = 'green'
        AND round_id = (SELECT id FROM round_id)
        AND event_time < (SELECT event_time FROM warning_event_time)
    )
    INSERT INTO round_checks (
        round_id,
        outcome_valid,
        green_pecks_valid,
        red_pecks_valid,
        feedback_period_valid,
        pecks_until_warning_valid,
        quarter_valid,
        pecks_in_green,
        risky_green_events,
        green_events,
        pecks_in_red,
        red_events,
        green_count_until_warning,
        warning_index,
        warning_quarter,
        feeding_time,
        feeding_end_time,
        punishment_time,
        punishment_end_time,
        punishment_duration,
        feed_time
    )
    SELECT
        events.round_id,
        CASE
            WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0 
                 AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) < sessions.reinforcement_ratio 
                 AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) > sessions.warning_hits THEN TRUE
            WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1 
                 AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = sessions.reinforcement_ratio 
                 AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) < sessions.warning_hits THEN TRUE
            ELSE FALSE
        END AS outcome_valid,
        CASE
            WHEN COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = pecks_in_green.peck_count THEN TRUE
            ELSE FALSE
        END AS green_pecks_valid,
        CASE
            WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = pecks_in_red.peck_count THEN TRUE
            ELSE FALSE
        END AS red_pecks_valid,
        CASE
            WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0 
                 AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - sessions.punishment_duration) <= 0.2 THEN TRUE
            WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1 
                 AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 0.2 THEN TRUE
            ELSE FALSE
        END AS feedback_period_valid,
        CASE
            WHEN (SELECT green_count_until_warning FROM green_events_until_warning) = (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) THEN TRUE
            ELSE FALSE
        END AS pecks_until_warning_valid,
        CASE
            WHEN (SELECT warning_quarter FROM rounds WHERE round_id = (SELECT id FROM round_id)) = 
                 FLOOR((SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id))::float / (SELECT reinforcement_ratio FROM sessions WHERE session_id = (SELECT session_id FROM rounds WHERE round_id = (SELECT id FROM round_id)))::float * 4) + 1 THEN TRUE
            ELSE FALSE
        END AS quarter_valid,
        pecks_in_green.peck_count AS pecks_in_green,
        COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) AS risky_green_events,
        COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) AS green_events,
        pecks_in_red.peck_count AS pecks_in_red,
        COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) AS red_events,
        (SELECT green_count_until_warning FROM green_events_until_warning) AS green_count_until_warning,
        (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) AS warning_index,
        (SELECT warning_quarter FROM rounds WHERE round_id = (SELECT id FROM round_id)) AS warning_quarter,
        MAX(timely_events.feeding_time) AS feeding_time,
        MAX(timely_events.feeding_end_time) AS feeding_end_time,
        MAX(timely_events.punishment_time) AS punishment_time,
        MAX(timely_events.punishment_end_time) AS punishment_end_time,
        sessions.punishment_duration,
        sessions.feed_time
    FROM
        events
    JOIN
        rounds ON events.round_id = rounds.round_id
    JOIN
        sessions ON rounds.session_id = sessions.session_id
    JOIN
        pecks_in_green ON TRUE
    JOIN
        pecks_in_red ON TRUE
    JOIN
        timely_events ON events.round_id = timely_events.round_id
    WHERE
        events.round_id = (SELECT id FROM round_id)
    GROUP BY
        events.round_id, sessions.session_id, pecks_in_green.peck_count, pecks_in_red.peck_count;
END;
$$ LANGUAGE plpgsql;



--SELECT check_round('cd0d766e-a4b8-4da3-a2e6-a7af0d84c201');