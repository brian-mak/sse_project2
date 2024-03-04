import re
from flask import Flask, jsonify, render_template, request, Blueprint, session
from os import environ as env
import os
import pyodbc
from dotenv import find_dotenv, load_dotenv
import sys
import requests
import openai
from retry import retry

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

connection_string = env.get("AZURE_SQL_CONNECTIONSTRING")

db_bp = Blueprint('db', __name__)

def get_rapid_api_key():
    return os.environ.get('RAPID_API_KEY')

def get_openai_api_key():
    return os.environ.get('OPENAI_KEY')

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
                    WorkoutID varchar(255) NOT NULL,
                    WorkoutName varchar(255) NOT NULL,
                    Equipment varchar(255) NOT NULL,
                    TargetMuscleGroup varchar(255) NOT NULL,
                    SecondaryMuscles varchar(255) NOT NULL,
                    PRIMARY KEY (ListID, WorkoutID),
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

@db_bp.route('/api/saved_lists_workouts/<int:list_id>', methods=['GET'])
def get_workout_list_details(list_id):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # Fetch workout IDs associated with the saved list
            cursor.execute("SELECT * FROM SavedListWorkouts WHERE ListID = ?", (list_id,))
            workout_details = [ {"workout_id": row[1],
                                 "workout_name": row[2],
                                 "equipment": row[3],
                                 "target_muscle_group": row[4],
                                 "secondary_muscles": row[5]} for row in cursor.fetchall() ]
            print(jsonify(workout_details))
            return jsonify(workout_details)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@db_bp.route('/api/saved_lists/<int:list_id>/exercises', methods=['GET'])
def get_exercises_for_list(list_id):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            # Fetch workout IDs associated with the saved list
            cursor.execute("SELECT WorkoutID FROM SavedListWorkouts WHERE ListID = ?", (list_id,))
            workout_ids = [row[0] for row in cursor.fetchall()]

        # Fetch exercise details from the ExerciseDB API
        exercises_details = []
        for id in workout_ids:
            details = fetch_exercise_details_from_exercisedb(id)
            if details:
                exercises_details.append(details)

        return jsonify(exercises_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function to fetch exercise details from the ExerciseDB API
def fetch_exercise_details_from_exercisedb(workout_id):
    api_key = get_rapid_api_key()
    url = "https://exercisedb.p.rapidapi.com/exercises/exercise/" + workout_id
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
    workout_id = request.json.get('workout_id')
    workout_name = request.json.get('workout_name')
    equipment = request.json.get('equipment')
    target_muscle_group = request.json.get('target_muscle_group')
    secondary_muscles = request.json.get('secondary_muscles')
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO SavedListWorkouts (ListID, WorkoutID, WorkoutName, Equipment, TargetMuscleGroup, SecondaryMuscles) VALUES (?, ?, ?, ?, ?, ?)", (list_id, workout_id, workout_name, equipment, target_muscle_group, secondary_muscles))
            conn.commit()
        return jsonify({"success": True, "message": "Workout added to saved list successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    

@db_bp.route('/saved_lists/remove_workout', methods=['POST'])
def remove_workout_from_saved_list():
    data = request.get_json()
    list_id = data.get('list_id')
    workout_id = data.get('workout_id')
    if not list_id or not workout_id:
        return jsonify({"success": False, "message": "Missing list_id or workout_id"}), 400

    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM SavedListWorkouts WHERE ListID = ? AND WorkoutID = ?", (list_id, workout_id))
            conn.commit()
        return jsonify({"success": True, "message": "Workout removed from saved list successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


def generate_workout_plan(fitness_goal, target_muscle_groups, fitness_level, num_of_workouts):
    try:
        api_key = get_openai_api_key()

        openai.api_key = api_key

        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "Answer in a consistent style."
            },
            {
            "role": "user",
            "content": f"\"Create a workout plan for the following preferences: Fitness Goal: {fitness_goal}, Target Muscle Group: {', '.join(target_muscle_groups)}, Fitness Level: {fitness_level}. Include only {num_of_workouts} exercises from this list: 45° Side Bend, Air Bike, Barbell Bench Front Squat, Barbell Bent Over Row, Barbell Deadlift, Barbell Decline Bent Arm Pullover, Barbell Decline Wide-grip Pullover, Barbell Front Raise, Barbell Seated Behind Head Military Press, Dumbbell Around Pullover, Dumbbell Bench Press, Deep Push Up, Barbell Floor Calf Raise.\""
            }
        ],
        temperature=0.2,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )

        print(response)
        
        response_text = response.choices[0]['message']['content'].strip()
        workouts = parse_workout_plan(response_text)
        # Depending on your application's needs, you can now return, print, or otherwise use the exercises list
        print(workouts)  # For debugging
        return workouts

    except openai.error.AuthenticationError as e:
        return jsonify({"error": "Authentication with OpenAI failed.", "details": str(e)}), 401
    except openai.error.InvalidRequestError as e:
        return jsonify({"error": "Invalid request to OpenAI.", "details": str(e)}), 400
    except openai.error.APIError as e:
        return jsonify({"error": "An error occurred with the OpenAI API.", "details": str(e)}), 500
    except Exception as e:
        # Catch-all for any other exceptions
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

def parse_workout_plan(text):
    workouts = []

    # Define a regular expression to match the exercise details
    # This pattern accounts for variations in the formatting of the exercise details
    pattern = re.compile(r"\d+\.\s*([\w\s]+)(?:-|:)\s*(\d+)\s*sets\s*x\s*(\d+)\s*reps")

    # Split the text into lines for easier processing
    lines = text.split('\n')

    # Iterate over each line, trying to match the pattern
    for line in lines:
        match = pattern.search(line)
        if match:
            # Extract exercise name, sets, and reps from the match
            exercise = match.group(1).strip()
            sets = match.group(2).strip()
            reps = match.group(3).strip()

            # Append a dictionary with the extracted details to the exercises list
            workouts.append({
                'exercise': exercise,
                'sets': sets,
                'reps': reps
            })

    return workouts


# @db_bp.route('/my_custom_workout_plan')
# def my_custom_workout_plan():
#     # user_id = session['user_id']

#     workouts = generate_workout_plan()
#     # Ensure workout_plan is a dictionary before passing to render_template
#     if isinstance(workouts, str):
#         return workouts  # Handle error or "No workout plan generated" case
#     return render_template('custom_workout_plan.html', workouts=workouts)


@db_bp.route('/workout_plan')
def workout_plan():
    user_info = session.get('user')
    user_id = user_info.get('userinfo', {}).get('sub') if user_info else None
    saved_lists = get_saved_lists_for_user(user_id)
    return render_template("workout_plan.html", saved_lists=saved_lists)


@db_bp.route('/my_custom_workout_plan', methods=['POST'])
def my_custom_workout_plan():
    # Retrieving user information from the session
    user_info = session.get('user')
    user_id = user_info.get('userinfo', {}).get('sub') if user_info else None

    data = request.form.to_dict(flat=True)
    data['fitnessGoal'] = request.form.get('fitnessGoal')
    data['muscleGroups'] = request.form.getlist('muscleGroups')
    data['equipment'] = request.form.getlist('equipment')
    data['fitnessLevel'] = request.form.get('fitnessLevel')
    data['numOfWorkouts'] = request.form.get('numOfWorkouts')

    print(data['fitnessGoal'])
    print(data['muscleGroups'])
    print(data['equipment'])
    print(data['fitnessLevel'])
    print(data['numOfWorkouts'])

    target_muscle_groups = [muscle.lower() for muscle in data['muscleGroups']]
    available_equipment = [equipment.lower() for equipment in data['equipment']]

    print(target_muscle_groups)
    print(available_equipment)

    workouts = generate_workout_plan(data["fitnessGoal"], target_muscle_groups, data["fitnessLevel"], data["numOfWorkouts"])
    # Ensure workout_plan is a dictionary before passing to render_template
    if isinstance(workouts, str):
        return workouts  # Handle error or "No workout plan generated" case
    return render_template('custom_workout_plan.html', workouts=workouts)


def get_saved_lists_for_user(user_id):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ListID, Name FROM SavedLists WHERE UserID = ?", (user_id,))
        lists = cursor.fetchall()
        return [{"list_id": row[0], "name": row[1]} for row in lists]


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
    # delete_saved_list_workouts_table()
    # delete_saved_lists_table()
    root()
    # create_schema()