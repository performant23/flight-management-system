import csv
import re
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
from psycopg2 import Error
from flask import Blueprint
from app import get_db
from flask import request, session

airline_routes = Blueprint('airline_routes', __name__)

@airline_routes.route("/airlinedirectories", methods=['GET', 'POST'])
def airlinedir():
    con = get_db()
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        search_term = request.form.get('search_term')

        
        query_filtered = "SELECT * FROM AIRLINE WHERE \"Name\" ILIKE %s OR \"Country\" ILIKE %s"
        cur.execute(query_filtered, (f'%{search_term}%', f'%{search_term}%'))

        result_filtered = cur.fetchall()

        return render_template("airlines.html", list_airlines=result_filtered)

    
    query_all = "SELECT * FROM AIRLINE"
    cur.execute(query_all)
    result_all = cur.fetchall()

    return render_template("airlines.html", list_airlines=result_all)
