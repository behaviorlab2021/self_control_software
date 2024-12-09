INSERT INTO experiments (
    reinforcement_ratio,
    warning_pecks,
    punishment_duration,
    feed_time,
    total_reinforcements,
    consecutive_warnings_limit,
    warning_alarm_volume,
    warning_display_volume,
    subject_id,
    mode_id,
    is_spot_on,
    rounds_before_warning,
    warning_duration,
    time_before_warning_signal,
    highlight_warning_signal,
    warning_signal_position,
    comments
) VALUES (
    10,                -- reinforcement_ratio
    3,                 -- warning_pecks
    60,                -- punishment_duration (in seconds)
    120,               -- feed_time (in seconds)
    15,                -- total_reinforcements
    1,                 -- consecutive_warnings_limit
    0.75,              -- warning_alarm_volume
    0.80,              -- warning_display_volume
    1,                 -- subject_id (example value)
    1,                 -- mode_id (example value)
    TRUE,              -- is_spot_on
    10,                -- rounds_before_warning
    30,                -- warning_duration (in seconds)
    10,                -- time_before_warning_signal (in seconds)
    TRUE,              -- highlight_warning_signal
    2.34567,           -- warning_signal_position
    'First experiment run' -- comments
);


INSERT INTO experiments (
	experiment_id,
    reinforcement_ratio,
    warning_pecks,
    punishment_duration,
    feed_time,
    total_reinforcements,
    consecutive_warnings_limit,
    warning_alarm_volume,
    warning_display_volume,
    subject_id,
    mode_id,
    is_spot_on,
    rounds_before_warning,
    warning_duration,
    time_before_warning_signal,
    highlight_warning_signal,
    warning_signal_position,
    comments
) VALUES (
	'fde42ce6-5d6e-402d-ac02-aae568e80a46', -- uuid
    10,                -- reinforcement_ratio
    3,                 -- warning_pecks
    60,                -- punishment_duration (in seconds)
    120,               -- feed_time (in seconds)
    15,                -- total_reinforcements
    1,                 -- consecutive_warnings_limit
    0.75,              -- warning_alarm_volume
    0.80,              -- warning_display_volume
    1,                 -- subject_id (example value)
    1,                 -- mode_id (example value)
    TRUE,              -- is_spot_on
    10,                -- rounds_before_warning
    30,                -- warning_duration (in seconds)
    10,                -- time_before_warning_signal (in seconds)
    TRUE,              -- highlight_warning_signal
    2.34567,           -- warning_signal_position
    'First experiment run' -- comments
);
