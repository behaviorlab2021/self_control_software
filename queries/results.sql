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


