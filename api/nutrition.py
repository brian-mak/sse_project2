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

    # Collect form data
    # data = request.form
    # allergies = data.getlist('allergies[]')
    # diets = data.getlist('diet[]')
    # calories_min = data.get('calories_min')
    # calories_max = data.get('calories_max')
    
    # Build the query parameters for the API call
    # Note: Adjust the parameter names and values according to Edamam's API documentation and your form structure
    # params = {
    #     'app_id': app_id,
    #     'app_key': app_key,
    #     'health': allergies,
    #     'diet': diets,
    #     'calories': f"{calories_min}-{calories_max}",
    #     # Add more parameters here as needed
    # }

    # headers = {
    #     'accept': 'application/json',
    #     'Authorization': 'Basic YmwzMzIzOlBoQHJtYWN5MTIz',
    #     'Content-Type': 'application/json',
    # }

    # data = {
    #     "size": 7,
    #     "plan": {
    #         "accept": {
    #             "all": [
    #                 {
    #                 "health": [
    #                     "SOY_FREE",
    #                     "FISH_FREE",
    #                     "MEDITERRANEAN"
    #                 ]
    #                 }
    #             ]
    #         },
    #         "fit": {
    #             "ENERC_KCAL": {
    #                 "min": 1000,
    #                 "max": 2000
    #             },
    #             "SUGAR.added": {
    #                 "max": 20
    #             }
    #         },
    #         "sections": {
    #             "Breakfast": {
    #                 "accept": {
    #                     "all": [
    #                         {
    #                             "dish": [
    #                                 "drinks",
    #                                 "egg",
    #                                 "biscuits and cookies",
    #                                 "bread",
    #                                 "pancake",
    #                                 "cereals"
    #                             ]
    #                         },
    #                         {
    #                             "meal": [
    #                                 "breakfast"
    #                             ]
    #                         }
    #                     ]
    #                     },
    #                     "fit": {
    #                     "ENERC_KCAL": {
    #                         "min": 100,
    #                         "max": 600
    #                     }
    #                 }
    #             },
    #             "Lunch": {
    #                 "accept": {
    #                     "all": [
    #                         {
    #                             "dish": [
    #                                 "main course",
    #                                 "pasta",
    #                                 "egg",
    #                                 "salad",
    #                                 "soup",
    #                                 "sandwiches",
    #                                 "pizza",
    #                                 "seafood"
    #                             ]
    #                         },
    #                         {
    #                             "meal": [
    #                                 "lunch/dinner"
    #                             ]
    #                         }
    #                     ]
    #                 },
    #                     "fit": {
    #                     "ENERC_KCAL": {
    #                         "min": 300,
    #                         "max": 900
    #                     }
    #                 }
    #             },
    #             "Dinner": {
    #                 "accept": {
    #                     "all": [
    #                         {
    #                             "dish": [
    #                                 "seafood",
    #                                 "egg",
    #                                 "salad",
    #                                 "pizza",
    #                                 "pasta",
    #                                 "main course"
    #                             ]
    #                         },
    #                         {
    #                         "meal": [
    #                             "lunch/dinner"
    #                         ]
    #                         }
    #                     ]
    #                 },
    #                 "fit": {
    #                     "ENERC_KCAL": {
    #                         "min": 200,
    #                         "max": 900
    #                     }
    #                 }
    #             }
    #         }
    #     }
    # }
    
    # # Edamam Meal Planner API endpoint
    # # Replace 'your_api_endpoint' with the actual endpoint URL provided by Edamam
    # api_endpoint = f"https://api.edamam.com/api/meal-planner/v1/{app_id}/select'"

    # # Make the API call
    # response = requests.post(url=api_endpoint, headers=headers, json=data)

    # # Handle the API response
    # if response.status_code == 200:
    #     # Process the successful response
    #     meal_plans = response.json()
    #     print(meal_plans)
    #     return render_template("test.html", meal_plan=app_key)
    # else:
    #     meal_plans = response.json()
    #     print(meal_plans)
    #     return jsonify({'error': 'Failed to fetch meal plans from Edamam'}), 500

@app.route('/meal_planning', methods=['POST'])    
def meal_planning():
    # Replace 'your_app_id' and 'your_app_key' with your actual Edamam API credentials
    # app_id = '0bb675bb'
    # app_key = '86cf77b7ba0c020712a6be9e0f5d3aef'
    url = "https://edamam-recipe-search.p.rapidapi.com/api/recipes/v2"

    # data = request.form
    # diets = data.getlist('diet[]')
    # calories_min = data.get('calories_min')
    # calories_max = data.get('calories_max')
    
    # Build the query parameters for the API call
    # Note: Adjust the parameter names and values according to Edamam's API documentation and your form structure
    # params = {
    #     'app_id': app_id,
    #     'app_key': app_key,
    #     'health': allergies,
    #     'diet': diets,
    #     'calories': f"{calories_min}-{calories_max}",
    #     # Add more parameters here as needed
    # }

    # Get user selected preferences from the form
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
    
        
    # querystring = {"type":"public",
    #                "field[0]":"uri",
    #                "beta":"true",
    #                "random":"true",
    #                "cuisineType[0]":"[  \"American\", \"Asian]",
    #                "imageSize[0]":"NORMAL",
    #                "mealType[0]":"Breakfast",
    #                "mealType[1]":"Lunch",
    #                "mealType[2]":"Dinner",
    #                "calories":"500-700","health[0]":
    #                "alcohol-cocktail",
    #                "diet[0]":"balanced",
    #                "dishType[0]":"Biscuits and cookies",
    #                "dishType[1]":"Seafood"}

    # headers = {
    #     "Accept-Language": "en",
    #     "X-RapidAPI-Key": "9ede2c0d5emsh11b19ac6345dfa4p1d949fjsnc2352cae16c3",
    #     "X-RapidAPI-Host": "edamam-recipe-search.p.rapidapi.com"
    # }

    # response = requests.get(url, headers=headers, params=querystring)

    # # Check for successful response
    # if response.status_code == 200:
    # # Process the JSON response
    #     data = response.json()
    #     print(data)
    #     return render_template("test.html", meal_plan=data)
    # else:
    #     data = response.json()
    #     print(data)
    #     return jsonify({'error': 'Failed to fetch meal plans from Edamam'}), 500

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
