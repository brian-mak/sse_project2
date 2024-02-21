from flask import Flask, render_template, request, jsonify
from bmi import bmi 

app = Flask(__name__, static_url_path='/static') 
@app.route('/')
def index(): 
    return render_template('health_buddy.html') 

@app.route('/calculate_bmi', methods=['POST'])  # Fixed typo here: methods instead of methods=
def calculate_bmi():  # Fixed typo here: calculate_bmi instead of calcluate_bmi
    data = request.get_json()  # Fixed typo here: get_json instead of get.json
    height = data['height']
    weight = data['weight'] 
    result = bmi(height=height, weight=weight) 
    return jsonify({'bmi': result})

if __name__== '__main__': 
    app.run(debug=True) 
