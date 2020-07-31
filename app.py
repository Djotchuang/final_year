from flask import Flask, abort, jsonify, request, render_template, url_for, send_from_directory, session, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.debug import get_current_traceback
from werkzeug.utils import secure_filename

import joblib
import socket
import json
import bcrypt
import re

# Import dependent files
from model import *
from scrape_data import *


model = joblib.load('./model.sav')

app = Flask(__name__)

# Database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'nafake'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/')
def home():

    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE account_id = %s',
                       (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('index.html', account=account)

    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the dashboard
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM news WHERE accounts_account_id = %s', (session['id'],))
        result = cursor.fetchall()
        return render_template('home.html', username=session['username'], result=result)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE account_id = %s',
                       (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Output message if something goes wrong...
    sign_up_msg = ''
    # Check if "username", "password", "confirmpassword" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'confirmpassword' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            sign_up_msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            sign_up_msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            sign_up_msg = 'Username must contain only characters and numbers!'
        elif not (password == confirmpassword):
            sign_up_msg = 'Your passwords do not match!'
        elif not username or not password or not confirmpassword or not email:
            sign_up_msg = 'All fields are mandatory!'
        else:
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(password.encode('utf-8'), salt)
            # Account doesn't exist and the form data is valid, now insert new account into accounts table
            cursor.execute(
                'INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, email, password))
            mysql.connection.commit()
            # sign_up_msg = 'Signed up successfully! Please login.'
            # return redirect(url_for('login'))

            cursor.execute(
                'SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
            # Fetch one record and return result
            account = cursor.fetchone()
            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['account_id']
                session['username'] = account['username']

                # Redirect to home page
                return redirect(url_for('dashboard'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        sign_up_msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('index.html', sign_up_msg=sign_up_msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    login_msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if  exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        # If account exists in accounts table in out database
        if account:
            authenticated_user = bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8'))
            if authenticated_user:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['account_id']
                session['username'] = account['username']

                # Redirect to home page
                return redirect(url_for('dashboard'))
        else:
            # Account doesnt exist or username/password incorrect
            login_msg = 'Incorrect username and/or password!'
    # Show the login form with message (if any)
    return render_template('index.html', login_msg=login_msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/<name>')
def pages(name):
    try:
        return render_template(name)
    except Exception:
        track = get_current_traceback(skip=1, show_hidden_frames=True,
                                      ignore_system_exceptions=False)
        track.log()
        abort(500)


@app.errorhandler(404)
def not_found(e):
    # Page not found
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):

    return render_template("404.html"), 500


# Get and predict from text

@app.route('/', methods=['GET','POST'])
def predict():

    result = request.form
    query_title = result['title']
    query_text = result['maintext']

    # Call to get text data - defined in model.py
    query = get_all_query(query_title, query_text)

    pred = model.predict(query)

    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO news VALUES (NULL, %s, %s, %s, NULL, %s)', (query_title, query_text, pred[0].title(), session['id']))
        mysql.connection.commit()

    return render_template('index.html', prediction=f'We are 73% sure that your news is {pred[0].title()}', show_predictions_modal=True)


# Get and predict from url

@ app.route('/predict_url', methods=['GET','POST'])
def predict_url():
    result = request.form
    url = result['url']

    # Call to scrape text function in scrape_data.py
    query, title, text = scrape_text(url)

    pred = model.predict(query)

    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO news VALUES (NULL, %s, %s, %s, %s, %s)', (title, text, pred[0].title(), url, session['id']))
        mysql.connection.commit()

    return render_template('index.html', prediction=f'We are 73% sure that your news is {pred[0].title()}', show_predictions_modal=True)


# For direct API calls through request

@ app.route('/predict_api', methods=['POST'])
def predict_api():

    data = request.get_json(force=True)

    query_title = data['title']
    query_text = data['maintext']

    query = get_all_query(query_title, query_text)

    pred = model.predict(query)
    output = pred[0].title()
    return jsonify(output)


# Run app

if __name__ == '__main__':
    # Get Available Socket on Computer
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = 5000  # sock.getsockname()[1] or
    sock.close()

    app.secret_key = os.urandom(24)
    app.run(port=port, debug=True)
