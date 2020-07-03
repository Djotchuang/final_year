from flask import Flask, abort, jsonify, request, render_template, url_for, send_from_directory, session
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.debug import get_current_traceback
from werkzeug.utils import secure_filename

import joblib
import socket
import json
import bcrypt

# Import dependent files
from model import *
from ocr import *
from scrape_data import *


model = joblib.load('./model.sav')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/img/saved_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'nafake'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('index.html')


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


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']

        if password == confirmpassword:
            password = password.encode('utf-8')
            password_hash = bcrypt.hashpw(password, bcrypt.gensalt())

            cur = mysql.connection.cursor()
            sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (
                username, email, password_hash,)

            cur.execute(sql)
            mysql.connection.commit()

            # session['username'] = username
            # session['email'] = email

            return redirect(url_for('home'))

        else:
            return redirect(url_for('home'), error="Passwords do not match")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return redirect(url_for('home'))


# Get and predict from text

@app.route('/', methods=['POST'])
def predict():

    result = request.form
    query_title = result['title']
    query_author = result['author']
    query_text = result['maintext']

    # Call to get text data - defined in model.py
    query = get_all_query(query_title, query_author, query_text)

    user_input = {'query': query}
    pred = model.predict(query)

    return render_template('index.html', prediction=f'Your news is {pred[0].title()}')


# Get and predict from image

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/predict_image', methods=['POST'])
def extract_text():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_file = app.config['UPLOAD_FOLDER'] + '/' + filename

    # Call to extract text from image - defined in ocr.py
    query = [get_text(image_file)]

    user_input = {'query': query}
    pred = model.predict(query)

    return render_template('index.html', prediction=f'We are result sure that your news is {pred[0]}')


# Get and predict from url

@ app.route('/predict_url', methods=['POST'])
def predict_url():
    result = request.form
    url = result['url']

    # Call to scrape text function in scrape_data.py
    query = scrape_text(url)

    user_input = {'query': query}
    pred = model.predict(query)

    # print('Accuracy of SGD classifier on data: {:.2f}%'.format(round(model.score(X_train, y_train)*100, 3)))
    return render_template('index.html', prediction=f'We are result sure that your news is {pred[0]}')


# For direct API calls through request

@ app.route('/predict_api', methods=['POST'])
def predict_api():

    data = request.get_json(force=True)

    query_title = data['title']
    query_author = data['author']
    query_text = data['maintext']

    query = get_all_query(query_title, query_author, query_text)
    user_input = {'query': query}

    pred = model.predict(query)
    output = pred[0]
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
