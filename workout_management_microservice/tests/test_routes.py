import pytest
import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from app import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

# def test_create_saved_list(client):
#     response = client.post('/api/users/1/saved_lists', json={'list_name': 'New List'})
#     assert response.status_code == 201
#     assert response.json['success'] is True

# def test_delete_saved_list(client):
#     response = client.delete('/api/saved_lists/1')
#     assert response.status_code == 200
#     assert response.json['success'] is True

def test_get_saved_lists(client):
    response = client.get('/api/users/1/saved_lists')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_workouts_for_saved_list(client):
    response = client.get('/api/saved_lists/1/workouts')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_fetch_workouts(client):
    response = client.get('/api/fetch_workouts', query_string={'target_muscle_groups': 'legs', 'available_equipment': 'dumbbell'})
    assert response.status_code == 200
    assert isinstance(response.json, list)

# def test_remove_workout_from_saved_list(client):
#     response = client.delete('/api/saved_lists/1/workouts/1')
#     assert response.status_code == 200
#     assert response.json['success'] is True

# def test_add_workout_to_saved_list(client):
#     response = client.post('/saved_lists/1/workouts', json={
#         'workout_id': '1',
#         'workout_name': 'Squats',
#         'equipment': 'Barbell',
#         'target_muscle_group': 'Legs',
#         'secondary_muscles': 'Glutes'
#     })
#     assert response.status_code == 201
#     assert response.json['success'] is True