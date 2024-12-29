SELECT 
  COUNT(CASE WHEN e.event_type = 'green' THEN 1 END) AS green_event_count,
  COUNT(CASE WHEN e.event_type = 'red' THEN 1 END) AS red_event_count
FROM events e
JOIN rounds r ON e.round_id = r.round_id
WHERE r.session_id = '36d523b6-7c27-47e6-ad51-266f37b70772';

-- Create pecks table
CREATE TABLE pecks (
    peck_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    x_pos FLOAT NOT NULL,
    y_pos FLOAT NOT NULL,
    screen_on BOOLEAN NOT NULL,
    peck_time TIMESTAMP NOT NULL DEFAULT NOW(),
    round_id UUID REFERENCES rounds(round_id) NOT NULL
);

SELECT * FROM pecks;

-- Select the last session by time
SELECT *
FROM sessions
ORDER BY created_at DESC
LIMIT 1;

-- Select distinct event types from events table
SELECT DISTINCT event_type
FROM events;


CREATE OR REPLACE FUNCTION is_in_circle(
    x_position DOUBLE PRECISION,
    y_position DOUBLE PRECISION,
    radius DOUBLE PRECISION,
    center_x DOUBLE PRECISION,
    center_y DOUBLE PRECISION
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (POWER(x_position - center_x, 2) + POWER(y_position - center_y, 2)) <= POWER(radius, 2);
END;
$$ LANGUAGE plpgsql;


SELECT
  COUNT(CASE WHEN e.event_type = 'green' THEN 1 END) AS green_event_count,
  COUNT(CASE WHEN e.event_type = 'red' THEN 1 END) AS red_event_count,
  COUNT(CASE WHEN e.event_type = 'feeding' THEN 1 END) AS feeding_event_count,
  COUNT(CASE WHEN e.event_type = 'warning' THEN 1 END) AS warning_event_count
FROM events e
WHERE e.round_id = 'cf8755fd-b75c-4c25-94a2-0c025aca7918'



SELECT *,
       is_in_circle(p.x_pos, p.y_pos, 0.3, 0.7, 0.6) AS in_circle
FROM pecks p
WHERE p.round_id = '1487f2c1-a9ed-46a6-8267-9127ac4d0d16';

--Find number of pecks inside green
SELECT COUNT(*) AS num_in_circle
FROM (
    SELECT is_in_circle(p.x_pos, p.y_pos, 0.15, 0.7, 0.6) AS in_circle, p.screen_on AS screen_on
    FROM pecks p
    WHERE p.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d'
) subquery
WHERE subquery.in_circle = TRUE and subquery.screen_on = TRUE;

--Find the session_id from round_id
SELECT r.session_id
FROM rounds r 
WHERE r.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d'  


--Find reinforcement_ration from round_id
SELECT s.reinforcement_ratio
FROM rounds r
JOIN sessions s ON r.session_id = s.session_id
WHERE r.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d';

-- Select all peck of round
SELECT * FROM pecks p
WHERE p.round_id = '1487f2c1-a9ed-46a6-8267-9127ac4d0d16'

-- Select the last round by time
SELECT *
FROM rounds r JOIN sessions s ON r.session_id = s.session_id 
ORDER BY started_at DESC
LIMIT 2;

WITH 
sessions_info AS (
    SELECT s.reinforcement_ratio, s.button_height
    FROM rounds r
    JOIN sessions s ON r.session_id = s.session_id
    WHERE r.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d'
),
pecks_in_circle AS (
    SELECT COUNT(*) AS num_in_circle
    FROM (
        SELECT is_in_circle(p.x_pos, p.y_pos, 0.15, 0.7, (SELECT button_height FROM sessions_info)/100) AS in_circle, 
               p.screen_on AS screen_on
        FROM pecks p
        WHERE p.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d'
    ) subquery
    WHERE subquery.in_circle = TRUE AND subquery.screen_on = TRUE
)
SELECT 
    CASE 
        WHEN pecks_in_circle.num_in_circle = sessions_info.reinforcement_ratio THEN TRUE
        ELSE FALSE
    END AS green_number_accurate
FROM pecks_in_circle, sessions_info;





WITH 
sessions_info AS (
    SELECT s.reinforcement_ratio, s.button_height
    FROM rounds r
    JOIN sessions s ON r.session_id = s.session_id
    WHERE r.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d'
),
pecks_in_circle AS (
    SELECT COUNT(*) AS num_in_circle
    FROM (
        SELECT is_in_circle(p.x_pos, p.y_pos, 0.15, 0.7, (SELECT button_height FROM sessions_info)/100.0) AS in_circle, 
               p.screen_on AS screen_on
        FROM pecks p
        WHERE p.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d'
    ) subquery
    WHERE subquery.in_circle = TRUE AND subquery.screen_on = TRUE
)
SELECT 
    pecks_in_circle.num_in_circle,
    sessions_info.reinforcement_ratio,
    CASE 
        WHEN pecks_in_circle.num_in_circle = sessions_info.reinforcement_ratio THEN TRUE
        ELSE FALSE
    END AS green_number_accurate
FROM pecks_in_circle, sessions_info;

SELECT *
FROM rounds r JOIN sessions s ON r.session_id = s.session_id 
ORDER BY started_at DESC
LIMIT 2;

SELECT
  r.round_id AS round_id,
  r.round_index AS round_index,
  r.warning_index AS warning_index,
  r.warning_quarter AS warning_quarter,
  COUNT(CASE WHEN e.event_type = 'green' AND e.warning_signal_present = TRUE THEN 1 END) AS risky_green,
  COUNT(CASE WHEN e.event_type = 'green' THEN 1 END) AS green_count,
    CASE 
    WHEN COUNT(CASE WHEN e.event_type = 'warning' THEN 1 END) = 1 THEN TRUE 
    ELSE FALSE 
  END AS was_warned,
  CASE 
    WHEN COUNT(CASE WHEN e.event_type = 'red' THEN 1 END) = 1 THEN TRUE 
    ELSE FALSE 
  END AS warning_terminated,
  CASE 
    WHEN COUNT(CASE WHEN e.event_type = 'punishment' THEN 1 END) = 1 THEN TRUE 
    ELSE FALSE 
  END AS was_punished, 
  CASE 
    WHEN COUNT(CASE WHEN e.event_type = 'feeding' THEN 1 END) = 1 THEN TRUE 
    ELSE FALSE 
  END AS was_fed
  FROM events e
JOIN rounds r ON e.round_id = r.round_id
WHERE e.round_id = (
  SELECT r.round_id
  FROM rounds r
  ORDER BY started_at DESC
  LIMIT 1
  OFFSET 1
)
GROUP BY r.round_id;


SELECT * FROM events e
WHERE e.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d';

SELECT * FROM rounds r
WHERE r.round_id = 'f2f2526c-f0b8-403d-926a-e1faaf25da8d';


select * from events 
where event_type = 'warning'
