from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Landing page with form
@app.route('/', methods=['GET'])
def index():
    return render_template('recipe_search.html')

# Results page
@app.route('/recipes', methods=['POST'])
def get_recipes():
    if request.method == 'POST':
        # Get inputs from the form
        query = request.form['query']

        # Call Edamam Recipe Search API
        app_id = 'your_app_id'
        app_key = 'your_app_key'
        url = f"https://api.edamam.com/search?q={query}&app_id={app_id}&app_key={app_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for any HTTP error
            data = response.json()

            # Extract recipe data
            recipes = data['hits']

            return render_template('recipes.html', query=query, recipes=recipes)

        except requests.RequestException as e:
            error_message = f"Error fetching data from Edamam API: {str(e)}"
            print(error_message)
            return render_template('error.html', message=error_message)

        except KeyError as e:
            error_message = f"Error parsing response from Edamam API: {str(e)}"
            print(error_message)
            return render_template('error.html', message=error_message)
    else:
        return render_template('error.html', message="Invalid request method")

if __name__ == '__main__':
    app.run(debug=True)
