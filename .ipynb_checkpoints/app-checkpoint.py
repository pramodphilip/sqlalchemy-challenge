import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################
# Database Setup
#################################
engine = create_engine('sqlite:///hawaii.sqlite')

#reflect existing database into new model
Base = automap_base()
#reflect the tables
Base.prepare(engine, reflect=True)

#Save reference to the table
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
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def date_prcp():
    #Create session link from Python to DB
    session = Session(engine)
    
    #Query all dates and precipitation values
    results = session.query(Measure.date, Measure.prcp).all()
    
    session.close()
    
    #Convert list of tuples into normal list
    date_prcp = list(np.ravel(results))

    return jsonify(date_prcp)

if __name__ == '__main__':
    app.run(debug=True)