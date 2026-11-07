import sqlite3

connection = sqlite3.connect("panda_practice.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nhs_number TEXT NOT NULL UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
    )
""")

connection.commit()
print("Patients table created successfully")

cursor.execute(
    """
    INSERT OR IGNORE INTO patients (nhs_number, first_name, last_name)
    VALUES (?, ?, ?)
    """,
    ("9434765919", "John", "Smith"),
)

connection.commit()

cursor.execute(
    "SELECT * FROM patients WHERE nhs_number = ?",
    ("9434765919",),
)

patient = cursor.fetchone()

print(f"patient db record as tuple:\n {patient}")

connection.close()
