import sqlite3

conn = sqlite3.connect('voting_system.db')
cursor = conn.cursor()

# Check if voters table exists and its schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='voters'")
voters_schema = cursor.fetchone()

if voters_schema:
    print("Voters table schema:")
    print(voters_schema[0])
else:
    print("Voters table does not exist")

# Check all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\nAll tables:")
for table in tables:
    print(f"- {table[0]}")

conn.close()
