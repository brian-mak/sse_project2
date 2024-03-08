from flask import Flask, render_template, request, session
import requests
import authentication

app = Flask(__name__)

# Landing page with form
def index():
    user_info = session.get('user')
    if user_info:
        return render_template('meal_planner.html')
    else:
        return authentication.login()

def get_nutrition():
    if request.method == 'POST':
        # Get ingredients from the form
        query = request.form['query']
        print(query)
        # Split the input string based on new lines and commas
        ingredients = [ingredient.strip() for line in query.split('\n') for ingredient in line.split(',') if ingredient.strip()]
        
        # Call Edamam API to get nutrition analysis for each ingredient
        app_id = 'c1f66dde'
        app_key = '5e1435e7afc262817426d14e5ac58167'
        nutrients = []

        for ingredient in ingredients:
            url = f"https://api.edamam.com/api/nutrition-data?app_id={app_id}&app_key={app_key}&ingr={ingredient}"
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for any HTTP error
                data = response.json()

                # Extract nutrition data
                calories = data['calories']
                protein = data['totalNutrients']['PROCNT']['quantity']
                fat = data['totalNutrients']['FAT']['quantity']
                carbs = data['totalNutrients']['CHOCDF']['quantity']

                # Extract additional nutrient data
                nutrients = {
                    'Saturated Fat': data['totalNutrients']['FASAT']['quantity'],
                    'Trans Fat': data['totalNutrients']['FATRN']['quantity'],
                    'Cholesterol': data['totalNutrients']['CHOLE']['quantity'],
                    'Sodium': data['totalNutrients']['NA']['quantity'],
                    'Dietary Fiber': data['totalNutrients']['FIBTG']['quantity'],
                    'Total Sugars': data['totalNutrients']['SUGAR']['quantity'],
                    'Vitamin D': data['totalNutrients']['VITD']['quantity'],
                    'Calcium': data['totalNutrients']['CA']['quantity'],
                    'Iron': data['totalNutrients']['FE']['quantity'],
                    'Potassium': data['totalNutrients']['K']['quantity']
                }
                
                return render_template('nutrition.html', query=query, calories=calories, protein=protein, fat=fat, carbs=carbs, nutrients=nutrients)

            except requests.RequestException as e:
                error_message = f"Error fetching data from Edamam API: {str(e)}. Please try again."
                print(error_message)
                return render_template('error.html', error=error_message)

            except KeyError as e:
                error_message = f"Error parsing response from Edamam API: {str(e)}. Please try again."
                print(error_message)
                return render_template('error.html', error=error_message)
    else:
        return render_template('error.html', error="Invalid request method")

if __name__ == '__main__':
    app.run(debug=True) 
