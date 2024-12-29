CREATE TABLE round_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID UNIQUE REFERENCES rounds(round_id),
    warning_terminated BOOLEAN,
    result_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO round_results (round_id, warning_terminated)
VALUES ('some-uuid-value', false);

-- Select all session round results
SELECT 
    rr.result_id,
    rr.round_id,
    rr.warning_terminated,
    rr.result_time,
    r.session_id,
    r.round_index,
    r.warning_index,
    r.warning_quarter,
    r.reinforcers_count,
    r.started_at
FROM 
    round_results rr
JOIN 
    rounds r ON rr.round_id = r.round_id;

-- Select all results for all rounds of a specific session
SELECT 
    rr.result_id,
    rr.round_id,
    rr.warning_terminated,
    rr.result_time,
    r.session_id,
    r.round_index,
    r.warning_index,
    r.warning_quarter,
    r.reinforcers_count,
    r.started_at
FROM 
    round_results rr
JOIN 
    rounds r ON rr.round_id = r.round_id
WHERE 
    r.session_id = 'specific-session-uuid';

-- Query to return warning_terminated for a specific round_id and insert into round_results
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


CREATE TABLE session_results (
    result_id UUID UNIQUE PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID  REFERENCES sessions(session_id),
    warning_quarter INT NOT NULL,
    total_rounds INT NOT NULL,
    terminations INT NOT NULL,
    result_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (session_id, warning_quarter) -- Composite unique constraint
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
        r.session_id = session_id
    GROUP BY 
        warning_quarter, r.session_id
    ORDER BY 
        warning_quarter;
END;
$$ LANGUAGE plpgsql;




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
    session_id
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
    MAX(CASE WHEN warning_quarter = 1 THEN CONCAT(terminations, '/', total_rounds, ' (', ROUND(termination_percentage, 2), '%)') ELSE '' END) AS quarter_1,
    MAX(CASE WHEN warning_quarter = 2 THEN CONCAT(terminations, '/', total_rounds, ' (', ROUND(termination_percentage, 2), '%)') ELSE '' END) AS quarter_2,
    MAX(CASE WHEN warning_quarter = 3 THEN CONCAT(terminations, '/', total_rounds, ' (', ROUND(termination_percentage, 2), '%)') ELSE '' END) AS quarter_3,
    MAX(CASE WHEN warning_quarter = 4 THEN CONCAT(terminations, '/', total_rounds, ' (', ROUND(termination_percentage, 2), '%)') ELSE '' END) AS quarter_4
FROM
    termination_percentages
GROUP BY
    result_time
ORDER BY
    result_time DESC
LIMIT 10;

SELECT * FROM session_results;