CREATE TABLE errors (
    error_id UUID UNIQUE PRIMARY KEY DEFAULT gen_random_uuid(),
    error_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    round_id UUID REFERENCES rounds(round_id),
    session_id UUID REFERENCES sessions(session_id),
    CHECK (session_id IS NOT NULL OR round_id IS NOT NULL)
);

CREATE OR REPLACE FUNCTION log_error_with_session_id(session_id UUID, error_message TEXT) RETURNS VOID AS $$
BEGIN
    INSERT INTO errors (session_id, error_message) VALUES (session_id, error_message);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION log_error_with_round_id(round_id UUID, error_message TEXT) RETURNS VOID AS $$
BEGIN
    INSERT INTO errors (round_id, error_message) VALUES (round_id, error_message);
END;
$$ LANGUAGE plpgsql;


