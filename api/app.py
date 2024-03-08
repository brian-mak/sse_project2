from flask import Flask, render_template, request, session, jsonify
import requests
from dotenv import find_dotenv, load_dotenv
from os import environ as env
import os
from googleapiclient.discovery import build

import forum
import authentication
import nutrition
from database import db_bp


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

app.register_blueprint(db_bp, url_prefix='/db')
# app.register_blueprint(nutrition_bp, url_prefix='/nutrition')

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
        'wheel_roller': "wheel roller"
    }
    
    target_muscles = []
    for group in target_muscle_groups:
        if group in muscle_groups_mapping:
            target_muscles.extend(muscle_groups_mapping[group])
    
    target_muscles = list(set(target_muscles))
    available_equipments = [equipment_mapping[equipment] for equipment in available_equipment if equipment in equipment_mapping]
    
    try:
        response = requests.get(url, headers=headers, params={"limit": 1400})
        response.raise_for_status()  # This will raise an exception for 4xx and 5xx errors
        
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

    except requests.RequestException as e:
        print(f"Network or HTTP request failed: {e}")
        return []
    except ValueError:
        print("Failed to decode JSON response")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search_exercises')
def search_exercises():
    user_info = session.get('user')
    if user_info:
        return render_template("search_exercises.html")
    else:
        return authentication.login()

@app.route('/saved_lists')
def saved_lists():
    user_info = session.get('user')
    if user_info:
        user_id = user_info.get('userinfo', {}).get('sub')
        return render_template("saved_lists.html", user_id=user_id)
    else:
        return authentication.login()

@app.route('/exercises', methods=['POST'])
def search_exercises_result():
    user_info = session.get('user')
    if not user_info:
        return authentication.login()
    try:
        user_id = user_info.get('userinfo', {}).get('sub')
        data = request.form.to_dict(flat=True)
        data['muscleGroups'] = request.form.getlist('muscleGroups')
        data['equipment'] = request.form.getlist('equipment')

        target_muscle_groups = [muscle.lower() for muscle in data['muscleGroups']]
        available_equipment = [equipment.lower() for equipment in data['equipment']]

        exercises = fetch_exercises(target_muscle_groups, available_equipment)
        if exercises:
            return render_template("exercises.html", exercises=exercises, user_id=user_id)
        else:
            error_message = "No workouts found for user input."
            return render_template("error.html", error=error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        return render_template("error.html", error=error_message)

@app.route('/search_youtube', methods=['GET'])
def search_youtube():
    search_query = request.args.get('query')
    max_videos = int(request.args.get('max', 10))
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

app.add_url_rule('/forum', 'forum', forum.index)
app.add_url_rule('/login', 'login', authentication.login)
app.add_url_rule('/callback', 'callback', authentication.callback)
app.add_url_rule('/logout', 'logout', authentication.logout)
app.add_url_rule('/post', 'post', forum.post, methods=['POST'])
app.add_url_rule('/update_posts', 'update_posts', forum.update_posts, methods=['POST'])
app.add_url_rule('/reply', 'reply', forum.reply, methods=['POST'])
app.add_url_rule('/get_replies', 'get_replies', forum.get_replies)
app.add_url_rule('/delete_post', 'delete_post', forum.delete_post, methods=['POST'])
app.add_url_rule('/meal_planner', 'meal_planner', nutrition.index)
# app.add_url_rule('/nutrition', 'nutrition', nutrition.get_nutrition, methods=['POST'])
app.add_url_rule('/meal_planning', 'meal_planning', nutrition.meal_planning, methods=['POST'])

if __name__ == "__main__":
    app.run(debug=True)