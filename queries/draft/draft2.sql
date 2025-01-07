SELECT * FROM events e
JOIN rounds r ON e.round_id = r.round_id
WHERE r.session_id = (
    SELECT session_id FROM rounds
    ORDER BY created_at DESC
    LIMIT 1
)
ORDER BY e.created_at