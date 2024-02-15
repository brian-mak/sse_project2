from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


def get_rapid_api_key():
    # Ideally, store and retrieve your API key securely
    return '9ede2c0d5emsh11b19ac6345dfa4p1d949fjsnc2352cae16c3'


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

@app.route('/')
def home():
    return render_template("userinput.html")

@app.route('/generate_plan', methods=['POST'])
def generate_plan():

    data = request.form.to_dict(flat=True)
    data['muscleGroups'] = request.form.getlist('muscleGroups')
    data['equipment'] = request.form.getlist('equipment')

    target_muscle_groups = [muscle.lower() for muscle in data['muscleGroups']]
    available_equipment = [equipment.lower() for equipment in data['equipment']]

    exercises = fetch_exercises(target_muscle_groups, available_equipment)
    return render_template("exercises.html", exercises=exercises)

if __name__ == "__main__":
    app.run(debug=True)