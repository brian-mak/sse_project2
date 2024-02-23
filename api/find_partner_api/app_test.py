import datetime
from flask import jsonify, request
import pytest
from app import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_post_invitation(client):
    start_time = datetime.datetime.now().isoformat()
    end_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
    test_data = {
        'user_id': 'auth0|65cb6a87affd51e1baed38bc',
        'workout_name': 'test',
        'location': 'test',
        'start_time': start_time,
        'end_time': end_time,
        'message': 'test'
    }
    response = client.get('/post_invitation', query_string=test_data)
    assert response.status_code == 200
    response_data = response.get_json()
    assert 'success' in response_data
    print(response_data)
    assert response_data['success'] is True


def test_get_all_posts(client):
    # Assuming user is not provided
    user = None
    
    # Call the function
    response = client.get('/')
    result = response.get_json()

    # Assertions
    assert result['success'] == True
    assert 'data' in result
