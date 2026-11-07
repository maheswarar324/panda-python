import sqlite3
from datetime import date

from panda.models.patient import Patient

connection = sqlite3.connect("panda_practice.db")

# Configure row factory before creating cursor
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nhs_number TEXT NOT NULL UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth date NOT NULL,
        postcode TEXT NOT NULL
    )
""")

connection.commit()
print("Patients table created successfully")

cursor.execute("DELETE FROM patients")
# Insert patient
cursor.execute(
    """
    INSERT INTO patients (nhs_number, first_name, last_name, date_of_birth, postcode)
    VALUES (?, ?, ?, ?, ?)
    """,
    ("9434765919", "John", "Smith", date.fromisoformat("1990-05-20"), "SW1A 1AA"),
)

connection.commit()

# Retrieve patient
cursor.execute(
    "SELECT * FROM patients WHERE nhs_number = ?",
    ("9434765919",),
)

patient = cursor.fetchone()

print("Access database columns by name")
# print(patient["id"])
# print(patient["nhs_number"])
# print(patient["first_name"])
# print(patient["last_name"])
# print(patient["date_of_birth"])
# print(patient["postcode"])

patient_object = Patient(
    id=patient["id"],
    nhs_number=patient["nhs_number"],
    first_name=patient["first_name"],
    last_name=patient["last_name"],
    date_of_birth=date.fromisoformat(patient["date_of_birth"]),
    postcode=patient["postcode"],
)

print(patient_object)

connection.close()
