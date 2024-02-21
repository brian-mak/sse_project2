from flask import Flask, request, jsonify
from database import insert_data, get_data
from bmi import bmi

app = Flask(__name__)

@app.route('/calculate_bmi', methods=['POST'])
def calculate_bmi():
    data = request.get_json()
    height = data['height']
    weight = data['weight']
    result = bmi(height=height, weight=weight)
    return jsonify({'bmi': result})

@app.route('/insert_data', methods=['POST'])
def insert_data_route():
    data = request.get_json()
    success = insert_data(data)
    if success:
        return jsonify({'success': True, 'message': 'Data inserted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to insert data'})

@app.route('/get_data')
def get_data_route():
    data = get_data()
    return jsonify({'data': data})

if __name__ == '__main__':
    app.run(debug=True)
