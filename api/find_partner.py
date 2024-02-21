from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sys, os
import database
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    workout_invitations = database.get_all_user()
    return jsonify(workout_invitations)


@app.route('/post_invitation', methods=['POST'])
def post_invitation():
    input = request.form
    print(input)
    try:
        new_invitation = {
            'user_id': session["user"]["userinfo"]["sub"],
            'workout_id': 1, #input.get("workout_type"),
            'location': input.get("location"),
            'start_time': datetime.strptime(input.get("start_time"), '%Y-%m-%dT%H:%M'),
            'end_time': datetime.strptime(input.get("end_time"), '%Y-%m-%dT%H:%M'),
            'message': input.get("message")
        }
        database.post_invitation(new_invitation)
        return ('Workout Invitation Posted')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return (f"Post workout invitation failed. Error: {exc_type} {fname} {exc_tb.tb_lineno}")
    

@app.route('/send_message', methods=['POST'])
def send_message():
    query_params = request.args
    try:
        # new_message = {
        #     'user_id': session["user"]["userinfo"]["sub"],
        #     'post_id': post_id,
        #     'receiver_id': receiver_id,
        #     'message': ("message")
        # }
        database.post_new_message(query_params)
        return ('Message Sent')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return (f"Send message failed. Error: {exc_type} {fname} {exc_tb.tb_lineno}")


@app.route('/get_post', methods=['POST'])
def get_post():
    query_params = request.args
    try:
        user_id = query_params.get('user_id')
        if user_id == None:
            return ('Invalid Input: User_ID empty')
        posts = database.get_posts(user_id)
        return (jsonify(posts))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return (f"Send message failed. Error: {exc_type} {fname} {exc_tb.tb_lineno}")
    

if __name__ == '__main__':
    app.run()
