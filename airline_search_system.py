import csv
from flask import render_template, request
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import psycopg2.extras
from datetime import timedelta
import re

app = Flask(__name__)
app.secret_key = "flight_planner"
DB_HOST = "10.2.95.122"
DB_NAME = "laldinpuia_elvia"
DB_USER = "laldinpuia_elvia"
DB_PASS = "1e1c2ec5"

con = psycopg2.connect(database=DB_NAME, user=DB_USER,
                       password=DB_PASS, host=DB_HOST)
app.permanent_session_lifetime = timedelta(minutes=5)


@app.route("/")
def home():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT \"Name\" FROM airline WHERE \"Name\" NOT IN ('Private flight', 'Unknown') LIMIT 10"
    cur.execute(s)
    list_airline_names = [row["Name"] for row in cur.fetchall()]
    return render_template("index.html", list_airline_names=list_airline_names)

5
@app.route("/airlinedirectories", methods=['GET', 'POST'])
def airlinedir():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        search_term = request.form.get('search_term')

        # Construct the query for SELECT with filtering
        query_filtered = "SELECT * FROM AIRLINE WHERE \"Name\" ILIKE %s OR \"Country\" ILIKE %s"
        cur.execute(query_filtered, (f'%{search_term}%', f'%{search_term}%'))

        result_filtered = cur.fetchall()

        return render_template("airlines.html", list_airlines=result_filtered)

    # If it's a GET request or no form data, retrieve all airlines
    query_all = "SELECT * FROM AIRLINE"
    cur.execute(query_all)
    result_all = cur.fetchall()

    return render_template("airlines.html", list_airlines=result_all)


@app.route('/flightwonders')
def flightwon():
    return render_template("flightwonders.html")


@app.route('/longest_flights')
def longest_flights():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
            SELECT
                src_airport."Name" AS Source_Airport_Name,
                dest_airport."Name" AS Destination_Airport_Name,
                routes."Departure Time",
                routes."Arrival Time",
                (EXTRACT(EPOCH FROM routes."Arrival Time") - EXTRACT(EPOCH FROM routes."Departure Time")) AS Flight_Duration
            FROM
                Routes routes
            JOIN
                Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
            JOIN
                Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
            ORDER BY
                Flight_Duration DESC
            LIMIT 10;
            """
    cur.execute(query)
    longest_flights = cur.fetchall()

    return render_template("longestflights.html", longest_flights=longest_flights)


@app.route('/shortest_flights')
def shortest_flights():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
SELECT
    src_airport."Name" AS Source_Airport_Name,
    src_country."Name" AS Source_Country,
    dest_airport."Name" AS Destination_Airport_Name,
    dest_country."Name" AS Destination_Country,
    routes."Departure Time",
    routes."Arrival Time",
    (EXTRACT(EPOCH FROM routes."Arrival Time") - EXTRACT(EPOCH FROM routes."Departure Time")) AS Flight_Duration
FROM
    Routes routes
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
JOIN
    Country src_country ON src_airport."Country" = src_country."Name"
JOIN
    Country dest_country ON dest_airport."Country" = dest_country."Name"
WHERE
    routes."Departure Time" < routes."Arrival Time"
ORDER BY
    Flight_Duration ASC
LIMIT 10;
            """
    cur.execute(query)
    shortest_flights = cur.fetchall()

    return render_template("shortestflights.html", shortest_flights=shortest_flights)


@app.route('/busiest_routes')
def busiest_routes():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
SELECT
    src_airport."Name" AS Source_Airport_Name,
    dest_airport."Name" AS Destination_Airport_Name,
    COUNT(*) AS Number_of_Flights
FROM
    Routes routes
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
GROUP BY
    Source_Airport_Name, Destination_Airport_Name
ORDER BY
    Number_of_Flights DESC
LIMIT 10;
            """
    cur.execute(query)
    busiest_routes = cur.fetchall()

    return render_template("busiestroutes.html", busiest_routes=busiest_routes)


@app.route('/expensive_flights')
def expensive_flights():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
SELECT
    airline."Name" AS Airline_Name,
    src_airport."Name" AS Source_Airport_Name,
    src_country."Name" AS Source_Country,
    dest_airport."Name" AS Destination_Airport_Name,
    dest_country."Name" AS Destination_Country,
    routes."Price"
FROM
    Routes routes
JOIN
    Airline airline ON routes."Airline ID" = airline."Airline ID"
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
JOIN
    Country src_country ON src_airport."Country" = src_country."Name"
JOIN
    Country dest_country ON dest_airport."Country" = dest_country."Name"
ORDER BY
    routes."Price" DESC
LIMIT 10;
            """
    cur.execute(query)
    expensive_flights = cur.fetchall()

    return render_template("expensiveflights.html", expensive_flights=expensive_flights)


@app.route('/idle_routes')
def idle_routes():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
SELECT
    src_airport."Name" AS Source_Airport_Name,
    src_airport."Country" AS Source_Country,
    dest_airport."Country" AS Destination_Country,
    dest_airport."Name" AS Destination_Airport_Name,
    COUNT(*) AS Number_of_Flights
FROM
    Routes routes
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
GROUP BY
    Source_Airport_Name, Destination_Airport_Name, Source_Country, Destination_Country
ORDER BY
    Number_of_Flights ASC
LIMIT 10;
            """
    cur.execute(query)
    idle_routes = cur.fetchall()

    return render_template("idleroutes.html", idle_routes=idle_routes)


@app.route('/cheapest_flights')
def cheapest_flights():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
SELECT
    airline."Name" AS Airline_Name,
    src_airport."Name" AS Source_Airport_Name,
    src_country."Name" AS Source_Country,
    dest_airport."Name" AS Destination_Airport_Name,
    dest_country."Name" AS Destination_Country,
    routes."Price"
FROM
    Routes routes
JOIN
    Airline airline ON routes."Airline ID" = airline."Airline ID"
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
JOIN
    Country src_country ON src_airport."Country" = src_country."Name"
JOIN
    Country dest_country ON dest_airport."Country" = dest_country."Name"
ORDER BY
    routes."Price" ASC
LIMIT 10;
            """
    cur.execute(query)
    cheapest_flights = cur.fetchall()

    return render_template("cheapestflights.html", cheapest_flights=cheapest_flights)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            'SELECT * FROM "user" WHERE email = %s AND password = %s', (email, password,))
        # Use fetchone() instead of fetchall() since you're expecting one user
        user = cur.fetchone()
        if user:
            session['loggedin'] = True
            # Use correct column name 'phone_number'
            session['phonenumber'] = user['phone number']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return render_template('index.html', message=message)
        else:
            message = flash ('Please enter correct email / password!')
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if the user is logged in
    if 'loggedin' in session and session['loggedin']:
        # Get user information from the session
        name = session['name']
        email = session['email']
        
        
        # Render the profile template with user information
        return render_template('profile.html', name=name, email=email)
    else:
        # If user is not logged in, redirect to the login page
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        phoneNumber = request.form['phoneNumber']
        cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM "user" WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not userName or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO "user" VALUES (%s, %s, %s, %s)',
                           (userName, email, password, phoneNumber))
            con.commit()
            message = 'You have successfully registered!'
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('register.html', message=message)

@app.route("/search", methods=['GET', 'POST'])
def search():
    cur = con.cursor()
    cur.execute("SELECT \"Name\" FROM Country")
    countries = [row[0] for row in cur.fetchall()]

    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        session['source'] = source
        session['destination'] = destination
        return redirect(url_for('search_results'))

    # Check if the user is logged in
    if 'loggedin' not in session:
        flash('Please login or register first!', 'warning')
        return redirect(url_for('login'))

    return render_template("searchflights.html", countries=countries)


@app.route("/search/results", methods=['GET', 'POST'])
def search_results(source=None, destination=None):
    if source is None or destination is None:
        source = session.get('source')
        destination = session.get('destination')

    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = """
-- Find direct and indirect flights
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
ORDER BY
  "hops";

        """
    cur.execute(query, (source, destination, source, destination, source, destination))
    result = cur.fetchall()
    return render_template("searchresults.html", flights=result)

from flask import request, session

@app.route("/sort", methods=['POST'])
def sort():
    sort_option = request.form['sort_option']
    sort_order = request.form['sort_order']

    if 'source' in session and 'destination' in session:
        source = session['source']
        destination = session['destination']
    else:
        # Handle the case when source and destination are not set in the session
        return redirect(url_for('search'))

    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Define the SQL query based on the selected sorting option and order
    if sort_option == 'price' and sort_order == 'asc':
        query = """
-- Find direct and indirect flights
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
ORDER BY
  "Price";
        """
    elif sort_option == 'price' and sort_order == 'desc':
        query = """
-- Find direct and indirect flights
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
ORDER BY
  "Price" DESC;
        """
    elif sort_option == 'duration' and sort_order == 'asc':
        query = """
-- Find direct and indirect flights
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
ORDER BY
  "Flight Duration";
        """
    elif sort_option == 'duration' and sort_order == 'desc':
        query = """
-- Find direct and indirect flights
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
ORDER BY
  "Flight Duration" DESC;
        """
    else:
        # Handle invalid sorting option or order
        flash('Invalid sorting option or order', 'danger')
        return redirect(url_for('search_results'))

    cur.execute(query, (source, destination, source, destination, source, destination))

    result = cur.fetchall()
    return render_template("searchresults.html", flights=result)



@app.before_request
def before_request():
    # This function will be called before each request
    if 'loggedin' not in session and request.endpoint not in ['login', 'register']:
        flash('Please login or register first!', 'warning')
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
