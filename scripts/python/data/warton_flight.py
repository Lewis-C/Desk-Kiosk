# Imports
import urllib.request # Used to obtain API requests
import json # Used to write and read JSONs from API requests and for website
import datetime # Used to manage time
import time
import sqlite3
# Local Imports
from data.utilities import logging

_airport = "EGNO"

_db = sqlite3.connect('/usr/files/server/database.db')
_c = _db.cursor()
_c.execute("""
    CREATE TABLE IF NOT EXISTS Warton_Flight(
                                            flight_type TEXT,
                                            icao_type TEXT,
                                            icao TEXT,
                                            first_seen TEXT,
                                            last_seen TEXT,
                                            dep_airpt TEXT,
                                            arr_airpt TEXT,
                                            callsign TEXT,
                                            type TEXT,
                                            manufacturer TEXT,
                                            registration TEXT,
                                            registration_country TEXT,
                                            registration_owner TEXT,
                                            photo_url TEXT)
    """)


def get_data():
    
    logging.get_start_info(__name__)
    record_count = 0

    try:
        # Set time span to search for flights
        time_end = int(time.time())
        time_start = time_end - 259200 # 3 days

        # Get arrivals within timespan at airport
        with urllib.request.urlopen(f"https://opensky-network.org/api/flights/arrival?airport={_airport}&begin={time_start}&end={time_end}") as url:
            arrival_data = json.load(url)

        # Get departures within timespan at airport
        with urllib.request.urlopen(f"https://opensky-network.org/api/flights/departure?airport={_airport}&begin={time_start}&end={time_end}") as url:
            departure_data = json.load(url)

        # Finds the most recent flight activity, departure or arrival
        if((departure_data[0]["lastSeen"]) > (arrival_data[0]["lastSeen"])):
            flight_type = "departure"
            flight = departure_data[0] 
        else:
            flight_type = "arrival"
            flight = arrival_data[0] 

        # If a flight is retrieved
        if bool(flight):
            # Use the flights icao24 in another api
            with urllib.request.urlopen(f"https://api.adsbdb.com/v0/aircraft/{flight['icao24']}") as url:
                aircraft = json.load(url)
                aircraft = aircraft['response']['aircraft']

            # Build dict with details from both flight and aircraft apis
            result = {
                "flight_type": flight_type,
                "icao_type" : aircraft['icao_type'],
                "icao":flight['icao24'],
                "first_seen": datetime.datetime.fromtimestamp((flight['firstSeen'])).strftime('%Y-%m-%d %H:%M:%S'),
                "last_seen" : datetime.datetime.fromtimestamp((flight['lastSeen'])).strftime('%Y-%m-%d %H:%M:%S'),
                "dep_airpt" : flight['estDepartureAirport'],
                "arr_airpt" : flight['estArrivalAirport'],
                "callsign" : flight['callsign'].strip(),
                "type" : aircraft['type'],
                "manufacturer" : aircraft['manufacturer'],
                "registration" : aircraft['registration'],
                "registration_country" : aircraft['registered_owner_country_name'],
                "registration_owner" : aircraft['registered_owner'],
                "photo_url" : aircraft['url_photo']
            }

            _c.execute("""
                DELETE FROM Warton_Flight
                """)

            record_count = record_count + 1

            _c.execute("""
                INSERT INTO Warton_Flight (
                    flight_type,
                    icao_type,
                    icao,
                    first_seen,
                    last_seen,
                    dep_airpt,
                    arr_airpt,
                    callsign,
                    type,
                    manufacturer,
                    registration,
                    registration_country,
                    registration_owner,
                    photo_url)
                VALUES(
                    :flight_type,
                    :icao_type, 
                    :icao, 
                    :first_seen, 
                    :last_seen, 
                    :dep_airpt, 
                    :arr_airpt, 
                    :callsign, 
                    :type, 
                    :manufacturer, 
                    :registration, 
                    :registration_country, 
                    :registration_owner, 
                    :photo_url)    
            """,result)

            _db.commit()
            _db.close()

            logging.get_finish_info(record_count)
            logging.write_log()
        else:
            logging.get_finish_info(record_count)
            logging.write_log()
            _db.commit()
            _db.close()

    except Exception as e:
        logging.get_error_message(e.args[0])
        logging.write_log()
        _db.commit()
        _db.close()