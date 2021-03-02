# Dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################
# Database Setup
#################################
engine = create_engine('sqlite:///hawaii.sqlite')

# Reflect existing database into new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measure = Base.classes.measurement
Station = Base.classes.station

#################################
# Flask Setup
#################################

app = Flask(__name__)

#################################
# Flask Routes
#################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/enter_start_here <br/>"
        f"/api/v1.0/enter_start_here/enter_end_here"
    )

@app.route("/api/v1.0/precipitation")
def date_prcp():
    # Create session link from Python to DB
    session = Session(engine)
    
    # Query all dates and precipitation values
    results = session.query(Measure.date, Measure.prcp).all()
    
    session.close()
    
     # Create a dictionary with date and prcp from row and appends
     # to list to be displayed
    all_date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {date:prcp}
        all_date_prcp.append(date_prcp_dict)

    return jsonify(all_date_prcp)

@app.route('/api/v1.0/stations')
def stations():
    # Create session link from Python to DB
    session = Session(engine)
    
    # Query all station names
    results = session.query(Station.name).all()
    
    session.close()
    
    # Create list of stations to be displayed
    all_stations = []
    for row in results:
        all_stations.append(row)

    return jsonify(all_stations)    

@app.route('/api/v1.0/tobs')
def tobs():
    # Create session link from Python to DB
    session = Session(engine)

    # Find most recent date in measurement table
    recent_date = session.query(Measure.date).order_by(Measure.date.desc()).first()
    recent_date = dt.datetime.strptime(recent_date[0],'%Y-%m-%d')

    # Calculate the date one year from the last data in data set
    date_year_ago = recent_date - dt.timedelta(days=365)
    date_year_ago = date_year_ago.strftime('%Y-%m-%d')

    # Find the most active station
    active_station = session.query(Station.station,Station.name,func.count(Measure.station)).\
              filter(Measure.station == Station.station).group_by(Station.station).order_by(func.count(Measure.station).desc()).\
              first()
    most_active = active_station[0]

    # Query all dates and temperature values
    results = session.query(Measure.date, Measure.tobs).\
              filter(Measure.date >= date_year_ago).\
                  filter(Measure.station == most_active).all()
    
    session.close()

    # Create list of temperature observations to be displayed
    all_tobs = []
    for date,tobs in results:
        date_tobs_dict = {date:tobs}
        all_tobs.append(date_tobs_dict)

    return jsonify(all_tobs)  

@app.route('/api/v1.0/<start>')
def start(start):
    # Create session link from Python to DB
    session = Session(engine)

    # Query all temperatures from start date to most recent date
    max_temp = session.query(func.max(Measure.tobs)).\
        filter(Measure.date >= start).all()[0][0]
    min_temp = session.query(func.min(Measure.tobs)).\
        filter(Measure.date >= start).all()[0][0]
    avg_temp = round(session.query(func.avg(Measure.tobs)).\
        filter(Measure.date >= start).all()[0][0],2)

    session.close()

    # Create list with min, max, and avg temp for given range
    # beginning with provided start date
    all_temp = [{'Max Temp':max_temp},{'Min Temp':min_temp},{'Avg Temp':avg_temp}]

    return jsonify(all_temp)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    # Create session link from Python to DB
    session = Session(engine)

    # Query all temperatures from start date to end date
    max_temp = session.query(func.max(Measure.tobs)).\
        filter(Measure.date >= start).\
            filter(Measure.date <= end).all()[0][0]
    min_temp = session.query(func.min(Measure.tobs)).\
        filter(Measure.date >= start).\
            filter(Measure.date <= end).all()[0][0]
    avg_temp = round(session.query(func.avg(Measure.tobs)).\
        filter(Measure.date >= start).\
            filter(Measure.date <= end).all()[0][0],2)

    session.close()

    # Create list with min, max, and avg temp for given range
    # beginning with provided start date and end date
    all_temp = [{'Max Temp':max_temp},{'Min Temp':min_temp},{'Avg Temp':avg_temp}]

    return jsonify(all_temp)

if __name__ == '__main__':
    app.run(debug=True)