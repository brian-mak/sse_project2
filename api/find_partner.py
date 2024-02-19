from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sys, os
import database

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
            'user_id': database.get_user_id(session["user"]["userinfo"]["email"])[0][0],
            'workout_id': input.get("workout_type"),
            'location': input.get("location"),
            'start_time': input.get("start_time"),
            'end_time': input.get("end_time"),
            'message': input.get("message")
        }
        print(new_invitation['user_id'])
        database.post_invitation(new_invitation)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
    return index()
 

@app.route('/send_message/<int:invitation_id>', methods=['POST'])
def send_message(invitation_id):
    if request.method == 'POST':
        invitation = next((inv for inv in workout_invitations if inv['id'] == invitation_id), None)
        if invitation:
            message = request.form.get('message')
            # Here you can implement the logic to send the message to the inviter
            # For example, you might use a messaging service or email
            # In this example, we'll just print the message to the console
            print(f"Message sent to {invitation['name']}: {message}")
            return jsonify({'message': 'Message sent successfully'})
        else:
            return jsonify({'error': 'Invitation not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
