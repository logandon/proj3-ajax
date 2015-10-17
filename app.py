"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify # For AJAX transactions

import json
import logging

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
# import acp_limits


###
# Globals
###
app = flask.Flask(__name__)
import CONFIG

import uuid
app.secret_key = str(uuid.uuid4())
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)


###
# Pages
###

@app.route("/")
@app.route("/index")
@app.route("/calc")
def index():
  app.logger.debug("Main page entry")
  return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("calc")
    return flask.render_template('page_not_found.html'), 404


###############
#
# AJAX request handlers 
#   These return JSON, rather than rendering pages. 
#
###############
@app.route("/_calc_times")
def calc_times():
  """
  Calculates open/close times from miles, using rules 
  described at http://www.rusa.org/octime_alg.html.
  Expects one URL-encoded argument, the number of miles. 
  """
  app.logger.debug("Got a JSON request");

  km2m = 0.621371
  m2km = 1.60934
  miles = request.args.get('miles', 0, type= float)
  location = request.args.get('location', 0, type = str)
  brev_dist = request.args.get('brev_dist', 0 , type=float)
  date = request.args.get('date', 0, type=str)
  time = request.args.get('time', 0, type=str)
  input_type = request.args.get('input_type', 0, type=str)
  # output = request.args.get('output', 0, type=str)
  start_time = arrow.get(date + ' ' + time, 'MM/DD/YYYY HH:mm')

  if(input_type == "miles"):
    miles = miles*m2km

  if (miles > brev_dist*1.1):
    max_dist_error = {'opening_time': "Error: distance out of range", 'closing_time': "Error: distance out of range"}
    return jsonify(result = max_dist_error)
  elif(miles == 0):
    zero_error = {'opening_time': format_arrow_date(opening_time), 'closing_time': format_arrow_date(closing_time.replace(minutes=+60))}
    return jsonify(result = zero_error)


  if(miles<200):
    opening_time = miles/34
    closing_time = miles/15
  elif(miles > 199 and miles < 399):
    opening_time = 200/34 + ((miles-200)/32)
    closing_time = miles/15
  elif(miles > 399 and miles < 599):
    opening_time = 200/34 + 200/32 + ((miles-400)/30)
    closing_time = miles/15
  elif(miles > 599 and miles < 999):
    opening_time = 200/34 + 200/32 + 200/30 ((miles-600)/28)
    closing_time = 600/15 + ((miles-600)/11.428)
  elif(miles > 999 and miles < 1299):
    opening_time = 200/34 + 200/32 + 200/30 + 400/28 + ((miles-1000)/26)
    closing_time = 600/15 + 400/11.482 + ((miles-1000)/34)
  else:
    max_miles_error = {'opening_time': "Error: out of range", 'closing_time': "Error: out of range"}
    return jsonify(result=max_miles_error)
  return_result = {'opening_time': format_arrow_date(start_time.replace(hours=hours+opening_time)), 'closing_time': format_arrow_date(start_time.replace(hours = hours+closing_time))}
  return jsonify(result=return_result)
#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try: 
        normal = arrow.get( date )
        return normal.format("hh:mm")
    except:
        return "(bad time)"



#############


if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)

    
