from flask import jsonify
from os import environ as env
import os
import pyodbc
from dotenv import find_dotenv, load_dotenv
import sys
from retry import retry

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

connection_string = env.get("AZURE_SQL_CONNECTIONSTRING")


@retry(Exception, tries=3, delay=1, backoff=2)
def get_conn():
    conn = pyodbc.connect(connection_string)
    return conn


def create_partner_post():
    print("Create Partner Post")
    try:
        conn = get_conn()
        cursor = conn.cursor()

        print("connected")
        # Table should be created ahead of time in production app.
        cursor.execute("""
            CREATE TABLE workout_posts (
                id int NOT NULL PRIMARY KEY IDENTITY,
                user_id varchar(255) NOT NULL FOREIGN KEY REFERENCES Users(User_ID),
                workout_id int NOT NULL,
                location varchar(255) NOT NULL,
                start_time datetime NOT NULL,
                end_time datetime NOT NULL,
                post_time datetime NOT NULL,
                message text
            );
        """)

        conn.commit()
    except Exception as e:
        # Table may already exist
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    return 


# def create_message_log():
#     print("Create Message Log")
#     try:
#         conn = get_conn()
#         cursor = conn.cursor()

#         print("connected")
#         # Table should be created ahead of time in production app.
#         cursor.execute("""
#             CREATE TABLE message_log (
#                 id int NOT NULL PRIMARY KEY IDENTITY,
#                 post_id int NOT NULL FOREIGN KEY REFERENCES workout_posts(id),
#                 user_id varchar(255) NOT NULL FOREIGN KEY REFERENCES Users(ID),
#                 sent_time datetime,
#                 message text
#             );
#         """)

#         conn.commit()
#     except Exception as e:
#         # Table may already exist
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#     return 


def get_all_invitations():
    posts = []
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""SELECT * FROM workout_posts""")
        posts = cursor.fetchall()
    except Exception as e:
        # Table may already exist
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    return posts


def post_invitation(new_invitation):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                INSERT INTO workout_posts (user_id, workout_name, location, start_time, end_time, post_time, message) VALUES (?, ?, ?, ?, ?, GETDATE(), ?)
            """, (new_invitation['user_id'], new_invitation['workout_name'], new_invitation['location'], 
                  new_invitation['start_time'].strftime('%Y-%m-%d %H:%M:%S'), new_invitation['end_time'].strftime('%Y-%m-%d %H:%M:%S'), new_invitation['message']))
        conn.commit()
        return jsonify({"success": True, "message": "Post added successfully."})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return jsonify({"success": False, "message": str(e)})


def post_new_message(new_message):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                INSERT INTO message_log (user_id, post_id, receiver_id, sent_time, message) VALUES (?, ?, ?, GETDATE(), ?)
            """, (new_message['user_id'], new_message['post_id'], new_message['receiver_id'], new_message['message']))
        conn.commit()
        print ("new message added")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    return


def get_posts(user):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                SELECT * FROM workout_posts WHERE user_id = ?
            """, (user))
        posts = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = []
        for row in posts:
            data.append(dict(zip(columns, row)))
        return jsonify({"success": True, "data": data})
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return jsonify({"success": False, "message": str(e)})


def get_message(user):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                SELECT * FROM message_log WHERE user_id = ? OR receiver_id = ?
            """, (user, user))
        messages = cursor.fetchall()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    return messages


def ad_hoc():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                ALTER TABLE workout_posts DROP COLUMN workout_id """)
        cursor.execute("""ALTER TABLE workout_posts ADD workout_name varchar(255)""")
        conn.commit()
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    ad_hoc()