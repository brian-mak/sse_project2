from flask import Flask, render_template, request, session
import requests

app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET'])
def meal_planner():
    # Display the meal planner form
    return render_template('meal_planner.html')

@app.route('/facts', methods=['POST'])
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
