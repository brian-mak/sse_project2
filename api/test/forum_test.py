import pytest
from flask import session
import sys
import os

# Add the parent directory to the Python module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app # Importing your Flask app

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


@pytest.fixture
def mock_api_response():
    return {
        'success': True,
        'data': [{'id': 1, 'title': 'Test Post', 'message': 'This is a test post'}]
    }


@pytest.mark.parametrize("login_session", [{'user': {'userinfo': {'sub': '123'}}}])
def test_index_success(mock_api_response, client, monkeypatch, login_session):
    def mock_get(*args, **kwargs):
        return mock_api_response

    monkeypatch.setattr(app.requests, 'get', mock_get)

    response = client.get('/')
    assert response.status_code == 200


def test_index_failure(client, monkeypatch):
    def mock_get(*args, **kwargs):
        return {'success': False}, 500

    monkeypatch.setattr(app.requests, 'get', mock_get)

    response = client.get('/')
    assert response.status_code == 200  # Even if there's an error, it should return 200


@pytest.mark.parametrize("login_session", [{'user': {'userinfo': {'sub': '123'}}}])
def test_post(mock_api_response, client, monkeypatch, login_session):
    def mock_get(*args, **kwargs):
        return MockResponse(mock_api_response, 200)

    monkeypatch.setattr(app.requests, 'get', mock_get)

    response = client.post('/post', data={'title': 'Test Title', 'message': 'Test Message'})
    assert response.status_code == 302  # Redirects after successful post


@pytest.fixture
def login_session(client, monkeypatch):
    with app.app.test_request_context('/'):
        with client.session_transaction() as sess:
            sess['user'] = {'userinfo': {'sub': '123'}}
        yield session


# More tests can be added similarly for other routes and functionalities
