from Database.database_connection import DatabaseConnection

db = DatabaseConnection()
if db.test_connection():
    print("SQL Server connection successful!")
else:
    print("SQL Server connection failed.")
