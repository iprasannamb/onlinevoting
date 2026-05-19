Migration & MySQL Integration

This project uses SQLite by default for local development. To migrate to MySQL (as requested), follow these steps:

1. Install MySQL server and create a database/user.
2. Execute the provided `mysql_schema.sql` to create the required schema:

   mysql -u <user> -p < mysql_schema.sql

3. Install Python MySQL connector in the project's virtualenv:

   pip install mysql-connector-python

4. Update `app.py` to use MySQL connection parameters or set environment variables and adjust `get_db()` to connect to MySQL.

Notes:
- The repository still ships code that uses SQLite for local development. The MySQL schema file is provided and is compatible with the updated ECI workflow.
- If you want, I can update `app.py` to support an optional MySQL connection via environment variables (and add `mysql-connector-python` to `requirements.txt`). Tell me if you want me to proceed with that change and provide your MySQL connection details or preferred env var names.
