-- SELECT_BY_ID:
SELECT *
FROM patients
WHERE id = ?;

-- SELECT_ALL:
SELECT *
FROM patients;

-- INSERT:
INSERT INTO patients (
    nhs_number,
    first_name,
    last_name,
    date_of_birth,
    postcode
)
VALUES (?, ?, ?, ?, ?);

-- DELETE_BY_ID:
DELETE FROM patients
WHERE id = ?;

-- UPDATE:
UPDATE patients
SET
    nhs_number = ?,
    first_name = ?,
    last_name = ?,
    date_of_birth = ?,
    postcode = ?
WHERE id = ?;

-- SELECT_BY_NHS_NUMBER:
SELECT *
FROM patients
WHERE nhs_number = ?;