import os
import requests
from flask import Flask, render_template, request, Blueprint, jsonify

nutrition_bp = Blueprint('nutrition', __name__)

# Get API credentials from environment variables
EDAMAM_API_ID = os.environ.get('EDAMAM_API_ID')
EDAMAM_API_KEY = os.environ.get('EDAMAM_API_KEY')

@nutrition_bp.route('/')
def nutrition_home():
    return render_template("meal_planner.html")

@nutrition_bp.route('/recipes', methods=['GET'])
def get_filtered_recipes():
    # Get parameters from request
    allergies = request.args.getlist('allergies')
    query = request.args.get('query')  # Optional query parameter

    # Validate API credentials
    if not EDAMAM_API_ID or not EDAMAM_API_KEY:
        return jsonify({'error': 'API credentials are missing'}), 500

    # Construct URL for Edamam API
    url = 'https://api.edamam.com/search'
    params = {
        'q': query if query else 'recipes',  # Use 'recipes' if no query is provided
        'app_id': EDAMAM_API_ID,
        'app_key': EDAMAM_API_KEY,
        'to': 10  # Number of recipes to fetch
    }

    # Add allergy parameters
    if allergies:
        params['health'] = '-'.join(allergies)

    try:
        # Make request to Edamam API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Extract relevant recipe information
        data = response.json()
        recipes = []
        for recipe in data['hits']:
            recipe_data = recipe['recipe']
            recipe_info = {
                'title': recipe_data['label'],
                'ingredients': [ingredient['text'] for ingredient in recipe_data['ingredients']],
                'instructions': recipe_data.get('url')  # Link to full recipe instructions
            }
            recipes.append(recipe_info)

        return jsonify(recipes)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

    