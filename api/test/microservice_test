import os
from os import environ as env
from flask import Flask
import requests

forum_api_url = os.getenv('FORUM_API')
workout_api_url = 'http://workout-management-microservice-dns.dpf4a3ayemg0b0fu.uksouth.azurecontainer.io:5000/api/saved_lists/1/workouts'


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")


def test_forum_api():
    response = requests.get(forum_api_url)
    assert response.status_code == 200

def test_workout_api_url():
    response = requests.get(workout_api_url)
    assert response.status_code == 200

test_forum_api()
test_workout_api_url()