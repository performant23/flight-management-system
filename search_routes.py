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
from flask import request, session

con = get_db()
search_routes = Blueprint('search_routes', __name__)

@search_routes.route("/search", methods=['GET', 'POST'])
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

    
    if 'loggedin' not in session:
        flash('Please login or register first!', 'warning')
        return redirect(url_for('login'))

    return render_template("searchflights.html", countries=countries)

@search_routes.route("/search/results", methods=['GET', 'POST'])
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

@search_routes.route("/sort", methods=['POST'])
def sort():
    sort_option = request.form['sort_option']
    sort_order = request.form['sort_order']

    if 'source' in session and 'destination' in session:
        source = session['source']
        destination = session['destination']
    else:
       
        return redirect(url_for('search'))

    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    
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
        
        flash('Invalid sorting option or order', 'danger')
        return redirect(url_for('search_results'))

    cur.execute(query, (source, destination, source, destination, source, destination))

    result = cur.fetchall()
    return render_template("searchresults.html", flights=result)
