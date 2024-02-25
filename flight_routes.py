import csv
import re
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
from psycopg2 import Error
from flask import g
from flask import Blueprint
from app import get_db
from flask import request, session

flight_routes = Blueprint('flight_routes', __name__)

con = get_db()

@flight_routes.route('/flightwonders')
def flightwon():
    return render_template("flightwonders.html")

@flight_routes.route('/longest_flights')
def longest_flights():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
            SELECT
    airline."Name" AS Airline_Name,
    routes."Airline ID" AS Airline_ID,
    src_airport."Name" AS Source_Airport_Name,
    dest_airport."Name" AS Destination_Airport_Name,
    src_airport."Country" AS Source_Country_Name,
    dest_airport."Country" AS Destination_Country_Name,
    routes."Departure Time",
    routes."Arrival Time",
    (EXTRACT(EPOCH FROM routes."Arrival Time") - EXTRACT(EPOCH FROM routes."Departure Time")) AS Flight_Duration,
    routes."Price" AS Price
FROM
    Routes routes
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
JOIN
    Airline airline ON routes."Airline ID" = airline."Airline ID"
ORDER BY
    Flight_Duration DESC
LIMIT 10;
            """
    cur.execute(query)
    longest_flights = cur.fetchall()

    return render_template("longestflights.html", longest_flights=longest_flights)

@flight_routes.route('/shortest_flights')
def shortest_flights():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
SELECT
    airline."Name" AS Airline_Name,
    routes."Airline ID" AS Airline_ID,
    src_airport."Name" AS Source_Airport_Name,
    dest_airport."Name" AS Destination_Airport_Name,
    src_airport."Country" AS Source_Country_Name,
    dest_airport."Country" AS Destination_Country_Name,
    routes."Departure Time",
    routes."Arrival Time",
    (EXTRACT(EPOCH FROM routes."Arrival Time") - EXTRACT(EPOCH FROM routes."Departure Time")) AS Flight_Duration,
    routes."Price" AS Price
FROM
    Routes routes
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
JOIN
    Airline airline ON routes."Airline ID" = airline."Airline ID"
WHERE
    EXTRACT(EPOCH FROM routes."Departure Time") < EXTRACT(EPOCH FROM routes."Arrival Time")
ORDER BY
    Flight_Duration ASC
LIMIT 10;

            """
    cur.execute(query)
    shortest_flights = cur.fetchall()

    return render_template("shortestflights.html", shortest_flights=shortest_flights)

@flight_routes.route('/busiest_routes')
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

@flight_routes.route('/expensive_flights')
def expensive_flights():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
SELECT
    airline."Name" AS Airline_Name,
    routes."Airline ID" AS Airline_ID,
    src_airport."Name" AS Source_Airport_Name,
    dest_airport."Name" AS Destination_Airport_Name,
    src_airport."Country" AS Source_Country_Name,
    dest_airport."Country" AS Destination_Country_Name,
    routes."Departure Time",
    routes."Arrival Time",
    (EXTRACT(EPOCH FROM routes."Arrival Time") - EXTRACT(EPOCH FROM routes."Departure Time")) AS Flight_Duration,
    routes."Price" AS Price
FROM
    Routes routes
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
JOIN
    Airline airline ON routes."Airline ID" = airline."Airline ID"
    WHERE
    EXTRACT(EPOCH FROM routes."Departure Time") < EXTRACT(EPOCH FROM routes."Arrival Time")
ORDER BY
    routes."Price" DESC
LIMIT 10;
            """
    cur.execute(query)
    expensive_flights = cur.fetchall()

    return render_template("expensiveflights.html", expensive_flights=expensive_flights)

@flight_routes.route('/idle_routes')
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

@flight_routes.route('/cheapest_flights')
def cheapest_flights():
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
SELECT
    airline."Name" AS Airline_Name,
    routes."Airline ID" AS Airline_ID,
    src_airport."Name" AS Source_Airport_Name,
    dest_airport."Name" AS Destination_Airport_Name,
    src_airport."Country" AS Source_Country_Name,
    dest_airport."Country" AS Destination_Country_Name,
    routes."Departure Time",
    routes."Arrival Time",
    (EXTRACT(EPOCH FROM routes."Arrival Time") - EXTRACT(EPOCH FROM routes."Departure Time")) AS Flight_Duration,
    routes."Price" AS Price
FROM
    Routes routes
JOIN
    Airports src_airport ON routes."Source Airport ID" = src_airport."Airport ID"
JOIN
    Airports dest_airport ON routes."Destination Airport ID" = dest_airport."Airport ID"
JOIN
    Airline airline ON routes."Airline ID" = airline."Airline ID"
    WHERE
    EXTRACT(EPOCH FROM routes."Departure Time") < EXTRACT(EPOCH FROM routes."Arrival Time")
ORDER BY
    routes."Price" ASC
LIMIT 10;
            """
    cur.execute(query)
    cheapest_flights = cur.fetchall()

    return render_template("cheapestflights.html", cheapest_flights=cheapest_flights)
