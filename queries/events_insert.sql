INSERT INTO events (
    event_time,
    reinforcers,
    quarter,
    hit_count,
    event_type,
    x_pos,
    y_pos,
    warning_present,
    warning_signal_index,
    experiment_id
) VALUES (
    '2024-11-27 15:00:00', -- Specific event time
    3,                     -- Reinforcers count
    2,                     -- Quarter
    5,                     -- hit_count
    'stimulus',            -- Type of event
    12.34567,              -- X-coordinate position
    45.67890,              -- Y-coordinate position
    TRUE,                  -- Warning present
    1,                     -- Warning signal index
    '550e8400-e29b-41d4-a716-446655440000' -- Experiment ID (UUID)
);
