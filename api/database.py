from flask import Flask, jsonify, request, Blueprint
from os import environ as env
import os
import pyodbc
from dotenv import find_dotenv, load_dotenv
import sys
import requests
from retry import retry

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

connection_string = env.get("AZURE_SQL_CONNECTIONSTRING")

db_bp = Blueprint('db', __name__)

def get_rapid_api_key():
    return os.environ.get('RAPID_API_KEY')

@db_bp.get("/")
def root():
    print("Root of User API")
    try:
        conn = get_conn()
        cursor = conn.cursor()

        print("connected")
        # Table should be created ahead of time in production app.
        cursor.execute("""
            CREATE TABLE Users (
                ID int NOT NULL IDENTITY,
                User_ID varchar(255) NOT NULL PRIMARY KEY,
                Email varchar(255) NOT NULL,
                Name varchar(255),
                NickName varchar(255),
            );
        """)
        conn.commit()
    except Exception as e:
        print(e)
    return "User API"

def get_all_user():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users")
        rows = cursor.fetchall()    

        columns = [column[0] for column in cursor.description]
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))

    return data

def update_user_log(info):
    email = info.get("email")
    name = info.get("name")
    nickname = info.get("nickname")
    user_id = info.get("user_id")

    with get_conn() as conn:
        cursor = conn.cursor()
        #check if user id exists
        cursor.execute("SELECT 1 FROM Users WHERE User_ID = ?", user_id) 
        existing_row = cursor.fetchone()
        if not existing_row:
            # If email exists, update lastlogin
            cursor.execute("INSERT INTO Users (Email, Name, NickName, User_ID) VALUES (?, ?, ?, ?)", email, name, nickname, user_id)
        conn.commit()

    print(f"user {email} updated.")   

@retry(Exception, tries=3, delay=1, backoff=2)
def get_conn():
    conn = pyodbc.connect(connection_string)
    return conn

def create_schema():
    conn = None
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Create Workouts Table
        # cursor.execute("""
        #     IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Workouts]') AND type in (N'U'))
        #     BEGIN
        #         CREATE TABLE Workouts (
        #             WorkoutID int NOT NULL PRIMARY KEY IDENTITY,
        #             Name varchar(255) NOT NULL,
        #             Equipment varchar(255),
        #             TargetMuscleGroup varchar(255),
        #             SecondaryMuscles varchar(255),
        #             Instructions text,
        #             GifUrl varchar(255)
        #         );
        #     END
        # """)

        # Create SavedLists Table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SavedLists]') AND type in (N'U'))
            BEGIN
                CREATE TABLE SavedLists (
                    ListID int NOT NULL PRIMARY KEY IDENTITY,
                    UserID varchar(255) NOT NULL,
                    Name varchar(255) NOT NULL,
                    CreationDate datetime NOT NULL DEFAULT GETDATE(),
                    FOREIGN KEY (UserID) REFERENCES Users(User_ID)
                );
            END
        """)

        # Create SavedListWorkouts Junction Table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SavedListWorkouts]') AND type in (N'U'))
            BEGIN
                CREATE TABLE SavedListWorkouts (
                    ListID int NOT NULL,
                    WorkoutName varchar(255) NOT NULL,
                    PRIMARY KEY (ListID, WorkoutName),
                    FOREIGN KEY (ListID) REFERENCES SavedLists(ListID),
                );
            END
        """)

        conn.commit()
        print("Database schema created/updated successfully.")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(f"Failed to create/update database schema: {e}")
    finally:
        if conn:  # Check if conn is not None
            conn.close()

# @db_bp.route('/workouts/add', methods=['POST'])
# def add_workout():
#     data = request.get_json()
#     try:
#         with get_conn() as conn:
#             cursor = conn.cursor()
#             cursor.execute("""
#                 INSERT INTO Workouts (Name, Equipment, TargetMuscleGroup, SecondaryMuscles, Instructions, GifUrl)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """, (data['name'], data['equipment'], data['targetMuscleGroup'], data['secondaryMuscles'], data['instructions'], data['gifUrl']))
#             conn.commit()
#         return jsonify({"success": True, "message": "Workout added successfully."})
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)})

# # List all workouts
# @db_bp.route('/workouts', methods=['GET'])
# def get_workouts():
#     try:
#         with get_conn() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT * FROM Workouts")
#             workouts = cursor.fetchall()
#         return jsonify([dict(zip([column[0] for column in cursor.description], row)) for row in workouts])
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)})

# # Get details of a specific workout
# @db_bp.route('/workouts/<int:workout_id>', methods=['GET'])
# def get_workout(workout_id):
#     try:
#         with get_conn() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT * FROM Workouts WHERE WorkoutID = ?", (workout_id,))
#             workout = cursor.fetchone()
#         if workout:
#             return jsonify(dict(zip([column[0] for column in cursor.description], workout)))
#         else:
#             return jsonify({"success": False, "message": "Workout not found."})
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)})

# @db_bp.route('/workouts/update/<int:workout_id>', methods=['POST'])
# def update_workout(workout_id):
#     data = request.get_json()
#     try:
#         with get_conn() as conn:
#             cursor = conn.cursor()
#             cursor.execute("""
#                 UPDATE Workouts
#                 SET Name = ?, Equipment = ?, TargetMuscleGroup = ?, SecondaryMuscles = ?, Instructions = ?, GifUrl = ?
#                 WHERE WorkoutID = ?
#             """, (data['name'], data['equipment'], data['targetMuscleGroup'], data['secondaryMuscles'], data['instructions'], data['gifUrl'], workout_id))
#             conn.commit()
#         return jsonify({"success": True, "message": "Workout updated successfully."})
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)})

# @db_bp.route('/workouts/delete/<int:workout_id>', methods=['POST'])
# def delete_workout(workout_id):
#     try:
#         with get_conn() as conn:
#             cursor = conn.cursor()
#             cursor.execute("DELETE FROM Workouts WHERE WorkoutID = ?", (workout_id,))
#             conn.commit()
#         return jsonify({"success": True, "message": "Workout deleted successfully."})
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)})

@db_bp.route('/saved_lists/create', methods=['POST'])
def create_saved_list():
    if request.json:
        user_id = request.json.get('user_id')
        list_name = request.json.get('list_name')
    else:
        user_id = request.form.get('user_id')
        list_name = request.form.get('list_name')

    if not user_id or not list_name:
        return jsonify({"success": False, "message": "Missing required fields."}), 400

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # Check for duplicate list names for the same user
            cursor.execute("""
                SELECT 1 FROM SavedLists WHERE UserID = ? AND Name = ?
            """, (user_id, list_name))
            if cursor.fetchone():
                return jsonify({"success": False, "message": "A list with this name already exists for the user."}), 400
            
            # Proceed with inserting the new saved list
            cursor.execute("""
                INSERT INTO SavedLists (UserID, Name) VALUES (?, ?)
            """, (user_id, list_name))
            conn.commit()
        return jsonify({"success": True, "message": "Saved list created successfully."})
    except pyodbc.IntegrityError as e:
        return jsonify({"success": False, "message": "Database integrity error. Please check the data."}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@db_bp.route('/api/user/saved_lists', methods=['GET'])
def get_saved_lists():
    # Assuming you have a user_id to fetch lists for, perhaps from session or a request parameter
    user_id = request.args.get('user_id')
    if user_id is None:
        return jsonify({"error": "User ID is required"}), 400
    
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM SavedLists WHERE UserID = ?", (user_id,))
            lists = cursor.fetchall()
            saved_lists = [{"list_id": row[0], "name": row[2]} for row in lists]
        return jsonify(saved_lists)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@db_bp.route('/api/saved_lists/<int:list_id>/exercises', methods=['GET'])
def get_exercises_for_list(list_id):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # Fetch workout names associated with the saved list
            cursor.execute("SELECT WorkoutName FROM SavedListWorkouts WHERE ListID = ?", (list_id,))
            workout_names = [row[0] for row in cursor.fetchall()]

        print(workout_names)

        unique_workout_names = list(set(workout_names))
        # Fetch exercise details from the ExerciseDB API
        exercises_details = []
        for name in unique_workout_names:
            details = fetch_exercise_details_from_exercisedb(name)
            if details:
                exercises_details.append(details)

        print(exercises_details)
        return jsonify(exercises_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to fetch exercise details from the ExerciseDB API
def fetch_exercise_details_from_exercisedb(exercise_name):
    api_key = get_rapid_api_key()
    url = "https://exercisedb.p.rapidapi.com/exercises/name/" + exercise_name
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(response.json)
        return response.json()
    else:
        print(f"Failed to fetch exercises: {response.status_code}")
        return None
    

@db_bp.route('/saved_lists/add_workout', methods=['POST'])
def add_workout_to_saved_list():
    list_id = request.json.get('list_id')
    workout_name = request.json.get('workout_name')
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO SavedListWorkouts (ListID, WorkoutName) VALUES (?, ?)", (list_id, workout_name))
            conn.commit()
        return jsonify({"success": True, "message": "Workout added to saved list successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

def ad_hoc():
    conn = get_conn()
    print('connected')
    return   

def delete_users_table():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS Users")
            conn.commit()
            print("Users table deleted successfully.")
    except Exception as e:
        print(f"Failed to delete Users table: {e}")

def delete_workouts_table():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS Workouts")
            conn.commit()
            print("Workouts table deleted successfully.")
    except Exception as e:
        print(f"Failed to delete Workouts table: {e}")

def delete_saved_lists_table():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS SavedLists")
            conn.commit()
            print("SavedLists table deleted successfully.")
    except Exception as e:
        print(f"Failed to delete SavedLists table: {e}")

def delete_saved_list_workouts_table():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS SavedListWorkouts")
            conn.commit()
            print("SavedListWorkouts table deleted successfully.")
    except Exception as e:
        print(f"Failed to delete SavedListWorkouts table: {e}")

def delete_workout_posts_table():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS workout_posts")
            conn.commit()
            print("workout_posts table deleted successfully.")
    except Exception as e:
        print(f"Failed to delete workout_posts table: {e}")

def delete_message_log_table():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS message_log")
            conn.commit()
            print("message_log table deleted successfully.")
    except Exception as e:
        print(f"Failed to delete message_log table: {e}")

if __name__ == "__main__":
    root()