# Imports
import urllib.request 
import json 
import datetime 
import sqlite3
# Local Imports
from data.utilities import logging

_latitude = "53.477989"
_longitude = "-2.258230"
_timezone = "GB"

_db = sqlite3.connect('/usr/files/server/database.db')
_c = _db.cursor()

_c.execute("""
    CREATE TABLE IF NOT EXISTS Weather_Hourly(
                                    reading_type TEXT,
                                    time TEXT,
                                    temp REAL, 
                                    code TEXT, 
                                    weather TEXT, 
                                    windspeed REAL)
    """)


def get_data():
    logging.get_start_info(__name__)
    record_count = 0

    try:
        with urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?latitude={_latitude}&longitude={_longitude}&hourly=temperature_2m,weathercode,windspeed_10m&daily=sunrise,sunset&current_weather=true&windspeed_unit=mph&timezone={_timezone}") as url:
            data = json.load(url)

        if bool(data):
            _c.execute("""
                DELETE FROM Weather_Hourly
                """)

        with open('/usr/files/scripts/python/code_translation.json') as code_translation_source:
            code_translation = json.load(code_translation_source)

        # Strips minutes for comparison to dates
        current_time = (datetime.datetime.now().replace(minute=0, second=0, microsecond=0).isoformat())[:-3] 

        # Iterate through data list to find current date
        for index, date in enumerate(data['daily']['time']):
            if current_time[0:10] == date:
                current_daily_index = index
                break

        # Use current date to find current hour
        for index, date in enumerate(data['hourly']['time']):
            if current_time == date:
                current_hourly_index = index
                break

        sunsets = (data['daily']['sunset'][current_daily_index:])
        sunrises = (data['daily']['sunrise'][current_daily_index:])

        weather_times = (data['hourly']['time'][current_hourly_index:])
        weather_temps = (data['hourly']['temperature_2m'][current_hourly_index:])
        weather_codes = (data['hourly']['weathercode'][current_hourly_index:])
        weather_windspeed = (data['hourly']['windspeed_10m'][current_hourly_index:])

        day_code = ""

        # Compare weather and sun status to find a matching date (with hour) for the first sunstatus change. 
        # Set inital day code to the opposite of change, for hours before change occurs
        for weather_time_index in range(len(weather_times)):
            for sunrise_index in range(len(sunrises)):
                if sunrises[sunrise_index][0:13] == weather_times[weather_time_index][0:13]:
                    day_code = "n"
                    break
                if sunsets[sunrise_index][0:13] == weather_times[weather_time_index][0:13]:
                    day_code = "d"
                    break
            if day_code != "":
                break

        _c.execute("""
            DELETE FROM Weather_Hourly
            """)

        for hour_index in range(len(weather_times)):
            weather_reading = {
                "reading_type": "weather",
                "time": (weather_times[hour_index]),
                "temp": (weather_temps[hour_index]),
                "code": day_code + str(weather_codes[hour_index]),
                "weather": (code_translation[str(weather_codes[hour_index])]),
                "windspeed": (weather_windspeed[hour_index])
            }

            record_count = record_count + 1

            _c.execute("""
                INSERT INTO Weather_Hourly (
                    reading_type, 
                    time, 
                    temp, 
                    code, 
                    weather, 
                    windspeed)
                VALUES(
                    :reading_type, 
                    :time, 
                    :temp, 
                    :code, 
                    :weather, 
                    :windspeed)    
            """,weather_reading)

            for sunrise_index in range(len(sunrises)):

                # Find if hour inserted matches a sunrise. If it does, add sunrise details then set day code to "d" (sun has now rose)
                if sunrises[sunrise_index][0:13] == weather_times[hour_index][0:13]:
                    sunrise_reading = {
                        "reading_type": "sun",
                        "time": (sunrises[sunrise_index]),
                        "weather": "Sunrise"
                    }

                    record_count = record_count + 1

                    _c.execute("""
                        INSERT INTO Weather_Hourly (
                            reading_type, 
                            time, 
                            weather)
                        VALUES(
                            :reading_type, 
                            :time, 
                            :weather)    
                    """,sunrise_reading)
                    day_code = "d"

                # Find if hour inserted matches a sunset. If it does, add sunset details then set day code to "n" (sun has now set)
                # Uses sunrise index as always a match between the two
                elif sunsets[sunrise_index][0:13] == weather_times[hour_index][0:13]:
                    sunset_reading = {
                        "reading_type": "sun",
                        "time": (sunsets[sunrise_index]),
                        "weather": "Sunset"
                    }

                    record_count = record_count + 1

                    _c.execute("""
                        INSERT INTO Weather_Hourly (
                            reading_type, 
                            time, 
                            weather)
                        VALUES(
                            :reading_type, 
                            :time, 
                            :weather)    
                    """,sunset_reading)
                    day_code = "n"
        _db.commit()
        _db.close()
        logging.get_finish_info(record_count)
        logging.write_log()

    except Exception as e:
        logging.get_error_message(e.args[0])
        logging.write_log()
        _db.commit()
        _db.close()
