import csv
import re
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
from psycopg2 import Error
from flask import g
from flask import request, session


app = Flask(__name__)
app.secret_key = "flight_planner"
DB_HOST = "xxxxxxxxxxxxx"
DB_NAME = "xxxxxxxxxxxxxxxxx"
DB_USER = "xxxxxxxxxxxxxxxxx"
DB_PASS = "xxxxxxxxxxxxxxxxx"

from airline_routes import airline_routes
from flight_routes import flight_routes
from user_routes import user_routes
from search_routes import search_routes

app.register_blueprint(airline_routes)
app.register_blueprint(flight_routes)
app.register_blueprint(user_routes)
app.register_blueprint(search_routes)


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(database=DB_NAME, user=DB_USER,
                                password=DB_PASS, host=DB_HOST)
    return g.db
@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

con = get_db()

@app.route("/")
def home():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT \"Name\" FROM airline WHERE \"Name\" NOT IN ('Private flight', 'Unknown') LIMIT 10"
    cur.execute(s)
    list_airline_names = [row["Name"] for row in cur.fetchall()]
    return render_template("index.html", list_airline_names=list_airline_names)

@app.before_request
def before_request():
    
    if 'loggedin' not in session and request.endpoint not in ['login', 'register']:
        flash('Please login or register first!', 'warning')
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
