# Flask imports
from flask import Flask, render_template
from flask_socketio import SocketIO

# Imports
from dotenv import load_dotenv 
import sqlite3
import os
import datetime
import math


# Configure environment
load_dotenv('/usr/files/server/.credentials/.env') 
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
socket = SocketIO(app)

# Function to get events lists for each day 
def get_event_lists(weather_daily, events):
    event_lists = []
    for i,day in enumerate(weather_daily):
        # For each day, create a seperate list
        day_events = []
        for event in events:
            # For each event, format string. If time specified, add to string. 
            if event[1] == day[1]:
                if event[6] == 1:
                    event_text = event[0]
                else:
                    event_text = f"{event[0]} ({event[4][11:16]} to {event[5][11:16]})"
                # Add event string to day list
                day_events.append(event_text)
        # If there are no events, add string to specify this
        if not day_events:
            if i == 0:
                day_events.append("No Events Today")
            else:
                day_events.append(" ")
        # Add day list to events list (should be 7 in total)
        event_lists.append(day_events)
    return event_lists


def get_champions_league_status(liverpool_matches):
    # Function to iterate through each match and find if a champions league game is scheduled. If not, we're knocked out (or draw hasnt happened, but couldnt be arsed developing for that)
    for match in liverpool_matches[3:]:
        print(match)
        if match[0] == "CL":
            return match[1]
    return "Knocked Out"

# Route to open and handle the main kiosk page
@app.route('/')
def index():
    db = sqlite3.connect('/usr/files/server/database.db')
    c = db.cursor()
    c.execute("SELECT * FROM Events")
    events = c.fetchall()
    c.execute("SELECT * FROM Liverpool_Matches")
    liverpool_matches = c.fetchall()
    c.execute("SELECT * FROM Liverpool_Status")
    liverpool_status = c.fetchall()
    c.execute("SELECT * FROM Warton_Flight  ORDER BY last_seen DESC LIMIT 1")
    warton_flight = c.fetchall()
    c.execute("SELECT * FROM Weather_Daily")
    weather_daily = c.fetchall()
    c.execute("SELECT * FROM Weather_Hourly LIMIT 10")
    weather_hourly = c.fetchall()
    c.execute("SELECT * FROM News ORDER BY Date DESC")
    news = c.fetchall()
    c.execute("SELECT * FROM BAE_Stock")
    stock = c.fetchall()
    db.close()
    event_lists = get_event_lists(weather_daily, events)
    # If there are less than 5 events today, get the amount needed to multiply to show 5 (assures width meets design)
    carousel_size = math.ceil(2 / len(event_lists[0]))
    cl_status = get_champions_league_status(liverpool_matches)
    return render_template('index.html', 
                           events=events, 
                           liverpool_matches=liverpool_matches, 
                           liverpool_status=liverpool_status, 
                           warton_flight=warton_flight, 
                           weather_daily=weather_daily, 
                           weather_hourly=weather_hourly,
                           event_lists=event_lists,
                           carousel_size=carousel_size,
                           cl_status = cl_status,
                           news=news,
                           stock=stock)

if __name__ == '__main__':
    socket.run(app,host='0.0.0.0',debug=True,allow_unsafe_werkzeug=True)
    