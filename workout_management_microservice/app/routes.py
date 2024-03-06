from flask import Blueprint, request, jsonify
from .services import (
    create_saved_list_service,
    get_saved_lists_service,
    add_workout_to_saved_list_service,
    remove_workout_from_saved_list_service,
    get_workouts_for_saved_list_service,
    fetch_workouts_service
)

workout_blueprint = Blueprint('workout', __name__)

@workout_blueprint.route('/users/<user_id>/saved_lists', methods=['POST'])
def create_saved_list(user_id):
    data = request.get_json()
    list_name = data.get('list_name')
    
    result = create_saved_list_service(user_id, list_name)
    return jsonify(result), 201 if result['success'] else 500

@workout_blueprint.route('/users/<user_id>/saved_lists', methods=['GET'])
def get_saved_lists(user_id):
    saved_lists = get_saved_lists_service(user_id)
    return jsonify(saved_lists), 200

@workout_blueprint.route('/saved_lists/<list_id>/workouts', methods=['GET'])
def get_workouts_for_saved_list(list_id):
    workouts = get_workouts_for_saved_list_service(list_id)
    return jsonify(workouts), 200

@workout_blueprint.route('/saved_lists/<list_id>/workouts', methods=['POST'])
def add_workout_to_saved_list(list_id):
    data = request.get_json()
    result = add_workout_to_saved_list_service(
        list_id=list_id,
        workout_id=data.get('workout_id'),
        workout_name=data.get('workout_name'),
        equipment=data.get('equipment'),
        target_muscle_group=data.get('target_muscle_group'),
        secondary_muscles=data.get('secondary_muscles', '')
    )
    return jsonify(result), 201 if result['success'] else 500

@workout_blueprint.route('/saved_lists/<list_id>/workouts/<workout_id>', methods=['DELETE'])
def remove_workout_from_saved_list(list_id, workout_id):
    result = remove_workout_from_saved_list_service(list_id, workout_id)
    return jsonify(result), 200 if result['success'] else 404 if 'not found' in result['message'] else 500

@workout_blueprint.route('/fetch_workouts', methods=['GET'])
def fetch_workouts_route():
    """
    Route to fetch exercises filtered by target muscle groups and available equipment.
    """
    try:
        # Get parameters from the request
        target_muscle_groups = request.args.getlist('target_muscle_groups')
        available_equipment = request.args.getlist('available_equipment')
        
        # Call the service function to fetch workouts
        workouts = fetch_workouts_service(target_muscle_groups, available_equipment)
        
        # Convert workouts to JSON and return
        return jsonify(workouts)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500