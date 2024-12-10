CREATE TABLE events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),          -- Time of the event
    reinforcers INTEGER NOT NULL,                         -- Number of reinforcers
    quarter INTEGER NOT NULL,                             -- Quarter of the session or event
    hit_count INTEGER,                                    -- Number of hit_count
    event_type VARCHAR(50) NOT NULL,                      -- Type of event (e.g., "stimulus", "response")
    x_pos DECIMAL(10, 5) NOT NULL,                        -- X-coordinate position
    y_pos DECIMAL(10, 5) NOT NULL,                        -- Y-coordinate position
    warning_present BOOLEAN DEFAULT FALSE,                -- Whether a warning was present
    warning_signal_index INTEGER,                         -- Position of the warning
    experiment_id UUID REFERENCES experiments(experiment_id) -- Foreign key to experiments table
);
