from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sys, os
import database
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    workout_invitations = database.get_all_invitations()
    return render_template('workout_match.html', invitations=workout_invitations)


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
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        flash(f"{exc_type} {fname} {exc_tb.tb_lineno}")

    return redirect(url_for("index"))
 

@app.route('/send_message/<int:invitation_id>', methods=['POST'])
def send_message(invitation_id):
    input = request.form
    print(input)
    try:
        new_message = {
            'user_id': session["user"]["userinfo"]["sub"],
            'post_id': 1, #input.get("workout_type"),
            'message': input.get("message")
        }
        database.post_new_message(new_message)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        flash(f"{exc_type} {fname} {exc_tb.tb_lineno}")

if __name__ == '__main__':
    app.run(debug=True)
