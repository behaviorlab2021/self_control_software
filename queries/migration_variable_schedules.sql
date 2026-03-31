-- ============================================================
-- Migration script for variable_schedules branch
-- Run this on an EXISTING database to apply all changes.
-- Safe to run multiple times (idempotent).
-- ============================================================

-- 1. New experiment modes
INSERT INTO experiment_modes (mode_name, mode_id) VALUES
('VARIABLE RATIO', 5),
('VARIABLE WARNING', 6)
ON CONFLICT DO NOTHING;

-- 2. New column: rounds.required_clicks (for modes 5 and 6)
ALTER TABLE rounds ADD COLUMN IF NOT EXISTS required_clicks INTEGER;

-- 3. New columns: sessions.warning_q1/q2/q3 (for mode 6 quartile computation)
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS warning_q1 INTEGER;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS warning_q2 INTEGER;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS warning_q3 INTEGER;

-- 4. New columns on session_checks (synced from checks.sql)
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS session_end_valid BOOLEAN;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS total_time_valid BOOLEAN;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS database_errors INT;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS total_reinforcements INT;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS total_rounds INT;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS total_punishments INT;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS total_warning_terminations INT;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS total_warning_presentations INT;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS total_warning_switches INT;
ALTER TABLE session_checks ADD COLUMN IF NOT EXISTS total_time INTERVAL;


-- ============================================================
-- 5. Updated functions
-- These use CREATE OR REPLACE so they safely overwrite old versions.
-- ============================================================

-- 5a. count_consecutive_unterminated_warnings
-- Changed: excludes free rounds (warning_index < 0)
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


-- 5b. check_round
-- Changed: modes 5/6 use rounds.required_clicks instead of sessions.reinforcement_ratio
-- Changed: modes 4/6 handle free rounds (warning_index < 0)
-- Changed: mode 6 quarter_valid uses warning_q1/q2/q3 from sessions
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
                End
            WHEN session_info.mode_id = 3 THEN
                CASE
                    WHEN COUNT(CASE WHEN events.event_type = 'warning' THEN 1 END) = 0
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 1
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.feeding_end_time) - MAX(timely_events.feeding_time))) - sessions.feed_time) <= 1 THEN TRUE
                    WHEN COUNT(CASE WHEN events.event_type = 'red' THEN 1 END) = 0
                         AND ABS(EXTRACT(EPOCH FROM (MAX(timely_events.punishment_end_time) - MAX(timely_events.punishment_time))) - sessions.punishment_duration) <= 1 THEN TRUE
                    ELSE FALSE
                End
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


-- 5c. check_session
-- Changed: modes 5/6 handling, free round exclusion in warning counts
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
