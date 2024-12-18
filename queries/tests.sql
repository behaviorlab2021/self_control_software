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

-- Example insert statement
INSERT INTO round_tests (
    round_test_id, round_id, green_number_accurate, red_number_accurate, 
    valid_green_clicks_equal_hits, valid_red_clicks_equal_warning_terminations, 
    punishment_time_valid, feeding_time_valid, clicks_until_reinforcement, 
    clicks_until_warning, accurate_punishment_time, accurate_feeding_time
) VALUES (
    '123e4567-e89b-12d3-a456-426614174000', '123e4567-e89b-12d3-a456-426614174001', true, false, 
    true, false, true, true, 10, 
    5, 300, 200
);

-- Example select statement
SELECT * FROM round_tests;

-- Function to notify new peck events
CREATE OR REPLACE FUNCTION notify_new_peck_event() RETURNS trigger AS $$
BEGIN
    RAISE NOTICE 'Trigger notify_new_peck_event executed for record: %', row_to_json(NEW)::text; -- Debug print
    PERFORM pg_notify('new_peck_event', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for new peck events
CREATE TRIGGER new_peck_event_trigger
AFTER INSERT ON peck
FOR EACH ROW
EXECUTE FUNCTION notify_new_peck_event();



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

-- Example insert statement
INSERT INTO session_tests (
    session_test_id, session_id, green_number_accurate, red_number_accurate, 
    valid_green_clicks_equal_hits, valid_red_clicks_equal_warning_terminations, 
    punishment_time_valid, feeding_time_valid, clicks_until_reinforcement, 
    clicks_until_warning, accurate_punishment_time, accurate_feeding_time,
    total_reinforcements_test, total_warnings_test
) VALUES (
    '223e4567-e89b-12d3-a456-426614174000', '223e4567-e89b-12d3-a456-426614174001', true, false, 
    true, false, true, true, 15, 
    7, 350, 250, true, false
);

-- Example select statement
SELECT * FROM session_tests;

-- Function to notify new session events
CREATE OR REPLACE FUNCTION notify_new_session_event() RETURNS trigger AS $$
BEGIN
    RAISE NOTICE 'Trigger notify_new_session_event executed for record: %', row_to_json(NEW)::text; -- Debug print
    PERFORM pg_notify('new_session_event', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for new session events
CREATE TRIGGER new_session_event_trigger
AFTER INSERT ON session
FOR EACH ROW
EXECUTE FUNCTION notify_new_session_event();
