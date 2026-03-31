CREATE TABLE IF NOT EXISTS experiment_modes (
    mode_id SERIAL PRIMARY KEY,
    mode_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id SERIAL PRIMARY KEY,
    subject_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS sessions (
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
    button_size INTEGER NOT NULL,                       -- Size of the button
    grace_radius INTEGER NOT NULL,                      -- Radius outside the button where pecks are valid
    warning_signal_position INTEGER NOT NULL,           -- Position of the warning signal
    button_height INTEGER NOT NULL,                     -- Height of the button
    peck_slide INTEGER NOT NULL,                        -- Acceptable peck slide distance
    created_at TIMESTAMP DEFAULT NOW(),                 -- Record creation timestamp
    updated_at TIMESTAMP DEFAULT NOW(),                 -- Record update timestamp
    window_height INTEGER,                              -- Height of the window
    window_width INTEGER,                               -- Width of the window
    warning_q1 INTEGER,                                 -- Warning quartile 1 boundary (mode 6)
    warning_q2 INTEGER,                                 -- Warning quartile 2 boundary (mode 6)
    warning_q3 INTEGER,                                 -- Warning quartile 3 boundary (mode 6)
    comments TEXT                                       -- Optional comments
);

CREATE TABLE IF NOT EXISTS cumulative_record (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),          -- Time of the event
    hit_count INTEGER,                                    -- Number of hit_count
    session_id UUID REFERENCES sessions(session_id) -- Foreign key to experiments table
);

CREATE TABLE IF NOT EXISTS rounds (
    session_id UUID REFERENCES sessions(session_id),
    round_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    round_index INTEGER NOT NULL,
    warning_index INTEGER NOT NULL,
    warning_quarter INTEGER NOT NULL,
    reinforcers_count INTEGER NOT NULL,
    required_clicks INTEGER,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Migration: add required_clicks for existing databases (no-op if column already exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'rounds' AND column_name = 'required_clicks'
    ) THEN
        ALTER TABLE rounds ADD COLUMN required_clicks INTEGER;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS events (
    round_id UUID REFERENCES rounds(round_id),              -- Round Index
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),   -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),            -- Time of the event
    event_type VARCHAR(50) NOT NULL,                        -- Type of event (e.g., "stimulus", "response")
    warning_signal_present BOOLEAN NOT NULL,                 -- Whether a warning signal was present
    hit_count INT NOT NULL DEFAULT 0                       -- Number of hits
);

-- Create pecks table
CREATE TABLE IF NOT EXISTS pecks (
    peck_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	x_start FLOAT NOT NULL, 
	y_start FLOAT NOT NULL,
    x_pos FLOAT NOT NULL,
    y_pos FLOAT NOT NULL,
    screen_on BOOLEAN NOT NULL,
    green_on BOOLEAN NOT NULL,
    red_on BOOLEAN NOT NULL,
    peck_time TIMESTAMP NOT NULL DEFAULT NOW(),
    round_id UUID REFERENCES rounds(round_id) NOT NULL
);


CREATE TABLE IF NOT EXISTS round_tests (
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



CREATE TABLE IF NOT EXISTS session_tests (
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
    ('Ermis', 4)
ON CONFLICT DO NOTHING;


INSERT INTO experiment_modes (mode_name, mode_id) VALUES
('HOPPER TRAINING', 1),
('SCHEDULE TRAINING', 2),
('WARNING TRAINING', 3),
('RANDOM WARNING', 4),
('VARIABLE RATIO', 5),
('VARIABLE WARNING', 6)
ON CONFLICT DO NOTHING;

-- Index for JOIN
CREATE INDEX IF NOT EXISTS idx_events_round_id ON events(round_id);
CREATE INDEX IF NOT EXISTS idx_rounds_round_id ON rounds(round_id);

-- Index for Subquery Sorting
CREATE INDEX IF NOT EXISTS idx_rounds_started_at ON rounds(started_at);

-- Index for Filtering
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_warning_signal_present ON events(warning_signal_present);

-- Composite Index for Filtering
CREATE INDEX IF NOT EXISTS idx_events_round_event_type ON events(round_id, event_type);

CREATE TABLE IF NOT EXISTS round_results (
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



CREATE TABLE IF NOT EXISTS round_checks (
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
    feed_time INT,
    aspect_ratio NUMERIC,
    radius NUMERIC
);


CREATE OR REPLACE FUNCTION is_in_circle(
    x_position NUMERIC,  -- The x-coordinate of the point to check
    y_position NUMERIC,  -- The y-coordinate of the point to check
    radius NUMERIC,      -- The radius of the ellipse (the semi-major axis)
    center_x NUMERIC,    -- The x-coordinate of the ellipse center
    center_y NUMERIC,    -- The y-coordinate of the ellipse center
    aspect_ratio NUMERIC -- The aspect ratio, which adjusts the x-axis for the ellipse
)
RETURNS BOOLEAN AS $$
BEGIN
    -- Calculate the adjusted x-distance by scaling the x-position with the aspect ratio
    DECLARE
        adjusted_x NUMERIC;
        x_distance NUMERIC;
        y_distance NUMERIC;
        distance NUMERIC;
    BEGIN
        -- Adjust the x-coordinate by multiplying it with the aspect ratio
        adjusted_x := (x_position - center_x) * aspect_ratio;

        -- Calculate the squared distances in x and y directions
        x_distance := POWER(adjusted_x, 2);
        y_distance := POWER(y_position - center_y, 2);

        -- Calculate the total distance from the point to the center
        distance := SQRT(x_distance + y_distance);

        -- Check if the distance is less than or equal to the radius
        RETURN distance <= radius;
    END;
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






CREATE OR REPLACE FUNCTION check_round(round_uuid UUID)
RETURNS VOID AS $$
BEGIN
    WITH 
    round_id AS (
        SELECT round_uuid AS id
    ),
    session_info AS (
        SELECT s.reinforcement_ratio, s.button_height, s.warning_signal_position, r.round_index,
               s.button_size, s.grace_radius, s.peck_slide, s.window_width, s.window_height, s.mode_id, round_id 
        FROM rounds r
        JOIN sessions s ON r.session_id = s.session_id
        JOIN round_id ON r.round_id = round_id.id
    ),
    pecks_in_green AS (
        SELECT COUNT(*) AS peck_count
        FROM (
            SELECT is_in_circle(
									p.x_pos::NUMERIC, 
									p.y_pos::NUMERIC, 
                                	(SELECT (button_size / 2.0 + grace_radius) / 100.0 FROM session_info)::NUMERIC, 
                                	0.7::NUMERIC, 
                                	(SELECT button_height / 100.0 FROM session_info)::NUMERIC,
                                	(SELECT (window_width::NUMERIC / window_height::NUMERIC ) FROM session_info)::NUMERIC
									) AS in_circle, 
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
					SELECT is_in_circle(
					    p.x_pos::NUMERIC, 
					    p.y_pos::NUMERIC, 
					    ((SELECT button_size / 2.0 + grace_radius FROM session_info) / 100.0)::NUMERIC, 
					    (0.3 + (SELECT warning_signal_position FROM session_info) / 100.0 * 0.4)::NUMERIC, 
					    (SELECT button_height FROM session_info) / 100.0::NUMERIC, 
					    (SELECT (window_width::NUMERIC ) / (window_height::NUMERIC ) FROM session_info)::NUMERIC
					) AS in_circle,
													
                   (distance_between(p.x_start, p.y_start, p.x_pos, p.y_pos) > ( (SELECT peck_slide FROM session_info)) / 100.0 )AS peck_slides,
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
        feed_time,
		radius,
		aspect_ratio
    )
    SELECT
        events.round_id,
        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) < 0
                        AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = rounds.required_clicks THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) <= rounds.required_clicks
                         AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) > sessions.warning_hits THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = rounds.required_clicks
                         AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) <= sessions.warning_hits THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) < 0
                        AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = sessions.reinforcement_ratio THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) <= sessions.reinforcement_ratio
                         AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) > sessions.warning_hits THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = sessions.reinforcement_ratio
                         AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) <= sessions.warning_hits THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = sessions.reinforcement_ratio THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'warning' THEN 1 END) = 0
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = sessions.reinforcement_ratio THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) < sessions.reinforcement_ratio THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 5 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = rounds.required_clicks THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 2 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = sessions.reinforcement_ratio THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 1 THEN
                CASE
                    WHEN (COUNT(CASE WHEN events.event_type = 'feeding' THEN 1 END) = 1) OR (COUNT(CASE WHEN events.event_type = 'session_end' THEN 1 END) = 1) THEN TRUE
                    ELSE FALSE
                END
            ELSE FALSE
        END AS outcome_valid,

        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = pecks_in_green.peck_count THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = pecks_in_green.peck_count THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = pecks_in_green.peck_count THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 5 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = pecks_in_green.peck_count THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 2 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = pecks_in_green.peck_count THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 1 THEN TRUE
            ELSE FALSE
        END AS green_pecks_valid,

        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = pecks_in_red.peck_count THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = pecks_in_red.peck_count THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = pecks_in_red.peck_count THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 5 THEN TRUE
            WHEN session_info.mode_id = 2 THEN TRUE
            WHEN session_info.mode_id = 1 THEN TRUE
            ELSE FALSE
        END AS red_pecks_valid,

        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) < 0 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - sessions.punishment_duration) <= 1 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) < 0 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - sessions.punishment_duration) <= 1 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'warning' THEN 1 END) = 0
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - sessions.punishment_duration) <= 1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 5 THEN
                CASE
                    WHEN ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 2 THEN
                CASE
                    WHEN ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 1 THEN
                CASE
                    WHEN ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    ELSE FALSE
                END
            ELSE FALSE
        END AS feedback_period_valid,

        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN (SELECT green_count_until_warning FROM green_events_until_warning) = (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) THEN TRUE
                    WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) < 0 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN (SELECT green_count_until_warning FROM green_events_until_warning) = (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) THEN TRUE
                    WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) < 0 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN TRUE
            WHEN session_info.mode_id = 5 THEN TRUE
            WHEN session_info.mode_id = 2 THEN TRUE
            WHEN session_info.mode_id = 1 THEN TRUE
            ELSE FALSE
        END AS pecks_until_warning_valid,

        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) < 0
                         AND (SELECT warning_quarter FROM rounds WHERE round_id = (SELECT id FROM round_id)) = -1 THEN TRUE
                    WHEN (SELECT warning_quarter FROM rounds WHERE round_id = (SELECT id FROM round_id)) =
                         CASE
                             WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) <= (SELECT warning_q1 FROM sessions WHERE session_id = (SELECT session_id FROM rounds WHERE round_id = (SELECT id FROM round_id))) THEN 1
                             WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) <= (SELECT warning_q2 FROM sessions WHERE session_id = (SELECT session_id FROM rounds WHERE round_id = (SELECT id FROM round_id))) THEN 2
                             WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) <= (SELECT warning_q3 FROM sessions WHERE session_id = (SELECT session_id FROM rounds WHERE round_id = (SELECT id FROM round_id))) THEN 3
                             ELSE 4
                         END THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) < 0
                         AND (SELECT warning_quarter FROM rounds WHERE round_id = (SELECT id FROM round_id)) = -1 THEN TRUE
                    WHEN (SELECT warning_quarter FROM rounds WHERE round_id = (SELECT id FROM round_id)) =
                         FLOOR((SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id))::float / (SELECT reinforcement_ratio FROM sessions WHERE session_id = (SELECT session_id FROM rounds WHERE round_id = (SELECT id FROM round_id)))::float * 4) + 1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN (SELECT warning_quarter FROM rounds WHERE round_id = (SELECT id FROM round_id)) = -1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 5 THEN TRUE
            WHEN session_info.mode_id = 2 THEN TRUE
            WHEN session_info.mode_id = 1 THEN TRUE
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
        sessions.feed_time,
		((SELECT button_size / 2.0 + grace_radius FROM session_info) / 100.0)::NUMERIC AS radius,
		(SELECT (window_width::NUMERIC / window_height::NUMERIC ) FROM session_info)::NUMERIC AS aspect_ratio
    FROM
        events
    JOIN
        rounds ON events.round_id = rounds.round_id
    JOIN
        sessions ON rounds.session_id = sessions.session_id
    JOIN
        session_info ON TRUE
    JOIN
        pecks_in_green ON TRUE
    JOIN
        pecks_in_red ON TRUE
    JOIN
        timely_events ON events.round_id = timely_events.round_id
    WHERE
        events.round_id = (SELECT id FROM round_id)
    GROUP BY
        events.round_id, sessions.session_id, pecks_in_green.peck_count, pecks_in_red.peck_count, session_info.round_id, session_info.mode_id, rounds.round_id;
END;
$$ LANGUAGE plpgsql;





--SELECT check_round('cd0d766e-a4b8-4da3-a2e6-a7af0d84c201');

CREATE TABLE IF NOT EXISTS session_results (
    result_id UUID UNIQUE PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID  REFERENCES sessions(session_id),
    warning_quarter INT NOT NULL,
    total_rounds INT NOT NULL,
    terminations INT NOT NULL,
    result_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (session_id, warning_quarter) -- Composite unique constraint
);

CREATE TABLE IF NOT EXISTS weights (
    weight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),          -- Primary key
    subject_id INTEGER NOT NULL REFERENCES subjects(subject_id),    -- Foreign key to subjects table
    weighted_at TIMESTAMP DEFAULT NOW(),                            -- Record creation timestamp
    subject_weight INTEGER NOT NULL                                 -- Weight of the subject
);

CREATE TABLE IF NOT EXISTS errors (
    error_id UUID UNIQUE PRIMARY KEY DEFAULT gen_random_uuid(),
    error_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    round_id UUID REFERENCES rounds(round_id),
    session_id UUID REFERENCES sessions(session_id),
    CHECK (session_id IS NOT NULL OR round_id IS NOT NULL)
);


CREATE OR REPLACE FUNCTION log_error_with_session_id(session_id UUID, error_message TEXT) RETURNS VOID AS $$
BEGIN
    INSERT INTO errors (session_id, error_message) VALUES (session_id, error_message);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION log_error_with_round_id(round_id UUID, error_message TEXT) RETURNS VOID AS $$
BEGIN
    INSERT INTO errors (round_id, error_message) VALUES (round_id, error_message);
END;
$$ LANGUAGE plpgsql;



CREATE TABLE IF NOT EXISTS session_checks (
    session_check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID UNIQUE REFERENCES sessions(session_id),
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_reinforcements_valid BOOLEAN NOT NULL,
    total_rounds_valid BOOLEAN NOT NULL,
    total_warnings_valid BOOLEAN NOT NULL,
    warning_switch_valid BOOLEAN NOT NULL,
    round_checks_passed BOOLEAN NOT NULL,
    session_end_valid BOOLEAN NOT NULL,
    no_errors BOOLEAN NOT NULL,
    total_time_valid BOOLEAN NOT NULL,
    database_errors INT,
    total_reinforcements INT,
    total_rounds INT,
    total_punishments INT,
    total_warning_terminations INT,
    total_warning_presentations INT,
    total_warning_switches INT,
    total_time INTERVAL
);


CREATE OR REPLACE FUNCTION insert_session_results(session_id UUID)
RETURNS VOID AS $$
BEGIN
    INSERT INTO session_results (session_id, warning_quarter, total_rounds, terminations)
    SELECT 
        r.session_id,
        warning_quarter, 
        COUNT(*) AS total_rounds, 
        SUM(CASE WHEN warning_terminated THEN 1 ELSE 0 END) AS terminations
    FROM 
        round_results rr
    JOIN 
        rounds r ON rr.round_id = r.round_id
    WHERE 
        r.session_id = $1 -- Use $1 to explicitly reference the function parameter
        AND r.warning_quarter >= 0 -- Exclude free rounds (warning_quarter = -1)
    GROUP BY
        warning_quarter, r.session_id
    ORDER BY 
        warning_quarter;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION notify_event() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('new_event', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER event_trigger
AFTER INSERT ON events
FOR EACH ROW
EXECUTE FUNCTION notify_event();


CREATE OR REPLACE FUNCTION notify_peck() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('new_peck', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER peck_trigger
AFTER INSERT ON pecks
FOR EACH ROW
EXECUTE FUNCTION notify_peck();


CREATE OR REPLACE FUNCTION count_consecutive_unterminated_warnings(session_uuid UUID)
RETURNS INT AS $$
DECLARE
    consecutive_count INT := 0;
    consecutive_warnings_limit INT;
    current_consecutive INT := 0;
    round_id UUID;
    warning_terminated BOOLEAN;
BEGIN
    SELECT s.consecutive_warnings_limit
    INTO consecutive_warnings_limit
    FROM sessions s
    WHERE s.session_id = session_uuid;

    FOR round_id, warning_terminated IN
        SELECT r.round_id, rr.warning_terminated
        FROM rounds r
        JOIN round_results rr ON r.round_id = rr.round_id
        WHERE r.session_id = session_uuid
        AND r.warning_index >= 0 -- Exclude free rounds
        ORDER BY r.round_index
    LOOP
        IF warning_terminated = FALSE THEN
            current_consecutive := current_consecutive + 1;
            IF current_consecutive >= consecutive_warnings_limit THEN
                consecutive_count := consecutive_count + 1;
                current_consecutive := 0;
            END IF;
        ELSE
            current_consecutive := 0;
        END IF;
    END LOOP;

    RETURN consecutive_count;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION check_session(session_uuid UUID)
RETURNS VOID AS $$
BEGIN
    WITH
    session_info AS (
        SELECT session_id, total_reinforcements, mode_id
        FROM sessions
        WHERE session_id = session_uuid
    ),
    session_start_event AS (
        SELECT event_time AS session_start
        FROM events
        JOIN rounds ON events.round_id = rounds.round_id
        WHERE event_type = 'session_start'
        AND session_id = session_uuid
        LIMIT 1
    ),
    session_end_event AS (
        SELECT event_time AS session_end
        FROM events
        JOIN rounds ON events.round_id = rounds.round_id
        WHERE event_type = 'session_end'
        AND session_id = session_uuid
        LIMIT 1
    ),
    feeding_events AS (
        SELECT COUNT(*) AS feeding_count
        FROM events e
        JOIN rounds r ON e.round_id = r.round_id
        WHERE e.event_type = 'feeding'
        AND r.session_id = session_uuid
    ),
    round_count AS (
        SELECT COUNT(*) AS round_count
        FROM rounds
        WHERE session_id = session_uuid
    ),
    round_end_events AS (
        SELECT COUNT(*) AS round_end_count
        FROM events e
        JOIN rounds r ON e.round_id = r.round_id
        WHERE e.event_type = 'round_end'
        AND r.session_id = session_uuid
    ),
    new_round_events AS (
        SELECT COUNT(*) AS new_round_count
        FROM events e
        JOIN rounds r ON e.round_id = r.round_id
        WHERE e.event_type = 'new_round'
        AND r.session_id = session_uuid
    ),
    session_end_events AS (
        SELECT COUNT(*) AS session_end_count
        FROM events e
        JOIN rounds r ON e.round_id = r.round_id
        WHERE e.event_type = 'session_end'
        AND r.session_id = session_uuid
    ),
    warning_events AS (
        SELECT COUNT(*) AS warning_count
        FROM events e
        JOIN rounds r ON e.round_id = r.round_id
        WHERE e.event_type = 'warning'
        AND r.session_id = session_uuid
    ),
    termination_events AS (
        SELECT COUNT(*) AS termination_count
        FROM events e
        JOIN rounds r ON e.round_id = r.round_id
        WHERE e.event_type = 'red'
        AND r.session_id = session_uuid
    ),
    warning_switch_events AS (
        SELECT COUNT(*) AS warning_switch_count
        FROM events e
        JOIN rounds r ON e.round_id = r.round_id
        WHERE e.event_type = 'warning_switch'
        AND r.session_id = session_uuid
    ),
    punishment_events AS (
        SELECT COUNT(*) AS punishment_count
        FROM events e
        JOIN rounds r ON e.round_id = r.round_id
        WHERE e.event_type = 'punishment'
        AND r.session_id = session_uuid
    ),
    round_checks_passed AS (
        SELECT COUNT(*) = 0 AS all_passed
        FROM round_checks rc
        JOIN rounds r ON rc.round_id = r.round_id
        WHERE r.session_id = session_uuid
        AND NOT (rc.outcome_valid AND rc.green_pecks_valid AND rc.red_pecks_valid AND rc.feedback_period_valid AND rc.pecks_until_warning_valid AND rc.quarter_valid)
    ),
    database_errors AS (
        SELECT COUNT(*) AS error_count
        FROM errors e
        WHERE e.session_id = session_uuid
        OR e.round_id IN (SELECT round_id FROM rounds WHERE session_id = session_uuid)
    )
    INSERT INTO session_checks (
        session_id,
        total_reinforcements_valid,
        total_rounds_valid,
        total_warnings_valid,
        warning_switch_valid,
        round_checks_passed,
        session_end_valid,
        no_errors,
        total_time_valid,
        database_errors,
        total_reinforcements,
        total_rounds,
        total_punishments,
        total_warning_terminations,
        total_warning_presentations,
        total_warning_switches,
        total_time
    )
    SELECT
        session_info.session_id,

        CASE
            WHEN (SELECT feeding_count FROM feeding_events) = session_info.total_reinforcements THEN TRUE
            ELSE FALSE
        END AS total_reinforcements_valid,

        CASE
            WHEN (SELECT round_count FROM round_count) = (SELECT round_end_count FROM round_end_events)
                    AND (SELECT round_count FROM round_count) = (SELECT new_round_count FROM new_round_events)
                    AND (SELECT round_count FROM round_count) = (session_info.total_reinforcements + (SELECT punishment_count FROM punishment_events)) THEN TRUE
            ELSE FALSE
        END AS total_rounds_valid,

        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN (SELECT warning_count FROM warning_events) = (session_info.total_reinforcements + (SELECT punishment_count FROM punishment_events) - (SELECT warning_switch_count FROM warning_switch_events)) THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN (SELECT warning_count FROM warning_events) = (session_info.total_reinforcements + (SELECT punishment_count FROM punishment_events) - (SELECT warning_switch_count FROM warning_switch_events)) THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN (SELECT warning_count FROM warning_events) = (SELECT punishment_count FROM punishment_events) + (SELECT termination_count FROM termination_events) THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 5 THEN TRUE
            WHEN session_info.mode_id = 2 THEN TRUE
            WHEN session_info.mode_id = 1 THEN TRUE
            ELSE FALSE
        END AS total_warnings_valid,

        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN (SELECT warning_switch_count FROM warning_switch_events) = count_consecutive_unterminated_warnings(session_uuid) THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN (SELECT warning_switch_count FROM warning_switch_events) = count_consecutive_unterminated_warnings(session_uuid) THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN (SELECT round_count FROM round_count) = (SELECT termination_count FROM termination_events) + (SELECT punishment_count FROM punishment_events) + (SELECT warning_switch_count FROM warning_switch_events) + 1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 5 THEN TRUE
            WHEN session_info.mode_id = 2 THEN TRUE
            WHEN session_info.mode_id = 1 THEN TRUE
            ELSE FALSE
        END AS warning_switch_valid,

        (SELECT all_passed FROM round_checks_passed) AS round_checks_passed,

        CASE
            WHEN (SELECT session_end_count FROM session_end_events) = 1 THEN TRUE
            ELSE FALSE
        END AS session_end_valid,

        CASE
            WHEN (SELECT error_count FROM database_errors) = 0 THEN TRUE
            ELSE FALSE
        END AS no_errors,

        CASE
            WHEN EXTRACT(EPOCH FROM ((SELECT session_end FROM session_end_event) - (SELECT session_start FROM session_start_event))) > 0 THEN TRUE
            ELSE FALSE
        END AS total_time_valid,

        (SELECT error_count FROM database_errors) AS database_errors,
        (SELECT feeding_count FROM feeding_events) AS total_reinforcements,
        (SELECT round_count FROM round_count) AS total_rounds,
        (SELECT punishment_count FROM punishment_events) AS total_punishments,
        (SELECT termination_count FROM termination_events) AS total_warning_terminations,
        (SELECT warning_count FROM warning_events) AS total_warning_presentations,
        (SELECT warning_switch_count FROM warning_switch_events) AS total_warning_switches,
        (SELECT session_end FROM session_end_event) - (SELECT session_start FROM session_start_event) AS total_time
    FROM
        session_info;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- Schema migrations for existing databases
-- Adds new columns that may not exist yet
-- ============================================================
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS warning_q1 INTEGER;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS warning_q2 INTEGER;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS warning_q3 INTEGER;