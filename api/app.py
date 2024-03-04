from flask import Flask, render_template, request, session, jsonify
import requests
from dotenv import find_dotenv, load_dotenv
from os import environ as env
import os
import openai
import re
from googleapiclient.discovery import build

import find_partner, authentication
from database import db_bp

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

app.register_blueprint(db_bp, url_prefix='/db')

def get_rapid_api_key():
    return os.environ.get('RAPID_API_KEY')

def get_openai_api_key():
    return os.environ.get('OPENAI_KEY')


def fetch_exercises(target_muscle_groups, available_equipment):
    api_key = get_rapid_api_key()
    url = "https://exercisedb.p.rapidapi.com/exercises"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }
    
    muscle_groups_mapping = {
        'full_body': ["pectorals", "serratus anterior", "upper back", "lats", 
                      "traps", "spine", "delts", "biceps", "triceps", "forearms", 
                      "quads", "hamstrings", "calves", "glutes", "adductors", 
                      "abductors", "abs", "cardiovascular system"],
        'upper_body': ["pectorals", "serratus anterior", "upper back", "lats", 
                      "traps", "spine", "delts", "biceps", "triceps", "forearms"],
        'chest': ["pectorals", "serratus anterior"],
        'back': ["upper back", "lats", "traps", "spine"],
        'shoulders': ["delts"],
        'biceps': ["biceps"],
        'triceps': ["triceps"],
        'forearms': ["forearms"],        
        'lower_body': ["quads", "hamstrings", "calves", "glutes", "adductors", "abductors"],
        'quads': ["quads"],
        'hamstrings': ["hamstrings"],
        'calves': ["calves"],
        'glutes': ["glutes"],
        'hips': ["adductors", "abductors"],
        'abs': ["abs"],
        'cardio': ["cardiovascular system"],
    }
    
    equipment_mapping = {
        'body_weight': "body weight",
        'band': "band", 
        'barbell': "barbell", 
        'bosu_ball': "bosu ball", 
        'cable': "cable", 
        'dumbbell': "dumbbell", 
        'elliptical_machine': "elliptical machine", 
        'ez_barbell': "ez barbell", 
        'hammer': "hammer", 
        'kettlebell': "kettlebell", 
        'leverage_machine': "leverage machine",
        'medicine_ball': "medicine ball", 
        'olympic_barbell': "olympic barbell", 
        'resistance_band': "resistance band",
        'roller': "roller", 
        'rope': "rope", 
        'skierg_machine': "skierg machine", 
        'sled_machine': "sled machine", 
        'smith_machine': "smith machine", 
        'stability_ball': "stability ball", 
        'stationary_bike': "stationary bike", 
        'stepmill_machine': "stepmill machine",
        'wheel_roller': "wheel roller"
    }
    
    target_muscles = []
    for group in target_muscle_groups:
        if group in muscle_groups_mapping:
            target_muscles.extend(muscle_groups_mapping[group])
    
    target_muscles = list(set(target_muscles))
    available_equipments = [equipment_mapping[equipment] for equipment in available_equipment if equipment in equipment_mapping]
    
    response = requests.get(url, headers=headers, params={"limit": 1400})

    if response.status_code == 200:
        all_exercises = response.json()

        filtered_exercises = [
            exercise for exercise in all_exercises
            if exercise['target'].lower() in target_muscles
            and exercise['equipment'].lower() in available_equipments
        ]

        details_of_exercises = [{
            'name': exercise.get('name'),
            'id' : exercise.get('id'),
            'equipment': exercise.get('equipment'),
            'targetMuscleGroup': exercise.get('target'),
            'secondaryMuscles': exercise.get('secondaryMuscles', 'Not specified'),
            'instructions': exercise.get('instructions', 'Please refer to external sources for instructions'),
            'gifUrl': exercise.get('gifUrl', 'No GIF available')
        } for exercise in filtered_exercises]

        return details_of_exercises
    else:
        print(f"Failed to fetch exercises: {response.status_code}")
        return []


# @app.route()
# def fetch_exercises_details(exercise_name):
#     api_key = get_rapid_api_key()
#     url = "https://exercisedb.p.rapidapi.com/exercises"

#     headers = {
#         "X-RapidAPI-Key": api_key,
#         "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
#     }
    
#     params = {"name": exercise_name}
#     response = requests.get(url, headers=headers, params=params)

#     user_id = request.args.get('user_id')

#     if response.status_code == 200:
#         all_exercises = response.json()

#         details_of_exercises = [{
#             'name': exercise.get('name'),
#             'equipment': exercise.get('equipment'),
#             'targetMuscleGroup': exercise.get('target'),
#             'secondaryMuscles': exercise.get('secondaryMuscles', 'Not specified'),
#             'instructions': exercise.get('instructions', 'Please refer to external sources for instructions'),
#             'gifUrl': exercise.get('gifUrl', 'No GIF available')
#         } for exercise in all_exercises]

#         return details_of_exercises
#     else:
#         print(f"Failed to fetch exercises: {response.status_code}")
#         return []
    

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search_exercises')
def search_exercises():
    return render_template("search_exercises.html")

@app.route('/saved_lists')
def saved_lists():
    user_info = session.get('user')
    user_id = user_info.get('userinfo', {}).get('sub') if user_info else None
    return render_template("saved_lists.html", user_id=user_id)

@app.route('/exercises', methods=['POST'])
def search_exercises_result():
    # Retrieving user information from the session
    user_info = session.get('user')
    user_id = user_info.get('userinfo', {}).get('sub') if user_info else None

    data = request.form.to_dict(flat=True)
    data['muscleGroups'] = request.form.getlist('muscleGroups')
    data['equipment'] = request.form.getlist('equipment')

    target_muscle_groups = [muscle.lower() for muscle in data['muscleGroups']]
    available_equipment = [equipment.lower() for equipment in data['equipment']]

    exercises = fetch_exercises(target_muscle_groups, available_equipment)
    return render_template("exercises.html", exercises=exercises, user_id=user_id)


# @app.route('/search_youtube', methods=['GET'])
# def search_youtube():
#     search_query = request.args.get('query')
#     youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

#     youtube = build('youtube', 'v3', developerKey=youtube_api_key)

#     youtube_search_request = youtube.search().list(
#         part='snippet',
#         q=search_query,
#         type='video',
#         maxResults=1
#     )
#     response = youtube_search_request.execute()

#     if response['items']:
#         # Assuming we only want the first result
#         video_id = response['items'][0]['id']['videoId']
#         return jsonify({'videoId': video_id})
#     else:
#         return jsonify({'error': 'No videos found'}), 404
    

@app.route('/search_youtube', methods=['GET'])
def search_youtube():
    search_query = request.args.get('query')
    max_videos = int(request.args.get('max', 10))  # Get the max number of videos to return, default is 5
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    search_request = youtube.search().list(
        part='snippet',
        q=search_query,
        type='video',
        maxResults=max_videos
    )
    response = search_request.execute()

    videos = []
    if response['items']:
        for item in response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            description = item['snippet']['description']
            thumbnail_url = item['snippet']['thumbnails']['high']['url']
            videos.append({
                'videoId': video_id,
                'title': title,
                'description': description,
                'thumbnailUrl': thumbnail_url
            })
        print(videos)
        return jsonify(videos)
    else:
        return jsonify({'error': 'No videos found'}), 404


def generate_workout_plan():
    api_key = get_openai_api_key()

    # Example of fetching user preferences and saved exercises
    # preferences = get_user_preferences(user_id)
    # saved_exercises = get_saved_exercises(user_id)
    
    # # Constructing the prompt
    # prompt = f"Create a workout plan for the following preferences: Fitness Goal: {preferences['fitness_goal']}, Target Muscle Group: {preferences['target_muscle_group']}, Fitness Level: {preferences['fitness_level']}, Preferred Workout Duration: {preferences['preferred_workout_duration']} minutes. Include {preferences['no_of_exercises']} of these exercises: {', '.join([exercise['name'] for exercise in saved_exercises])}."

    # prompt = f"Create a workout plan for the following preferences: Fitness Goal: Weight Gain, Target Muscle Group: Upper Body, Fitness Level: Beginner, Preferred Workout Duration: 60 minutes. Include {preferences['no_of_exercises']} of these exercises: 45° Side Bend, Air Bike, Barbell Bench Front Squat, Barbell Bent Over Row, Barbell Deadlift, Barbell Decline Bent Arm Pullover, Barbell Decline Wide-grip Pullover, Barbell Front Raise, Barbell Seated Behind Head Military Press, Dumbbell Around Pullover, Dumbbell Bench Press, Deep Push Up, Barbell Floor Calf Raise."

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
        "content": "\"Create a workout plan for the following preferences: Fitness Goal: Weight Gain, Target Muscle Group: Upper Body, Fitness Level: Beginner, Preferred Workout Duration: 60 minutes. Include only 5 exercises from this list: 45° Side Bend, Air Bike, Barbell Bench Front Squat, Barbell Bent Over Row, Barbell Deadlift, Barbell Decline Bent Arm Pullover, Barbell Decline Wide-grip Pullover, Barbell Front Raise, Barbell Seated Behind Head Military Press, Dumbbell Around Pullover, Dumbbell Bench Press, Deep Push Up, Barbell Floor Calf Raise.\""
        }
    ],
    temperature=0.2,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    # response = openai.Completion.create(
    #     engine="gpt-3.5-turbo-instruct",
    #     prompt=prompt,
    #     temperature=0.7,
    #     max_tokens=500,
    #     top_p=1.0,
    #     frequency_penalty=0.0,
    #     presence_penalty=0.0
    # )

    print(response)

    # if response.choices:
    #     response_text = response.choices[0]['message']['content'].strip()
    #     workout_plan = parse_workout_plan(response_text)
    #     print(jsonify(workout_plan))
    #     return jsonify(workout_plan)
    #     # workout_plan = response.choices[0]['message']['content'].strip()
    # else:
    #     workout_plan = "No workout plan generated."

    # return workout_plan

    # if response.choices:
    #     response_text = response.choices[0]['message']['content'].strip()
    #     # Extract title, exercises, and remarks from response_text
    #     title, exercises, remarks = parse_workout_plan(response_text)
    #     return {
    #         'title': title,
    #         'exercises': exercises,
    #         'remarks': remarks
    #     }
    # else:
    #     return "No workout plan generated."
    
    if response.choices:
        response_text = response.choices[0]['message']['content'].strip()
        workouts = parse_workout_plan(response_text)
        # Depending on your application's needs, you can now return, print, or otherwise use the exercises list
        print(workouts)  # For debugging
        return workouts
    else:
        return "No workout plan generated."


def parse_workout_plan(text):
    # # Split the response by newlines to separate each exercise
    # lines = text.strip().split('\n')
    
    # # Regular expression pattern to identify the exercise and its details
    # pattern = re.compile(r"(\d+)\.\s+([\w\s]+)\s+-\s+(\d+)\s+sets\sof\s(\d+)\s+reps")

    # # Parse each line with the pattern and convert to a structured format
    # structured_response = []
    # for line in lines:
    #     match = pattern.match(line)
    #     if match:
    #         structured_response.append({
    #             'number': match.group(1),
    #             'exercise': match.group(2),
    #             'sets': match.group(3),
    #             'reps': match.group(4)
    #         })

    # return structured_response

    # # Split the response to separate title, exercises, and remarks
    # parts = text.split('\n\n')
    # title = parts[0]
    # exercises_text = parts[1]
    # remarks = parts[-1]

    # # Regular expression pattern to identify the exercise and its details
    # pattern = re.compile(r"(\d+)\.\s+([\w\s]+):\s+(\d+)\s+sets\sx\s(\d+)\s+reps")

    # # Parse each exercise with the pattern and convert to a structured format
    # exercises = []
    # for line in exercises_text.split('\n'):
    #     match = pattern.match(line)
    #     if match:
    #         exercises.append({
    #             'number': match.group(1),
    #             'exercise': match.group(2),
    #             'sets': match.group(3),
    #             'reps': match.group(4)
    #         })

    # return title, exercises, remarks

    # Define a list to hold each exercise's details
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

@app.route('/my_custom_workout_plan')
def my_custom_workout_plan():
    # user_id = session['user_id']

    workouts = generate_workout_plan()
    # Ensure workout_plan is a dictionary before passing to render_template
    if isinstance(workouts, str):
        return workouts  # Handle error or "No workout plan generated" case
    return render_template('custom_workout_plan.html', workouts=workouts)


app.add_url_rule('/find_partner', 'find_partner', find_partner.index)
app.add_url_rule('/login', 'login', authentication.login)
app.add_url_rule('/callback', 'callback', authentication.callback)
app.add_url_rule('/logout', 'logout', authentication.logout)
app.add_url_rule('/post_invitation', 'post_invitation', find_partner.post_invitation, methods=['POST'])
app.add_url_rule('/delete_post', 'delete_post', find_partner.delete_post, methods=['POST'])


if __name__ == "__main__":
    app.run(debug=True)