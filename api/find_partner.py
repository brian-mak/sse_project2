from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sys, os
import database
from datetime import datetime


api_url = os.getenv('BOOK_API_URL', 'http://book-api-server-dns.cye8ahgvh7b6dkea.uksouth.azurecontainer.io:5000/books')


@app.route('/post_invitation', methods=['GET'])
def post_invitation():
    input = request.form
    try:
        query_params = {
            'user_id': session["user"]["userinfo"]["sub"],
            'workout_id': 1, #input.get("workout_type"),
            'location': input.get("location"),
            'start_time': datetime.strptime(input.get("start_time"), '%Y-%m-%dT%H:%M'),
            'end_time': datetime.strptime(input.get("end_time"), '%Y-%m-%dT%H:%M'),
            'message': input.get("message")
        }
        response = requests.get(api_url, params=query_params)
        if response['success'] == false:
            return (f"Post workout invitation failed. Error: {response['message']}")    
        return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return (f"Post workout invitation failed. Error: {exc_type} {fname} {exc_tb.tb_lineno}")