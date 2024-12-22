

-- CREATE OR REPLACE FUNCTION is_in_circle(
--     x_position DOUBLE PRECISION,
--     y_position DOUBLE PRECISION,
--     radius DOUBLE PRECISION,
--     center_x DOUBLE PRECISION,
--     center_y DOUBLE PRECISION,
--     aspect_ratio FLOAT DEFAULT 1.0
-- )
-- RETURNS BOOLEAN AS $$
-- BEGIN
--     RETURN (POWER((x_position - center_x) * aspect_ratio , 2)+ POWER(y_position - center_y, 2)) <= POWER(radius, 2);
-- END;
-- $$ LANGUAGE plpgsql;





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
        SELECT is_in_circle(p.x_pos, p.y_pos, 0.075, 0.7, (SELECT button_height FROM sessions_info)/100.0, aspect_ratio) AS in_circle, 
               p.screen_on AS screen_on,
			   p.green_on AS green_on
        FROM pecks p
        JOIN round_id ON p.round_id = round_id.id
    ) subquery
    WHERE subquery.in_circle = TRUE AND subquery.screen_on AND subquery.green_on = TRUE
),
pecks_in_red AS (
    SELECT COUNT(*) AS peck_count
    FROM (
        SELECT is_in_circle(p.x_pos, p.y_pos, 0.075, 0.3 + (SELECT warning_signal_position FROM sessions_info)/100.0 * 0.4, (SELECT button_height FROM sessions_info)/100.0, aspect_ratio) AS in_circle, 
               p.screen_on AS screen_on,
			   p.red_on AS red_on
        FROM pecks p
        JOIN round_id ON p.round_id = round_id.id
    ) subquery
    WHERE subquery.in_circle = TRUE AND subquery.screen_on AND subquery.red_on = TRUE
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
        quarter_valid
    )
    SELECT
        events.round_id,
        CASE
            WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0 
                 AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) < sessions.reinforcement_ratio 
                 AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) > sessions.warning_hits THEN TRUE
            WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1 
                 AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = sessions.reinforcement_ratio 
                 AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) <= sessions.warning_hits THEN TRUE
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
        END AS quarter_valid
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