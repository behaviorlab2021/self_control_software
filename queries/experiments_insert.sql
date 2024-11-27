INSERT INTO experiments (
    reinforcement_ratio,
    warning_signal_points,
    warning_pecks,
    punishment_period,
    feed_time,
    total_reinforcements,
    skip_to_next_value,
    warning_alarm_volume,
    warning_display_volume,
    punishment_condition,
    subject,
    is_spot_on,
    random_warning,
    miliseconds_after_touch,
    in_warning_signal_training,
    regular_rounds_before_warning_signal_training,
    warning_duration,
    time_before_warning_signal,
    highlight_warning_signal,
    warning_signal_position,
    comments
) VALUES (
    10,                -- reinforcement_ratio
    5,                 -- warning_signal_points
    3,                 -- warning_pecks
    60,                -- punishment_period (in seconds)
    120,               -- feed_time (in seconds)
    15,                -- total_reinforcements
    1,                 -- skip_to_next_value
    0.75,              -- warning_alarm_volume
    0.80,              -- warning_display_volume
    1,                 -- punishment_condition
    'Subject_001',     -- subject
    TRUE,              -- is_spot_on
    FALSE,             -- random_warning
    250,               -- miliseconds_after_touch
    TRUE,              -- in_warning_signal_training
    10,                -- regular_rounds_before_warning_signal_training
    30,                -- warning_duration (in seconds)
    10,                -- time_before_warning_signal (in seconds)
    TRUE,              -- highlight_warning_signal
    2.34567,           -- warning_signal_position
    'First experiment run' -- comments
);
