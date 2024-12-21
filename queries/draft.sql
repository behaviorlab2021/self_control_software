CREATE OR REPLACE FUNCTION get_round_statistics(p_round_id UUID)
RETURNS TABLE (
    round_id UUID,
    outcome_valid BOOLEAN,
    green_pecks_valid BOOLEAN,
    red_pecks_valid BOOLEAN,
    feedback_time_valid BOOLEAN,
    pecks_until_warning_valid BOOLEAN,
    quarter_valid BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH 
    sessions_info AS (
        SELECT s.reinforcement_ratio, s.button_height, s.warning_signal_position
        FROM rounds r
        JOIN sessions s ON r.session_id = s.session_id
        WHERE r.round_id = p_round_id
    ),
    pecks_in_green AS (
        SELECT COUNT(*) AS peck_count
        FROM (
            SELECT is_in_circle(p.x_pos, p.y_pos, 0.15, 0.7, (SELECT button_height FROM sessions_info)/100.0) AS in_circle, 
                   p.screen_on AS screen_on
            FROM pecks p
            WHERE p.round_id = p_round_id
        ) subquery
        WHERE subquery.in_circle = TRUE AND subquery.screen_on = TRUE
    ),
    pecks_in_red AS (
        SELECT COUNT(*) AS peck_count
        FROM (
            SELECT is_in_circle(p.x_pos, p.y_pos, 0.15, 0.3 + (SELECT warning_signal_position FROM sessions_info)/100.0 * 0.4, (SELECT button_height FROM sessions_info)/100.0) AS in_circle, 
                   p.screen_on AS screen_on
            FROM pecks p
            WHERE p.round_id = p_round_id
        ) subquery
        WHERE subquery.in_circle = TRUE AND subquery.screen_on = TRUE
    ),
    timely_events AS (
        SELECT 
            e.round_id, 
            MAX(CASE WHEN e.event_type = 'punishment' THEN e.event_time END) AS punishment_time,
            MAX(CASE WHEN e.event_type = 'punishment_end' THEN e.event_time END) AS punishment_end_time,
            MAX(CASE WHEN e.event_type = 'feeding' THEN e.event_time END) AS feeding_time,
            MAX(CASE WHEN e.event_type = 'feeding_end' THEN e.event_time END) AS feeding_end_time
        FROM events e
        GROUP BY e.round_id
    ),
    warning_event_time AS (
        SELECT e.event_time
        FROM events e
        WHERE e.event_type = 'warning'
        AND e.round_id = p_round_id
        LIMIT 1
    ),
    green_events_until_warning AS (
        SELECT
            COUNT(*) AS green_count_until_warning
        FROM events e
        WHERE e.event_type = 'green'
        AND e.round_id = p_round_id
        AND e.event_time < (SELECT event_time FROM warning_event_time)
    )
    SELECT
        e.round_id,
        CASE
            WHEN COUNT(CASE WHEN e.event_type = 'red' THEN 1 END) = 0 
                 AND COUNT(CASE WHEN e.event_type = 'green' THEN 1 END) < s.reinforcement_ratio 
                 AND COUNT(CASE WHEN e.event_type = 'green' AND e.warning_signal_present = TRUE THEN 1 END) > s.warning_hits THEN TRUE
            WHEN COUNT(CASE WHEN e.event_type = 'red' THEN 1 END) = 1 
                 AND COUNT(CASE WHEN e.event_type = 'green' THEN 1 END) = s.reinforcement_ratio 
                 AND COUNT(CASE WHEN e.event_type = 'green' AND e.warning_signal_present = TRUE THEN 1 END) < s.warning_hits THEN TRUE
            ELSE FALSE
        END AS outcome_valid,
        CASE
            WHEN COUNT(CASE WHEN e.event_type = 'green' THEN 1 END) = pecks_in_green.peck_count THEN TRUE
            ELSE FALSE
        END AS green_pecks_valid,
        CASE
            WHEN COUNT(CASE WHEN e.event_type = 'red' THEN 1 END) = pecks_in_red.peck_count THEN TRUE
            ELSE FALSE
        END AS red_pecks_valid,
        CASE
            WHEN COUNT(CASE WHEN e.event_type = 'red' THEN 1 END) = 0 
                 AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - s.punishment_duration) <= 0.2 THEN TRUE
            WHEN COUNT(CASE WHEN e.event_type = 'red' THEN 1 END) = 1 
                 AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - s.feed_time) <= 0.2 THEN TRUE
            ELSE FALSE
        END AS feedback_time_valid,
        CASE
            WHEN (SELECT green_count_until_warning FROM green_events_until_warning) = (SELECT warning_index FROM rounds r WHERE r.round_id = p_round_id) THEN TRUE
            ELSE FALSE
        END AS pecks_until_warning_valid,
        CASE
            WHEN (SELECT warning_quarter FROM rounds r WHERE r.round_id = p_round_id) = 
                 FLOOR((SELECT warning_index FROM rounds r WHERE r.round_id = p_round_id)::float / (SELECT reinforcement_ratio FROM sessions s WHERE s.session_id = (SELECT session_id FROM rounds r WHERE r.round_id = p_round_id))::float * 4) + 1 THEN TRUE
            ELSE FALSE
        END AS quarter_valid
    FROM
        events e
    JOIN
        rounds r ON e.round_id = r.round_id
    JOIN
        sessions s ON r.session_id = s.session_id
    JOIN
        pecks_in_green ON TRUE
    JOIN
        pecks_in_red ON TRUE
    JOIN
        timely_events te ON e.round_id = te.round_id
    WHERE
        e.round_id = p_round_id
    GROUP BY
        e.round_id, s.session_id, pecks_in_green.peck_count, pecks_in_red.peck_count;
END;
$$ LANGUAGE plpgsql;