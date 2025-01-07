-- Create pecks table
CREATE TABLE pecks (
    peck_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	x_start FLOAT NOT NULL, 
	y_start FLOAT NOT NULL,
    x_pos FLOAT NOT NULL,
    y_pos FLOAT NOT NULL,
    screen_on BOOLEAN NOT NULL,
    green_on BOOLEAN NOT NULL,
    red_on BOOLEAN NOT NULL,
    peck_time TIMESTAMP NOT NULL DEFAULT NOW(),
    round_id UUID REFERENCES rounds(round_id) NOT NULL
);





CREATE OR REPLACE FUNCTION notify_peck() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('new_peck', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER peck_trigger
AFTER INSERT ON pecks
FOR EACH ROW
EXECUTE FUNCTION notify_peck();