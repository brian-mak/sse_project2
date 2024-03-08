from flask import Flask, render_template, request, session, jsonify
import requests
import authentication
import json
import os

app = Flask(__name__)

RAPID_API_KEY = os.getenv('RAPID_API_KEY')

# Landing page with form
def index():
    user_info = session.get('user')
    if user_info:
        cuisines = [
            "American", "Asian", "British", "Caribbean", "Central Europe", "Chinese",
            "Eastern Europe", "French", "Indian", "Italian", "Japanese", "Kosher",
            "Mediterranean", "Mexican", "Middle Eastern", "Nordic", "South American",
            "South East Asian"
        ]

        meal_types = ["Breakfast", "Dinner", "Lunch", "Snack", "Teatime"]

        dish_types = [
            "Biscuits and cookies", "Bread", "Cereals", "Condiments and sauces",
            "Desserts", "Drinks", "Main course", "Pancake", "Preps", "Preserve",
            "Salad", "Sandwiches", "Side dish", "Soup", "Starter", "Sweets"
        ]
        return render_template('meal_planning.html', cuisines=cuisines, meal_types=meal_types, dish_types=dish_types)
    else:
        return authentication.login()

@app.route('/meal_planning', methods=['POST'])    
def meal_planning():
    url = "https://edamam-recipe-search.p.rapidapi.com/api/recipes/v2"

    cuisine_type = request.form.getlist('cuisine_type')  # List of selected cuisines
    meal_type = request.form.getlist('meal_type')  # List of selected meal types
    dish_type = request.form.getlist('dish_type')  # List of selected dish types
    min_calories = int(request.form['min_calories'])
    max_calories = int(request.form['max_calories'])

    headers = {
        "Accept-Language": "en",
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "edamam-recipe-search.p.rapidapi.com"
    }

    # Build the Edamam API URL with user preferences
    url = "https://edamam-recipe-search.p.rapidapi.com/api/recipes/v2"
    params = {
        "type":"public",
        "field[0]":"uri",
        "beta":"true",
        "random":"true",
        "calories":f"{min_calories}-{max_calories}",
        "imageSize": "REGULAR"  # Assuming normal image size by default
    }

    # Add cuisine filters if selected
    if cuisine_type:
        for i in range(len(cuisine_type)):
            params["cuisineType"+"["+str(i)+"]"] = cuisine_type[i]

    # Add meal type filters if selected
    if meal_type:
        for i in range(len(meal_type)):
            params["mealType"+"["+str(i)+"]"] = meal_type[i]

    # Add dish type filters if selected
    if dish_type:
        for i in range(len(dish_type)):
            params["dishType"+"["+str(i)+"]"] = dish_type[i]

    # print(params)

    # Make the API request
    response = requests.get(url=url, headers=headers, params=params)

    # Check for successful response
    if response.status_code == 200:
        recipes = response.json()  # Extract recipes from the response
        filtered_recipes = []
        print(recipes['hits'][0])
        for i in range(len(recipes['hits'])):
            recipe_details = {
                "name": recipes['hits'][i]["recipe"]["label"] if not None else None,
                "cuisine_type": recipes['hits'][i]["recipe"]["cuisineType"][0] if not None else None,
                "meal_type": recipes['hits'][i]["recipe"]["mealType"][0] if not None else None,
                "dish_type": recipes['hits'][i]["recipe"]["dishType"][0] if not None else None,
                # "calories_per_serving": round((recipes['hits'][i]["recipe"]["calories"])/(recipes['hits'][i]["recipe"]["totalWeight"])),
                "nutritional_info_link": recipes['hits'][i]["recipe"]["shareAs"] if not None else None,
                "recipe_link": recipes['hits'][i]["recipe"]["url"] if not None else None,
                "image": recipes['hits'][i]["recipe"]["image"] if not None else None
            }
            filtered_recipes.append(recipe_details)
        print(filtered_recipes)
        return render_template('recipes.html', recipes=filtered_recipes)
    else:
        recipes = response.json()
        print(recipes)
        return f"Error: {response.status_code}"
    
def get_nutrition():
    # Get ingredients from the form
    query = request.form['query']
    
    # Call API-Ninjas API to get nutrition analysis for the ingredients
    api_key = 'tUA8QAux/Y75I+hn4zqkcQ==HSuDuV9i3xFTCbC7'  # Replace with your actual API key
    api_url = f'https://api.api-ninjas.com/v1/nutrition?query={query}'
    
    try:
        response = requests.get(api_url, headers={'X-Api-Key': api_key})
        if response.status_code == requests.codes.ok:
            nutrients_list = response.json()
            return render_template('nutrition.html', nutrients_list=nutrients_list)
        else:
            error_message = f"Error: {response.status_code}, {response.text}"
            return render_template('error.html', error=error_message)
    except requests.RequestException as e:
        error_message = f"Error fetching data from API-Ninjas: {str(e)}. Please try again."
        return render_template('error.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
