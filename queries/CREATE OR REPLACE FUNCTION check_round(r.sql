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
													
                   distance_between(p.x_start, p.y_start, p.x_pos, p.y_pos) > (SELECT peck_slide FROM session_info) AS peck_slides,
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
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) < rounds.required_clicks
                         AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) > sessions.warning_hits THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) = rounds.required_clicks
                         AND COUNT(CASE WHEN events.event_type = 'green' AND events.warning_signal_present = TRUE THEN 1 END) <= sessions.warning_hits THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0 
                         AND COUNT(CASE WHEN events.event_type = 'green' THEN 1 END) < sessions.reinforcement_ratio 
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
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0 
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - sessions.punishment_duration) <= 0.2 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1 
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 0.2 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0 
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - sessions.punishment_duration) <= 0.2 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1 
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 0.2 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'warning' THEN 1 END) = 0 
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 0.2 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1 
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 0.2 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0 
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - sessions.punishment_duration) <= 0.2 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 5 THEN
                CASE
                    WHEN ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 0.2 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 2 THEN
                CASE
                    WHEN ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 0.2 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 1 THEN
                CASE
                    WHEN ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 0.2 THEN TRUE
                    ELSE FALSE
                END
            ELSE FALSE
        END AS feedback_period_valid,

        CASE
            WHEN session_info.mode_id = 6 THEN
                CASE
                    WHEN (SELECT green_count_until_warning FROM green_events_until_warning) = (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN
                CASE
                    WHEN (SELECT green_count_until_warning FROM green_events_until_warning) = (SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id)) THEN TRUE
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
                    WHEN (SELECT warning_quarter FROM rounds WHERE round_id = (SELECT id FROM round_id)) = 
                         FLOOR((SELECT warning_index FROM rounds WHERE round_id = (SELECT id FROM round_id))::float / (SELECT reinforcement_ratio FROM sessions WHERE session_id = (SELECT session_id FROM rounds WHERE round_id = (SELECT id FROM round_id)))::float * 4) + 1 THEN TRUE
                    ELSE FALSE
                END
            WHEN session_info.mode_id = 4 THEN 
                CASE
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

