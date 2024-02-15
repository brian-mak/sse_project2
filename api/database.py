from flask import Flask, request
from os import environ as env
import os
import pyodbc
from dotenv import find_dotenv, load_dotenv
import sys

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

connection_string = env.get("AZURE_SQL_CONNECTIONSTRING")

app = Flask(__name__)


@app.get("/")
def root():
    print("Root of User API")
    try:
        conn = get_conn()
        cursor = conn.cursor()

        print("connected")
        # Table should be created ahead of time in production app.
        cursor.execute("""
            CREATE TABLE Users (
                ID int NOT NULL PRIMARY KEY IDENTITY,
                Email varchar(255) NOT NULL,
                Name varchar(255),
                NickName varchar(255),
                LastLogin datetime
            );
        """)

        conn.commit()
    except Exception as e:
        # Table may already exist
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    return "User API"


def get_all_user():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users")
        print(cursor.fetchall())


def update_user_log(info):
    email = info.get("email")
    name = info.get("name")
    nickname = info.get("nickname")

    with get_conn() as conn:
        cursor = conn.cursor()
        #check if email exists
        cursor.execute("SELECT 1 FROM Users WHERE email = ?", email) 
        existing_row = cursor.fetchone()
        if existing_row:
            # If email exists, update lastlogin
            cursor.execute("UPDATE Users SET LastLogin = GETDATE() WHERE email = ?", email)
        else:
            # If email does not exist, insert a new row
            cursor.execute("INSERT INTO Users (Email, Name, NickName, LastLogin) VALUES (?, ?, ?, GETDATE())", email, name, nickname)
        
        conn.commit()

    print(f"user {email} updated.")   


def get_conn():
    conn = pyodbc.connect(connection_string)
    return conn

if __name__ == "__main__":
    get_all_user()