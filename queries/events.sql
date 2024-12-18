CREATE TABLE events (
    round_id UUID REFERENCES rounds(round_id),              -- Round Index
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),   -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),            -- Time of the event
    event_type VARCHAR(50) NOT NULL,                        -- Type of event (e.g., "stimulus", "response")
    warning_signal_present BOOLEAN NOT NULL                 -- Whether a warning signal was present
);


INSERT INTO events (
    round_id,
    event_time,
    event_type,
    warning_signal_present
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000', -- Round ID (UUID)
    '2024-11-27 15:00:00',                  -- Specific event time
    'stimulus',                             -- Type of event
    TRUE                                    -- Warning signal present
);


CREATE OR REPLACE FUNCTION notify_event() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('new_event', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER event_trigger
AFTER INSERT ON events
FOR EACH ROW
EXECUTE FUNCTION notify_event();