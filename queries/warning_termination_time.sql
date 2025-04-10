SELECT 
    e.round_id, r.started_at,
    MAX(CASE WHEN e.event_type = 'warning' THEN e.event_time END) AS warning_start_time,
    MAX(CASE WHEN e.event_type = 'red' THEN e.event_time END) AS warning_end_time,
    EXTRACT(EPOCH FROM 
        COALESCE(MAX(CASE WHEN e.event_type = 'red' THEN e.event_time END), 'epoch') - 
        COALESCE(MAX(CASE WHEN e.event_type = 'warning' THEN e.event_time END), 'epoch')
    ) AS warning_duration_seconds
FROM events e
JOIN rounds r ON r.round_id = e.round_id
WHERE r.session_id = '99bcaa29-7a28-4690-9adf-4dfe27202a64'
GROUP BY e.round_id, r.started_at
ORDER BY r.started_at