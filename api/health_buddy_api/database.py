import pyodbc
from os import environ as env
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

connection_string = env.get("DATABASE_CONNECTION_STRING")

def get_connection():
    return pyodbc.connect(connection_string)

def insert_data(data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Example: Insert data into a table
        cursor.execute("INSERT INTO table_name (column1, column2) VALUES (?, ?)", (data['value1'], data['value2']))
        conn.commit()
        return True
    except Exception as e:
        print("Error:", str(e))
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_data():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Example: Fetch data from a table
        cursor.execute("SELECT * FROM table_name")
        rows = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    except Exception as e:
        print("Error:", str(e))
        return []
    finally:
        cursor.close()
        conn.close()
