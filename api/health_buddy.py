from flask import Flask, request, jsonify
from bmi import bmi 

app = Flask(__name__) 

@app.route('/calculate_bmi', methods =['POST'])
def calcluate_bmi(): 
    data = request.get.json()
    height = data['height']
    weight = data['weight'] 
    result = bmi(height=height,weight=weight) 
    return jsonify({'bmi': result})

if __name__== '__main__': 
    app.run(debug=True) 
