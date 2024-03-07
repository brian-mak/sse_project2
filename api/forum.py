from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import requests
import sys, os
from os import environ as env
import database
from datetime import datetime


api_url = os.getenv('FORUM_API')


app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")


def index():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            response = response.json()
            have_posts = False
            if response["success"] == False:
                message = "Sorry, we have encountered an issue. Please try again later."
            elif len(response['data']) == 0:
                message = "There is no post now. Create one!"
            else:
                message = ""
                have_posts = True
        else: 
            message = "Sorry, we have encountered an issue. Please try again later."
        return render_template("forum.html", have_posts = have_posts, posts = response['data'], message = message, active_tab = "allPosts")
    except Exception:
        return render_template("forum.html", message = "Sorry, we have encountered an issue. Please try again later.")
    

def post():
    if session.get('user') == None:
        return redirect("/login")
    input = request.form
    # try:
    query_params = {
        'user_id': session["user"]["userinfo"]["sub"],
        'title': input.get("title"),
        'message': input.get("message"),
        }
    url = api_url + "post"
    response = requests.get(url, params=query_params)
    if response.status_code == 200:
        if response.json()['success'] == False:
            return (f"Create post failed. Error: {response.json()['message']}")    
        return redirect('/forum')
    else: 
        return (f"Create post failed. Error: {response.status_code}")
    # except Exception as e:
    #     return (f"Post workout invitation failed at parent. Error: {e}")


def delete_post():
    post_id = request.form.get('post_id')
    url = api_url + "delete_post"
    query_params = {
        'post_id': post_id,
    }
    response = requests.get(url, params=query_params)
    if response.status_code == 200:
        if response.json()['success'] == False:
            flash(f"Delete post failed. Error: {response.json()['message']}")
        else:
            flash("Post deleted")
    else: 
        flash(f"Delete post failed. Error: {response.status_code}")
    return redirect('/forum')
    

def update_posts():
    try:
        tab = request.json.get('tab')
        if tab == 'allPosts':
            response = requests.get(api_url)
            if response.status_code == 200:
                response = response.json()
                have_posts = False
                if response["success"] == False:
                    message = "Sorry, we have encountered an issue. Please try again later."
                elif len(response['data']) == 0:
                    message = "There is no post now. Create one!"
                else:
                    message = ""
                    have_posts = True
                    posts = response['data']
        elif tab == 'yourPosts':
            url = api_url + "get_post"
            response = requests.get(url, params = {'user_id': session["user"]["userinfo"]["sub"]})
            if response.status_code == 200:
                response = response.json()
                have_posts = False
                if response["success"] == False:
                    message = "Sorry, we have encountered an issue. Please try again later."
                elif len(response['data']) == 0:
                    message = "There is no post now. Create one!"
                else:
                    message = ""
                    have_posts = True
                    posts = response['data']
        # elif tab == 'savedPosts':
        #     posts = saved_posts
        else:
            posts = []
        return jsonify({'posts': posts,
                        'message': message,
                        'have_posts': have_posts})
    except Exception as e:
        print(e)
        return render_template("forum.html", message = "Sorry, we have encountered an issue. Please try again later.")


def reply():
    if session.get('user') == None:
        return redirect("/login")
    input = request.form
    # try:
    query_params = {
        'user_id': session["user"]["userinfo"]["sub"],
        'post_id': input.get("postId"),
        'message': input.get("message"),
        }
    url = api_url + "reply"
    response = requests.get(url, params=query_params)
    if response.status_code == 200:
        if response.json()['success'] == False:
            return (f"Reply post failed. Error: {response.json()['message']}")    
        return redirect('/forum')
    else: 
        return (f"Reply post failed. Error: {response.status_code}")
    

def get_replies():
    try:
        post_id = request.args.get('postId')
        response = requests.get(api_url+'get_reply', params={'post_id': post_id})
        print(post_id)
        if response.status_code == 200:
            response = response.json()
            have_reply = False
            reply = None
            if response["success"] == False:
                message = "Sorry, we have encountered an issue. Please try again later."
            elif len(response['data']) == 0:
                message = "There is no reply now. Be the first one!"
            else:
                message = False
                have_reply = True
                reply = response['data']
        return jsonify({'replies': reply,
                        'message': message,
                        'have_reply': have_reply})
    except Exception as e:
        print(e)
        return render_template("forum.html", message = "Sorry, we have encountered an issue. Please try again later.")


if __name__ == "__main__":
    app.run(debug=True)