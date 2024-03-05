from flask import jsonify
from os import environ as env
import os
import pyodbc
from dotenv import find_dotenv, load_dotenv
import sys
from retry import retry

# script_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(script_dir)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

connection_string = env.get("AZURE_SQL_CONNECTIONSTRING")


@retry(Exception, tries=3, delay=1, backoff=2)
def get_conn():
    conn = pyodbc.connect(connection_string)
    return conn


def create_forum_post():
    print("Create Forum Post")
    try:
        conn = get_conn()
        cursor = conn.cursor()

        print("connected")
        # Table should be created ahead of time in production app.
        cursor.execute("""
            CREATE TABLE forum_posts (
                id int NOT NULL PRIMARY KEY IDENTITY,
                user_id varchar(255) NOT NULL FOREIGN KEY REFERENCES Users(User_ID),
                title text NOT NULL,
                message text,
                post_time datetime NOT NULL
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


def create_reply_log():
    print("Create Reply Log")
    try:
        conn = get_conn()
        cursor = conn.cursor()

        print("connected")
        # Table should be created ahead of time in production app.
        cursor.execute("""
            CREATE TABLE reply_log (
                id int NOT NULL PRIMARY KEY IDENTITY,
                post_id int NOT NULL FOREIGN KEY REFERENCES forum_posts(id),
                user_id varchar(255) NOT NULL FOREIGN KEY REFERENCES Users(User_ID),
                sent_time datetime NOT NULL,
                message text NOT NULL
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


# def get_all_posts():
#     posts = []
#     try:
#         conn = get_conn()
#         cursor = conn.cursor()
#         print("connected")
#         cursor.execute("""SELECT * FROM forum_posts""")
#         posts = cursor.fetchall()
#     except Exception as e:
#         # Table may already exist
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#         print(e)
#     return posts


def post(new_post):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                INSERT INTO forum_posts (user_id, title, message, post_time) VALUES (?, ?, ?, GETDATE())
            """, (new_post['user_id'], new_post['title'], new_post['message']))
        conn.commit()
        return jsonify({"success": True, "message": "Post added successfully."})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return jsonify({"success": False, "message": str(e)})


def reply(new_reply):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                INSERT INTO reply_log (user_id, post_id, sent_time, message) VALUES (?, ?, GETDATE(), ?)
            """, (new_reply['user_id'], new_reply['post_id'], new_reply['message']))
        conn.commit()
        return jsonify({"success": True, "message": "Message sent successfully."})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return jsonify({"success": False, "message": str(e)})


def get_active_posts(user = None):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        if user == None:
            cursor.execute("""
                    SELECT * FROM forum_posts JOIN Users ON Users.USER_ID = forum_posts.user_id WHERE is_active = 1
                """)
        else:
            cursor.execute("""
                    SELECT * FROM forum_posts JOIN Users ON Users.USER_ID = forum_posts.user_id WHERE is_active = 1 AND Users.user_id = ?
                """, (user))
        posts = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = []
        for row in posts:
            data.append(dict(zip(columns, row)))
        return jsonify({"success": True, "data": data})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


def deactivate_post(id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                    UPDATE forum_posts SET is_active = 0 WHERE id = ?
            """, (id))
        conn.commit()
        return jsonify({"success": True, "message": f"post {id} deleted"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


def get_reply(post_id):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                SELECT * FROM reply_log JOIN Users ON Users.USER_ID = reply_log.user_id WHERE post_id = ?
            """, (post_id))
        messages = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        data = []
        for row in messages:
            data.append(dict(zip(columns, row)))
        return jsonify({"success": True, "data": data})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


def ad_hoc():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        print("connected")
        cursor.execute("""
                ALTER TABLE forum_posts 
                ADD is_active bit NOT NULL
                CONSTRAINT DF_isactive_1 DEFAULT 1
                """)
        conn.commit()
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    get_active_posts()
