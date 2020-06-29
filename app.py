from flask import Flask, render_template,session,request,redirect,url_for
from flask_cors import CORS
import signal
from flask import Flask
from routes.list_projects import list_projects
from routes.list_runtime import list_runtime
import sys
import os
import requests
import constants
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.register_blueprint(list_projects, url_prefix="/list_projects")
app.register_blueprint(list_runtime, url_prefix="/list_runtime")

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        session.get('username')
        return 'Logout using <a href="/logout">Logout</a><br> Login to Metering dashboard using <a href="http://0.0.0.0:9000">dashboard</a>' 

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'developer' and request.form['username'] == 'developer':
        session['logged_in'] = True
        session['username']  = request.form['username']
        constants.username='developer'
        # constants.username=request.form['username']
    elif request.form['password'] == 'admin' and request.form['username'] == 'admin':  
        session['logged_in'] = True
        session['username']  = request.form['username']
        constants.username='admin'
    else:
        print('wrong password!')
    return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['username']  = None
    constants.username = None
    return home()


def signal_term_handler(signal, frame):
    app.logger.warn('got SIGTERM')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_term_handler)
    app.secret_key = os.urandom(12)
    app.run(host=str(os.environ.get("HOST","localhost")), port=int(os.environ.get("PORT", 8000)))
