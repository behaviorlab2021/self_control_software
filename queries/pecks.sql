-- Create pecks table
CREATE TABLE pecks (
    peck_id UUID PRIMARY KEY,
    x_pos INTEGER NOT NULL,
    y_pos INTEGER NOT NULL,
    screen_on BOOLEAN NOT NULL,
    peck_time TIMESTAMP NOT NULL,
    round_id UUID REFERENCES rounds(round_id)
);

-- Example insert into pecks table
INSERT INTO pecks (peck_id, x_pos, y_pos, screen_on, peck_time, round_id)
VALUES ('123e4567-e89b-12d3-a456-426614174000', 100, 150, TRUE, '2023-10-01 12:00:00', '123e4567-e89b-12d3-a456-426614174001');

-- Example select from pecks table
SELECT * FROM pecks;    

CREATE OR REPLACE FUNCTION notify_peck_event() RETURNS trigger AS $$
BEGIN
    RAISE NOTICE 'Trigger notify_peck_event executed for record: %', row_to_json(NEW)::text; -- Debug print
    PERFORM pg_notify('new_peck_event', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER peck_event_trigger
AFTER INSERT ON pecks
FOR EACH ROW
EXECUTE FUNCTION notify_peck_event();
