import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from datetime import datetime, timedelta

## import flask
from flask import Flask, jsonify

#################################################
## Database Setup
#################################################

## Create engine to hawaii.sqlite
database_path = "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

## Reflect an existing database into a new model
Base = automap_base()
## Reflect the tables
Base.prepare(engine, reflect=True)

## Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
## Flask Setup
#################################################

## Create an app
app = Flask(__name__)

#################################################
## Home Page
#################################################

## Define the Home Page app route
## List all routes that are available.
@app.route("/")
def home_page():
    return (
        f"Welcome to the Climate App!<br/>"
        f"<br>"
        f"Available Routes: (copy and paste one at the end of the web address)<br/>"
        f"<br/>"

        f"Convert the query results to a dictionary using date as the key and prcp as the value. "
        f"Return the JSON representation of your dictionary.<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"

        f"Return a JSON list of stations from the dataset.<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"

        f"Query the dates and temperature observations of the most active station for the last year of data. "
        f"Return a JSON list of temperature observations (TOBS) for the previous year.<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"

        f"When given the start only, calculate TMIN, TAVG, and TMAX "
        f"for all dates greater than and equal to the start date.<br/>"
        f"(replace 'start' with date format YYYY-MM-DD)<br/>"
        f"/api/v1.0/start<br/>"
        f"<br/>"

        f"When given the start and the end date, calculate the TMIN, TAVG, and TMAX "
        f"for dates between the start and end date inclusive.<br/>"
        f"(replace 'start' and 'end' with date format YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end<br/>"
    )
    
# @app.route("/api/v1.0/names")
# def names():
#     # Create our session (link) from Python to the DB
#     session = Session(engine)

#     """Return a list of all passenger names"""
#     # Query all passengers
#     results = session.query(Passenger.name).all()

#     session.close()

#     # Convert list of tuples into normal list
#     all_names = list(np.ravel(results))

#     return jsonify(all_names)


#################################################
## Precipitation
#################################################

## Convert the query results to a dictionary using date as the key and prcp as the value.
## Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def prcp():
    ## Create the session (link) from Python to the DB
    session = Session(engine)

    ## Find the most recent date in the data set.
    results_meas = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).all()
    
    ## Calculate the date one year from the last date in data set.
    recent_date = results_meas[0]
    recent_date_datetime = datetime.strptime(recent_date[0], "%Y-%m-%d")

    ## Use time delta to subtract 365 days from the datetime type varaible (recent_date_datetime)
    minus_one_year = recent_date_datetime - timedelta(days = 365)

    ## Convert minus_one_year to a string
    minus_one_year_str = datetime.strftime(minus_one_year,"%Y-%m-%d")

    ## Perform a query to retrieve the data and precipitation scores
    data_meas = session.query(Measurement.prcp, Measurement.date).\
        filter(Measurement.date >= minus_one_year_str).all()

    session.close()

    # Convert list of tuples into normal list
    prcp = list(np.ravel(data_meas))

    return jsonify(prcp)

#################################################
## Stations
#################################################

## Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def staions():
    ## Create the session (link) from Python to the DB
    session = Session(engine)

    stations_dist = session.query(Measurement.station).distinct().all()

    session.close()

    ## Do I need to convert???
    ## Convert list of tuples into normal list
    stns = list(np.ravel(stations_dist))

    return jsonify(stns)

#################################################
## TOBS
#################################################

## Query the dates and temperature observations of the most active station for the last year of data.
## Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    ## Create the session (link) from Python to the DB
    session = Session(engine)

    ## Design a query to find the most active stations (i.e. what stations have the most rows?)

    ## List the stations and the counts in descending order.
    sta_count = func.count(Measurement.station)

    results_sta_count = session.query(Measurement.station, sta_count).\
        group_by(Measurement.station).\
        order_by(sta_count.desc()).all()

    ## Find the most active
    most_active = results_sta_count[0]

    ## Query the last 12 months of temperature observation data for this station
    data_most_active = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).\
        filter(Measurement.station == most_active[0]).all()

    ## Convert to Date Time format
    recent_date_dt = datetime.strptime(data_most_active[0][0], "%Y-%m-%d")

    ## Use time delta to subtract 365 days from the datetime type varaible (recent_date_dt)
    minus_one_yr = recent_date_dt - timedelta(days = 365)

    ## Convert minus_one_year to a string
    minus_one_yr_str = datetime.strftime(minus_one_yr,"%Y-%m-%d")

    ## Query TOBS data for the last 12 months of the most active station
    ## most_active[0] equals Station USC00519281

    ## This creates an immutable tuple
    active_temps = session.query(Measurement.tobs).\
                filter(Measurement.date >= minus_one_yr_str).\
                filter(Measurement.station == most_active[0]).all()

    ## Close the session
    session.close()

    ## Convert list of tuples into normal list
    tobs = list(np.ravel(active_temps))

    return jsonify(tobs)


#################################################
## Start Date
#################################################

## When given the start only, calculate TMIN, TAVG, and TMAX 
## for all dates greater than and equal to the start date.

## Sample code
# @app.route("/api/v1.0/justice-league/superhero/<superhero>")
# def justice_league_by_superhero__name(superhero):
#     """Fetch the Justice League character whose superhero matches
#        the path variable supplied by the user, or a 404 if not."""

#     canonicalized = superhero.replace(" ", "").lower()
#     for character in justice_league_members:
#         search_term = character["superhero"].replace(" ", "").lower()

#         if search_term == canonicalized:
#             return jsonify(character)

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    ## Create the session (link) from Python to the DB
    session = Session(engine)

    calc = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start_date).all()
    
    ## Close the session
    session.close()

    ## Convert list of tuples into normal list
    calc_ls = list(np.ravel(calc))

    return jsonify(calc_ls)

#################################################
## Start/End Date
#################################################

## When given the start and the end date, calculate the TMIN, TAVG, and TMAX
## for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    ## Create the session (link) from Python to the DB
    session = Session(engine)

    calc = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start_date).\
             filter(Measurement.date <= end_date).all()
    
    ## Close the session
    session.close()

    ## Convert list of tuples into normal list
    calc_ls = list(np.ravel(calc))

    return jsonify(calc_ls)

## Must be used to run code
if __name__ == '__main__':
    app.run(debug=True)