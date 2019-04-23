# Import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

from flask import Flask, jsonify


# Set up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect database
Base = automap_base()
# Reflect tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Calculate the date 1 year ago from the last data point in the database
latest = np.ravel(session.query(Measurement.date).order_by(Measurement.date.desc()).first())[0]

latest_date = dt.datetime.strptime(latest,'%Y-%m-%d')
one_year_before = latest_date - dt.timedelta(days=366)

# Reset session for next query
session.rollback()

# Function for getting min, max, and average temps from given dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.

    Args:
    start_date (string): A date string in the format %Y-%m-%d
    end_date (string): A date string in the format %Y-%m-%d

    Returns:
    TMIN, TAVE, and TMAX
    """

    output = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Reset session for next query
    session.rollback()

    return output

# Setup flask
app = Flask(__name__)

# Home page definition
@app.route("/")
def home():
    # List of available routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/><br/>"
        f"Input start and end dates as YYYY-MM-DD"
    )

# Precipitation page definition
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data
    # Perform a query to retrieve the date and precipitation scores
    lastyear = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > one_year_before).all()
    
    # Reset session for next query
    session.rollback()

    # Convert query results into jsonify-able form
    precip = {}
    for i in lastyear:
        precip[i[0]] = i[1]

    return jsonify(precip)

# Stations page definitions
@app.route("/api/v1.0/stations")
def stations():
    # List the stations
    station_query = session.query(distinct(Measurement.station)).all()

    # Reset session for next query
    session.rollback()

    # Convert query results into jsonify-able form
    stations = list(np.ravel(station_query))

    return jsonify(stations)

# Temperature Observations page definition
@app.route("/api/v1.0/tobs")
def tobs():
    # Design a query to retrieve the last 12 months of temperature observation data
    # Perform a query to retrieve the date and temperature observations
    lastyear = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > one_year_before).all()
    
    # Reset session for next query
    session.rollback()

    # Convert query results into jsonify-able form
    temps = {}
    for i in lastyear:
        temps[i[0]] = i[1]

    return jsonify(temps)

# Date Start page definition
@app.route("/api/v1.0/<start>")
def date_start(start):
    
    # Call function with given date as start and last data point as end
    metrics = calc_temps(start, latest_date)
    
    metrics_output = {}
    for x in metrics:
        metrics_output['Minimum Temperature'] = x[0]
        metrics_output['Average Temperature'] = x[1]
        metrics_output['Maximum Temperature'] = x[2]
  
    return jsonify(metrics_output)

# Date Range page definition
@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
    # Call function with given date as start and last data point as end
    metrics = calc_temps(start, end)
    
    metrics_output = {}
    for x in metrics:
        metrics_output['Minimum Temperature'] = x[0]
        metrics_output['Average Temperature'] = x[1]
        metrics_output['Maximum Temperature'] = x[2]
  
    return jsonify(metrics_output)

if __name__ == '__main__':
    app.run(debug=True)