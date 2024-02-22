from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import requests
import sys, os
from os import environ as env
import database
from datetime import datetime


api_url = os.getenv('FIND_PARTNER_API')


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")


def index():
    response = requests.get(api_url).json()
    have_posts = False
    if response["success"] == False:
        message = "We are still trying to locate people looking for workout partner. Please try again later."
    elif len(response['data']) == 0:
        message = "There is no people looking for workout partner currently."
    else:
        have_posts = True
    return render_template("workout_match.html", have_posts = have_posts, invitation = response['data'], message = message)


def post_invitation():
    input = request.form
    try:
        query_params = {
            'user_id': session["user"]["userinfo"]["sub"],
            'workout_name': input.get("workout_type"),
            'location': input.get("location"),
            'start_time': datetime.strptime(input.get("start_time"), '%Y-%m-%dT%H:%M'),
            'end_time': datetime.strptime(input.get("end_time"), '%Y-%m-%dT%H:%M'),
            'message': input.get("message")
        }
        response = requests.get(api_url, params=query_params)
        if response['success'] == False:
            return (f"Post workout invitation failed. Error: {response['message']}")    
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return (f"Post workout invitation failed. Error: {exc_type} {fname} {exc_tb.tb_lineno}")