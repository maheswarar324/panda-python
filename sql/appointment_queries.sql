-- SELECT_BY_ID:
SELECT *
FROM appointments
WHERE id = ?;

-- SELECT_BY_PATIENT_ID:
SELECT *
FROM appointments
WHERE patient_id = ?
ORDER BY start_time;

-- INSERT:
INSERT INTO appointments (
    patient_id,
    start_time,
    end_time,
    status
)
VALUES (?, ?, ?, ?);

-- UPDATE:
UPDATE appointments
SET
    patient_id = ?,
    start_time = ?,
    end_time = ?,
    status = ?
WHERE id = ?;

-- DELETE_BY_ID:
DELETE FROM appointments
WHERE id = ?;