from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta

# decorator for routes that should be accessible only by logged in users
from auth_decorator import login_required

# # dotenv setup
# from dotenv import load_dotenv
# load_dotenv()


# App config
app = Flask(__name__)
# Session config
app.secret_key = "very secret key"
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='<client_id>',
    client_secret='<client_secret>',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


@app.route('/')
@login_required
def hello_world():
    email = dict(session)['profile']['email']
    return f'Hello, you are logge in as {email}!'


@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  
    token = google.authorize_access_token()  
    resp = google.get('userinfo')  
    user_info = resp.json()
    user = oauth.google.userinfo()  
    # use the user data to query from the database to check for the user
    # set your own data in while managing the sessions. 
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

if __name__ == "__main__":
    app.run(ssl_context="adhoc")
