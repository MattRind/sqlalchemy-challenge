# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# note: cannot use same path string as used in jupyter notebook for same sqlite file !!! --
engine = create_engine(r"sqlite:///C:\Users\mrindfleisch\Desktop\Analysis Projects\Assignments\module10\sqlalchemy-challenge\SurfsUp\Resources\hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br>"
        f"/api/v1.0/precipitation<br/>"
        f"<br>"
        f"/api/v1.0/stations<br/>"
        f"<br>"
        f"/api/v1.0/tobs<br/>"
        f"<br>"
        f"/api/v1.0/&lt;start&gt; &emsp;  enter start date; it must be in <b>yyyy-mm-dd</b> format<br/>"
        f"<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; &emsp;  enter start date, then /end date; dates must be in <b>yyyy-mm-dd</b> format<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Dictionary of the query results from your precipitation analysis (last 12 months)"""
    all_data = session.query(Measurements)
    date_one_year_prior = '2016-08-23'  #this date determined in climate_starter.ipynb
    last_12_mo_data = all_data.filter(Measurements.date >= date_one_year_prior)
    dates_list = []
    precipitation_list = []
    for row in last_12_mo_data: 
        dates_list.append(row.date) 
        precipitation_list.append(row.prcp)
    # direction specify that 
    dictionary = dict(zip(dates_list, precipitation_list))
    session.close()
    return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def stations():

    """JSON list of stations from the dataset"""
    results = session.query(Stations.name, Stations.station).all()
    all_stations = []
    for name, station in results:
        station_dict = {}
        station_dict["station name"] = name
        station_dict["station designation"] = station
        all_stations.append(station_dict)
    session.close()
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    """Query of dates & tobs of the most-active station for the previous year of data"""
    USC00519281_only = session.query(Measurements).filter_by(station = 'USC00519281')
    date_one_year_prior = '2016-08-18'  #this date determined in climate_starter.ipynb
    USC00519281_only_last_yr = USC00519281_only.filter(Measurements.date >= date_one_year_prior)
    dates_list = []
    tobs_list = []
    for row in USC00519281_only_last_yr: 
        dates_list.append(row.date) 
        tobs_list.append(row.tobs)
    tobs_dict = dict(zip(dates_list, tobs_list))
    session.close()
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def date_to_end(start):

    """min tobs, max tobs and average tobs of specified date to most recent date"""
    sel = [ 
       func.min(Measurements.tobs), 
       func.max(Measurements.tobs), 
       func.avg(Measurements.tobs)
       ]
    tobs_data_user_start_date = session.query(*sel).\
    filter(Measurements.date > start).first()
    session.close()
    return list(tobs_data_user_start_date)

@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start, end):

    """min tobs, max tobs and average tobs of specified date range"""
    sel = [ 
       func.min(Measurements.tobs), 
       func.max(Measurements.tobs), 
       func.avg(Measurements.tobs)
       ]
    tobs_data_user_date_range = session.query(*sel).\
    filter(Measurements.date > start, Measurements.date < end).\
    first()
    session.close()
    return list(tobs_data_user_date_range)

if __name__ == '__main__':
    app.run(debug=True)

