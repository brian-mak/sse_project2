import pytest
from flask import session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app # Importing your Flask app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login_route(client):
    response = client.get('/login')
    assert response.status_code == 302  # Redirects to Auth0

def test_callback_route(client):
    with client.session_transaction() as sess:
        sess['user'] = {'userinfo': {'email': 'test@example.com', 'name': 'Test User', 'nickname': 'tester', 'sub': '123456'}}

    response = client.get('/callback')
    assert 'user' in session  # User session should be updated

def test_logout_route(client):
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'].startswith('https://')  # Should redirect to Auth0 logout

# You can add more tests for edge cases, error handling, etc.
