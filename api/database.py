from flask import Flask, jsonify, request
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


def create_schema():
    conn = None
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Create Workouts Table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Workouts]') AND type in (N'U'))
            BEGIN
                CREATE TABLE Workouts (
                    WorkoutID int NOT NULL PRIMARY KEY IDENTITY,
                    Name varchar(255) NOT NULL,
                    Description text,
                    Equipment varchar(255),
                    TargetMuscleGroup varchar(255),
                    SecondaryMuscles varchar(255),
                    Instructions text,
                    GifUrl varchar(255)
                );
            END
        """)

        # Create SavedLists Table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SavedLists]') AND type in (N'U'))
            BEGIN
                CREATE TABLE SavedLists (
                    ListID int NOT NULL PRIMARY KEY IDENTITY,
                    UserID int NOT NULL,
                    Name varchar(255) NOT NULL,
                    Description text,
                    CreationDate datetime NOT NULL DEFAULT GETDATE(),
                    FOREIGN KEY (UserID) REFERENCES Users(ID)
                );
            END
        """)

        # Create SavedListWorkouts Junction Table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[SavedListWorkouts]') AND type in (N'U'))
            BEGIN
                CREATE TABLE SavedListWorkouts (
                    ListID int NOT NULL,
                    WorkoutID int NOT NULL,
                    PRIMARY KEY (ListID, WorkoutID),
                    FOREIGN KEY (ListID) REFERENCES SavedLists(ListID),
                    FOREIGN KEY (WorkoutID) REFERENCES Workouts(WorkoutID)
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


@app.route('/workouts/add', methods=['POST'])
def add_workout():
    data = request.get_json()
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Workouts (Name, Description, Equipment, TargetMuscleGroup, SecondaryMuscles, Instructions, GifUrl)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (data['name'], data['description'], data['equipment'], data['targetMuscleGroup'], data['secondaryMuscles'], data['instructions'], data['gifUrl']))
            conn.commit()
        return jsonify({"success": True, "message": "Workout added successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# List all workouts
@app.route('/workouts', methods=['GET'])
def get_workouts():
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Workouts")
            workouts = cursor.fetchall()
        return jsonify([dict(zip([column[0] for column in cursor.description], row)) for row in workouts])
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Get details of a specific workout
@app.route('/workouts/<int:workout_id>', methods=['GET'])
def get_workout(workout_id):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Workouts WHERE WorkoutID = ?", (workout_id,))
            workout = cursor.fetchone()
        if workout:
            return jsonify(dict(zip([column[0] for column in cursor.description], workout)))
        else:
            return jsonify({"success": False, "message": "Workout not found."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/workouts/update/<int:workout_id>', methods=['POST'])
def update_workout(workout_id):
    data = request.get_json()
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Workouts
                SET Name = ?, Description = ?, Equipment = ?, TargetMuscleGroup = ?, SecondaryMuscles = ?, Instructions = ?, GifUrl = ?
                WHERE WorkoutID = ?
            """, (data['name'], data['description'], data['equipment'], data['targetMuscleGroup'], data['secondaryMuscles'], data['instructions'], data['gifUrl'], workout_id))
            conn.commit()
        return jsonify({"success": True, "message": "Workout updated successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/workouts/delete/<int:workout_id>', methods=['POST'])
def delete_workout(workout_id):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Workouts WHERE WorkoutID = ?", (workout_id,))
            conn.commit()
        return jsonify({"success": True, "message": "Workout deleted successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/saved_lists/create', methods=['POST'])
def create_saved_list():
    if request.json:
        user_id = request.json.get('user_id')
        list_name = request.json.get('list_name')
        description = request.json.get('description')
    else:
        user_id = request.form.get('user_id')
        list_name = request.form.get('list_name')
        description = request.form.get('description')

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
                INSERT INTO SavedLists (UserID, Name, Description) VALUES (?, ?, ?)
            """, (user_id, list_name, description))
            conn.commit()
        return jsonify({"success": True, "message": "Saved list created successfully."})
    except pyodbc.IntegrityError as e:
        return jsonify({"success": False, "message": "Database integrity error. Please check the data."}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/saved_lists/add_workout', methods=['POST'])
def add_workout_to_saved_list():
    list_id = request.form.get('list_id')
    workout_id = request.form.get('workout_id')
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO SavedListWorkouts (ListID, WorkoutID) VALUES (?, ?)", (list_id, workout_id))
            conn.commit()
        return jsonify({"success": True, "message": "Workout added to saved list successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


if __name__ == "__main__":
    get_all_user()