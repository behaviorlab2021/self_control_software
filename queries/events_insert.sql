INSERT INTO events (
    event_time,
    reinforcers,
    quarter,
    pecks,
    event_type,
    x_pos,
    y_pos,
    warning_present
) VALUES (
    '2024-11-27 15:00:00', -- Specific event time
    3,                     -- Reinforcers count
    2,                     -- Quarter
    5,                     -- Pecks
    'stimulus',            -- Type of event
    12.34567,              -- X-coordinate position
    45.67890,              -- Y-coordinate position
    TRUE                   -- Warning present
);
