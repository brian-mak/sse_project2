from flask import Flask, request, jsonify
import database
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    query_params = request.args
    try:
        posts = database.get_active_posts()
        return posts
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/post', methods=['GET'])
def post_invitation():
    query_params = request.args
    try:
        return database.post(query_params)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    

@app.route('/reply', methods=['GET'])
def reply():
    query_params = request.args
    try:
        return database.reply(query_params)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/get_post', methods=['GET'])
def get_post():
    query_params = request.args
    try:
        user_id = query_params.get('user_id')
        if user_id == None:
            return ('Invalid Input: User_ID empty')
        posts = database.get_active_posts(user_id)
        return posts
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/get_reply', methods=['GET'])
def get_reply():
    query_params = request.args
    try:
        post_id = query_params.get('post_id')
        if post_id == None:
            return ('Invalid Input: Post_ID empty')
        replies = database.get_reply(int(post_id))
        return replies
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


if __name__ == '__main__':
    app.run()
