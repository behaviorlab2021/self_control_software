CREATE OR REPLACE FUNCTION notify_cumulative_recorder_event() RETURNS trigger AS $$
BEGIN
    RAISE NOTICE 'Trigger notify_cumulative_recorder_event executed for record: %', row_to_json(NEW)::text; -- Debug print
    PERFORM pg_notify('new_cumulative_recorder_event', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cumulative_recorder_event_trigger
AFTER INSERT ON cumulative_recorder
FOR EACH ROW
EXECUTE FUNCTION notify_cumulative_recorder_event();
