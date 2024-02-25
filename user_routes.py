import csv
import re
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
from psycopg2 import Error
from flask import g, Blueprint
from app import get_db
from utilities import validate_form
from flask import request, session

con = get_db()
user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute('SELECT * FROM "user" WHERE email = %s', (email,))
        user = cur.fetchone()
        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['phonenumber'] = user['phone number']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return render_template('index.html', message=message)
        else:
            message = 'Please enter correct email / password!'
    return render_template('login.html', message=message)

@user_routes.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@user_routes.route('/profile')
def profile():
    
    # Check if the user is logged in
    if 'loggedin' in session and session['loggedin']:
        
        name = session['name']
        email = session['email']



        
        flight_id = request.args.get('flight_id')
        flight_price = request.args.get('flight_price')

        if flight_id and flight_price:
            
            with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                booked_query = """

    WITH RECURSIVE FlightPaths AS (
      -- Base case: direct flights
      SELECT
        r."Airline",
        r."Airline ID",
        r."Price",
        a1."Name" AS "Source Airport",
        a1."Country" AS "Source Country",
        a2."Name" AS "Destination Airport",
        a2."Country" AS "Destination Country",
        a1."Name" || '->' || a2."Name" AS "Path",
        0 AS "hops",
        ABS(EXTRACT(EPOCH FROM r."Arrival Time" - r."Departure Time")) AS "Flight Duration"
      FROM
        Routes r
        JOIN Airports a1 ON r."Source Airport ID" = a1."Airport ID"
        JOIN Airports a2 ON r."Destination Airport ID" = a2."Airport ID"
      WHERE
        a1."Country" = %s
        AND a2."Country" = %s

      UNION ALL

      -- Recursive case: indirect flights with one stop
      SELECT
        r1."Airline",
        r1."Airline ID",
        r1."Price" + r2."Price" AS "Price",
        a1."Name" AS "Source Airport",
        a1."Country" AS "Source Country",
        a3."Name" AS "Destination Airport",
        a3."Country" AS "Destination Country",
        a1."Name" || '->' || a2."Name" || '->' || a3."Name" AS "Path",
        1 AS "hops",
        ABS(EXTRACT(EPOCH FROM r1."Arrival Time" - r1."Departure Time")) + 
        ABS(EXTRACT(EPOCH FROM r2."Arrival Time" - r2."Departure Time")) AS "Flight Duration"
      FROM
        Routes r1
        JOIN Airports a1 ON r1."Source Airport ID" = a1."Airport ID"
        JOIN Routes r2 ON r1."Destination Airport ID" = r2."Source Airport ID"
        JOIN Airports a2 ON r2."Source Airport ID" = a2."Airport ID"
        JOIN Airports a3 ON r2."Destination Airport ID" = a3."Airport ID"
      WHERE
        a1."Country" = %s
        AND a3."Country" = %s
        AND a2."Country" <> %s
        AND a2."Country" <> %s
    )
    SELECT
      "Airline",
      "Airline ID",
      "Source Airport",
      "Source Country",
      "Destination Airport",
      "Destination Country",
      "Path",
      "hops",
      "Flight Duration",
      "Price"
    FROM
      FlightPaths
    WHERE "Airline ID" = %s
    AND "Price" = %s
    ORDER BY
      "hops";
"""

                cur.execute(booked_query, (session['source'], session['destination'], session['source'], session['destination'], session['source'], session['destination'], flight_id, flight_price))

                booked_flight = cur.fetchone()

            with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                insert_query = """
    INSERT INTO BookedFlight ("email", "airline", "airlineid", "sourceairport", "sourcecountry", 
                               "destinationairport", "destinationcountry", "path", "hops", 
                               "flightduration", "price")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """
                cur.execute(insert_query, (email, booked_flight["Airline"], booked_flight["Airline ID"], booked_flight["Source Airport"],
                                booked_flight["Source Country"], booked_flight["Destination Airport"],
                                booked_flight["Destination Country"], booked_flight["Path"], booked_flight["hops"],
                                booked_flight["Flight Duration"], booked_flight["Price"]))

            
                con.commit()

                    
                inserted_record = cur.fetchone()

            
            return render_template('profile.html', name=name, email=email, booked_flight=booked_flight)
        else:
            
            return render_template('profile.html', name=name, email=email)
        


    else:
        
        return redirect('/login')
    
@user_routes.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        message = validate_form(request)
        if message is None:
            userName = request.form['name']
            password = generate_password_hash(request.form['password'])
            email = request.form['email']
            phoneNumber = request.form['phoneNumber']
            cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute('INSERT INTO "user" (username, email, password, phonenumber) VALUES (%s, %s, %s, %s) ON CONFLICT (email) DO NOTHING',
                           (userName, email, password, phoneNumber))
            if cursor.rowcount == 0:
                message = 'Account already exists!'
            else:
                con.commit()
                message = 'You have successfully registered!'
    return render_template('register.html', message=message)
