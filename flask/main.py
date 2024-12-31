import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)

#@app.route('/')
#def hello():
    #return 'Hello, World!'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/create', methods=('GET', 'POST'))
def create():
    # if the user clicked on Submit, it sends post request
    if request.method == 'POST':
        # Get the title and save it in a variable
        title = request.form['title']
        # Get the content the user wrote and save it in a variable
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            # Open a connection to databse
            conn = get_db_connection()
            # Insert the new values in the db
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',(title, content))
            conn.commit()
            conn.close()
            # Redirect the user to index page
            return redirect(url_for('index'))

    return render_template('create.html')

