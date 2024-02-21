from flask import Flask, request, jsonify
import database

app = Flask(__name__)

@app.route('/')
def index():
    query_params = request.args
    try:
        # return database.get_posts()
        return jsonify({"success": True, "message": "hello-world"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/post_invitation', methods=['GET'])
def post_invitation():
    query_params = request.args
    try:
        return database.post_invitation(query_params)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    

@app.route('/send_message', methods=['GET'])
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


@app.route('/get_post', methods=['GET'])
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
