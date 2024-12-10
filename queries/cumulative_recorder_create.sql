CREATE TABLE cumulative_record (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- Unique identifier for the event
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),          -- Time of the event
    hit_count INTEGER,                                    -- Number of hit_count
    experiment_id UUID REFERENCES experiments(experiment_id) -- Foreign key to experiments table
);
