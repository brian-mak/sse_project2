import datetime
from flask import jsonify, request
import pytest
from app import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_post(client):
    test_data = {
        'user_id': 'auth0|65cb6a87affd51e1baed38bc',
        'title': 'test',
        'message': 'test'
    }
    response = client.get('/post', query_string=test_data)
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


def test_reply(client):
    test_data = {
        'user_id': 'auth0|65cb6a87affd51e1baed38bc',
        'post_id': 1,
        'message': 'test'
    }
    response = client.get('/reply', query_string=test_data)
    assert response.status_code == 200
    response_data = response.get_json()
    assert 'success' in response_data
    print(response_data)
    assert response_data['success'] is True