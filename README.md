# Flight Management System (Flight Planner)

## Overview

Flight Planner is a web application designed to assist users in finding and organizing their flights. Built using Flask, a micro web framework written in Python, it allows users to search for flights, view various statistics like the longest and shortest flights, and manage their flight bookings. The application uses a PostgreSQL database to store and query flight information.

## Features

- **Flight Search**: Users can search for flights based on their preferences.
- **Statistics**: View lists of the longest, shortest, busiest, most expensive, and cheapest flights.
- **User Authentication**: Secure login and registration system for users.
- **Profile Management**: Users can view their profile and manage bookings.
- **Flight Sorting**: Flights can be sorted based on price or duration.

## Installation

1. Clone the repository to your local machine.
2. Ensure that Python 3 and pip are installed.
3. Install Flask: `pip install Flask`.
4. Install psycopg2: `pip install psycopg2`.
5. Set up a PostgreSQL database and update the DB_HOST, DB_NAME, DB_USER, and DB_PASS in the code to match your database credentials.

## Usage

1. Run the application using `python app.py`.
2. Access the web application by navigating to `localhost:5000` in your web browser.
3. Register for an account or login.
4. Start searching for flights and explore various flight statistics.

## Contributions

Contributions are welcome! Please fork the repository and open a pull request with your proposed changes.

## License

Distributed under the MIT License. See `LICENSE` for more information.
---
