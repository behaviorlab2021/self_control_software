CREATE TABLE cumulative_record (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),          -- Time of the event
    hit_count INTEGER,                                    -- Number of hit_count
    session_id UUID REFERENCES sessions(session_id) -- Foreign key to experiments table
);

INSERT INTO cumulative_record (hit_count, experiment_id)
VALUES (5, '123e4567-e89b-12d3-a456-426614174000');

SELECT * FROM cumulative_record;

CREATE OR REPLACE FUNCTION notify_cumulative_record_event() RETURNS trigger AS $$
BEGIN
    RAISE NOTICE 'Trigger notify_cumulative_record_event executed for record: %', row_to_json(NEW)::text; -- Debug print
    PERFORM pg_notify('new_cumulative_record_event', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cumulative_record_event_trigger
AFTER INSERT ON cumulative_record
FOR EACH ROW
EXECUTE FUNCTION notify_cumulative_record_event();
