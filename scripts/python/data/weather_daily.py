# Imports
import urllib.request # Used to obtain API requests
import json # Used to write and read JSONs from API requests and for website
import datetime # Used to manage time
import sqlite3
# Local Imports
from data.utilities import logging

_latitude = "53.477989"
_longitude = "-2.258230"
_timezone = "GB"

# Connect to database and create cursor
_db = sqlite3.connect('/usr/files/server/database.db')
_c = _db.cursor()

# Create hourly weather table if not exists exists
_c.execute("""
    CREATE TABLE IF NOT EXISTS Weather_Daily(
                                        reading_type TEXT, 
                                        date TEXT, 
                                        date_formatted TEXT, 
                                        weekday TEXT, 
                                        temp_min REAL, 
                                        temp_max REAL, 
                                        temp_avg REAL, 
                                        code TEXT, 
                                        weather TEXT)
    """)

def get_data():
    logging.get_start_info(__name__)
    record_count = 0

    try:
        with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?latitude={_latitude}&longitude={_longitude}&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone={_timezone}") as url:
            data = json.load(url)

        with open('/usr/files/scripts/python/code_translation.json') as code_translation_source:
            code_translation = json.load(code_translation_source)

        if bool(data):
            # Clear existing hourly weather table if exists
            _c.execute("""
                DELETE FROM Weather_Daily
                """)

        # Strips minutes for comparison to dates
        current_time = (datetime.datetime.now().replace(minute=0, second=0, microsecond=0).isoformat())[:-3]

        for index, date in enumerate(data['daily']['time']):
            if current_time[0:10] == date:
                current_daily_index = index
                break

        dates = (data['daily']['time'][current_daily_index:])
        temps_max = (data['daily']['temperature_2m_max'][current_daily_index:])
        temps_min = (data['daily']['temperature_2m_min'][current_daily_index:])
        weathercodes = (data['daily']['weather_code'][current_daily_index:])

        _c.execute("""
            DELETE FROM Weather_Daily
            """)

        # For every day available
        for date_index in range(len(dates)):

            # Build a dict with all weather metrics
            weather_reading = {
                "reading_type": "weather",
                "date": (dates[date_index]),
                "date_formatted": datetime.datetime.strptime((dates[date_index]), '%Y-%m-%d').date().strftime(f'%d{_get_ordinal_suffix(dates[date_index])} %B'),
                "weekday": datetime.datetime.strptime((dates[date_index]), '%Y-%m-%d').date().strftime(f'%A'),
                "temp_min": (temps_min[date_index]),
                "temp_max": (temps_max[date_index]),
                "temp_avg": ((temps_max[date_index]) + (temps_min[date_index]))/2,
                "code": "d" + str(weathercodes[date_index]),
                "weather": (code_translation[str(weathercodes[date_index])]),
            }

            record_count = record_count + 1


            # Insert metrics into the hourly weather table
            _c.execute("""
                INSERT INTO Weather_Daily (
                    reading_type, 
                    date, 
                    date_formatted,
                    weekday, 
                    temp_min, 
                    temp_max, 
                    temp_avg, 
                    code, 
                    weather)
                VALUES(:reading_type, 
                    :date, 
                    :date_formatted,
                    :weekday, 
                    :temp_min, 
                    :temp_max, 
                    :temp_avg, 
                    :code, 
                    :weather)    
            """,weather_reading)

        _db.commit()
        _db.close()
        logging.get_finish_info(record_count)
        logging.write_log()

    except Exception as e:
        logging.get_error_message(e.args[0])
        logging.write_log()
        _db.commit()
        _db.close()


def _get_ordinal_suffix(date):
    # Convert date to it then compare with set of rules to find suffix
    date = int(date[8:])
    date_suffix = ["th", "st", "nd", "rd"]

    if date % 10 in [1, 2, 3] and date not in [11, 12, 13]:
        return date_suffix[date % 10]
    else:
        return date_suffix[0]