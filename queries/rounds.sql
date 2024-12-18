CREATE TABLE rounds (
    session_id UUID REFERENCES sessions(session_id),
    round_id UUID PRIMARY KEY,
    round_index INTEGER NOT NULL,
    warning_index INTEGER NOT NULL,
    warning_quarter INTEGER NOT NULL,
    reinforcers_count INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL
);

-- Insert a new round
INSERT INTO rounds (session_id, round_id, round_index, warning_index, warning_quarter, reinforcers_count, started_at)
VALUES ('123e4567-e89b-12d3-a456-426614174000', '123e4567-e89b-12d3-a456-426614174001', 1, 2, 3, 4, '2023-10-01 10:00:00');

-- Select the last round
SELECT * FROM rounds
ORDER BY round_index DESC
LIMIT 1;

-- Select all rounds
SELECT * FROM rounds;

CREATE OR REPLACE FUNCTION notify_new_round_event() RETURNS trigger AS $$
BEGIN
    RAISE NOTICE 'Trigger notify_new_round_event executed for record: %', row_to_json(NEW)::text; -- Debug print
    PERFORM pg_notify('new_round_event', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER new_round_event_trigger
AFTER INSERT ON rounds
FOR EACH ROW
EXECUTE FUNCTION notify_new_round_event();

