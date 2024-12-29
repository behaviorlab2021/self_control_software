CREATE TABLE session_results (
    result_id UUID UNIQUE PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID  REFERENCES sessions(session_id),
    warning_quarter INT NOT NULL,
    total_rounds INT NOT NULL,
    terminations INT NOT NULL,
    result_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (session_id, warning_quarter) -- Composite unique constraint
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

WITH session_info AS (
    SELECT
        subject_id,
        reinforcement_ratio
    FROM
        sessions
    WHERE
        session_id = '6f84a92f-0069-4969-9572-62cb5703cada'
),
termination_percentages AS (
    SELECT
        sr.session_id,
        sr.warning_quarter,
        (sr.terminations::FLOAT / sr.total_rounds) * 100 AS termination_percentage,
        sr.result_time
    FROM
        session_results sr
    JOIN
        sessions s ON sr.session_id = s.session_id
    WHERE
        s.subject_id = (SELECT subject_id FROM session_info)
        AND s.reinforcement_ratio = (SELECT reinforcement_ratio FROM session_info)
)
SELECT
    TO_CHAR(result_time, 'YYYY-MM-DD') AS result_time,
    MAX(CASE WHEN warning_quarter = 1 THEN termination_percentage ELSE 0 END) AS quarter_1_percentage,
    MAX(CASE WHEN warning_quarter = 2 THEN termination_percentage ELSE 0 END) AS quarter_2_percentage,
    MAX(CASE WHEN warning_quarter = 3 THEN termination_percentage ELSE 0 END) AS quarter_3_percentage,
    MAX(CASE WHEN warning_quarter = 4 THEN termination_percentage ELSE 0 END) AS quarter_4_percentage,
FROM
    termination_percentages
GROUP BY
    session_id, result_time
ORDER BY
    result_time DESC
LIMIT 10;

SELECT * FROM session_results;

WITH session_info AS (
    SELECT
        subject_id,
        reinforcement_ratio
    FROM
        sessions
    WHERE
        session_id = '6f84a92f-0069-4969-9572-62cb5703cada'
),
termination_percentages AS (
    SELECT
        sr.session_id,
        sr.warning_quarter,
        sr.terminations,
        sr.total_rounds,
        (sr.terminations::FLOAT / sr.total_rounds) * 100 AS termination_percentage,
        sr.result_time
    FROM
        session_results sr
    JOIN
        sessions s ON sr.session_id = s.session_id
    WHERE
        s.subject_id = (SELECT subject_id FROM session_info)
        AND s.reinforcement_ratio = (SELECT reinforcement_ratio FROM session_info)
)
SELECT
    TO_CHAR(result_time, 'YYYY-MM-DD') AS result_time,
    MAX(CASE WHEN warning_quarter = 1 THEN CONCAT(terminations, '/', total_rounds, ' (', ROUND(termination_percentage::numeric, 2), '%)') ELSE '' END) AS quarter_1,
    MAX(CASE WHEN warning_quarter = 2 THEN CONCAT(terminations, '/', total_rounds, ' (', ROUND(termination_percentage::numeric, 2), '%)') ELSE '' END) AS quarter_2,
    MAX(CASE WHEN warning_quarter = 3 THEN CONCAT(terminations, '/', total_rounds, ' (', ROUND(termination_percentage::numeric, 2), '%)') ELSE '' END) AS quarter_3,
    MAX(CASE WHEN warning_quarter = 4 THEN CONCAT(terminations, '/', total_rounds, ' (', ROUND(termination_percentage::numeric, 2), '%)') ELSE '' END) AS quarter_4
FROM
    termination_percentages
GROUP BY
    result_time
ORDER BY
    result_time DESC
LIMIT 10;

SELECT * FROM session_results;

WITH session_info AS (
    SELECT
        subject_id,
        reinforcement_ratio
    FROM
        sessions
    WHERE
        session_id = '6f84a92f-0069-4969-9572-62cb5703cada'
),
termination_percentages AS (
    SELECT
        sr.session_id,
        sr.warning_quarter,
        (sr.terminations::FLOAT / sr.total_rounds) * 100 AS termination_percentage,
        sr.result_time
    FROM
        session_results sr
    JOIN
        sessions s ON sr.session_id = s.session_id
    WHERE
        s.subject_id = (SELECT subject_id FROM session_info)
        AND s.reinforcement_ratio = (SELECT reinforcement_ratio FROM session_info)
)
SELECT
    ROW_NUMBER() OVER (ORDER BY result_time) AS session_number,
    TO_CHAR(result_time, 'YYYY-MM-DD') AS result_time,
    MAX(CASE WHEN warning_quarter = 1 THEN termination_percentage ELSE 0 END) AS quarter_1_percentage,
    MAX(CASE WHEN warning_quarter = 2 THEN termination_percentage ELSE 0 END) AS quarter_2_percentage,
    MAX(CASE WHEN warning_quarter = 3 THEN termination_percentage ELSE 0 END) AS quarter_3_percentage,
    MAX(CASE WHEN warning_quarter = 4 THEN termination_percentage ELSE 0 END) AS quarter_4_percentage
FROM
    termination_percentages
GROUP BY
    result_time
ORDER BY
    result_time DESC
LIMIT 10;

