SELECT e.*, ex.total_reinforcements, COUNT(DISTINCT e.reinforcers) AS actual_reinforcers_given,
       (SELECT COUNT(DISTINCT reinforcers) 
        FROM events 
        WHERE experiment_id = '28f6096d-cb5e-437c-8e60-0a8089bbcdd9' 
        AND event_type = 'green') AS total_distinct_reinforcers
FROM events e
JOIN experiments ex ON e.experiment_id = ex.experiment_id
WHERE e.experiment_id = '28f6096d-cb5e-437c-8e60-0a8089bbcdd9'
AND e.event_type = 'green'
GROUP BY e.event_id, ex.total_reinforcements;