# Imports
import datetime # Used to manage time
import os.path
import sqlite3
# Imports for handling google calendar api
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# Local Imports
from data.utilities import logging

_db = sqlite3.connect('/usr/files/server/database.db')
_c = _db.cursor()
_c.execute("""
    CREATE TABLE IF NOT EXISTS Events(
          event TEXT, 
          event_date TEXT, 
          event_date_end TEXT, 
          multiple_days INTEGER, 
          start_date REAL, 
          end_date REAL, 
          all_day INTEGER, 
          location TEXT)
    """)

# Google authentication script for API
# Appears to revoke after 7 days, unless the project is in verification
# Uses creentials.json from google api to create authenticaiton token
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
_creds = None
if os.path.exists("/usr/files/scripts/python/.credentials/token.json"):
    _creds = Credentials.from_authorized_user_file("/usr/files/scripts/python/.credentials/token.json", SCOPES)
if not _creds or not _creds.valid:
    if _creds and _creds.expired and _creds.refresh_token:
        _creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("/usr/files/scripts/python/.credentials/credentials.json", SCOPES)
        _creds = flow.run_local_server(port=0)
    with open("/usr/files/scripts/python/.credentials/token.json", "w") as token:
        token.write(_creds.to_json())


def get_data():
    logging.get_start_info(__name__)
    record_count = 0

    try:
        service = build("calendar", "v3", credentials=_creds)

        # Set date range (today - 7 days)
        date_min = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()  # 'Z' indicates UTC time
        date_max = (datetime.datetime.now(datetime.timezone.utc).astimezone() + datetime.timedelta(days=7)).isoformat()

        # Get events from date range of primary calendar
        events_result = (service.events().list(calendarId="primary",timeMin=date_min,timeMax=date_max,singleEvents=True,orderBy="startTime",).execute())
        events = events_result.get("items", [])

        
        # If any events have been returned, empty the table
        if bool(events):
            _c.execute("""
                DELETE FROM Events
                """)


        for day in range(8):
            # Format day of iteration to string to compare with calendar
            day_string = (datetime.datetime.now(datetime.timezone.utc).astimezone() + datetime.timedelta(days=day)).isoformat()[0:10]
            # Also format for comparison with API results
            day = datetime.datetime.strptime(day_string, "%Y-%m-%d")

            for event in events:
                # For every event, get the start and end as both string and date
                event_date_start_string = (event["start"].get("dateTime", event["start"].get("date")))[0:10]
                event_date_start = datetime.datetime.strptime(event_date_start_string, "%Y-%m-%d")
                event_date_end_string = (event["end"].get("dateTime", event["end"].get("date")))[0:10]
                event_date_end = datetime.datetime.strptime(event_date_end_string, "%Y-%m-%d")

                # If the event is not all day mark as such
                if event_date_start_string == event_date_end_string:
                    multiple_days = False
                # Or if a single, all day event, mark as such and set end date to same as start
                elif (event_date_end - datetime.timedelta(days=1)) == event_date_start:
                    event_date_end = event_date_start
                    event_date_end_string = event_date_start_string
                    multiple_days = False
                # Or multiple days, mark as such and mark end date
                else:
                    event_date_end = event_date_end - datetime.timedelta(days=1)
                    event_date_end_string = event_date_end.isoformat()[0:10]
                    multiple_days = True
                
                # If the iteration is within event span
                if event_date_start <= day <= event_date_end:
                        
                    event_dict = {
                        "event":(event["summary"]),
                        "event_date":day_string,
                        "event_date_end": event_date_end_string,
                        "multiple_days": multiple_days,
                        "start_date":None,
                        "end_date":None,
                        "all_day":None,
                        "location":None
                    }

                    # Attempt to retrieve event datetime (will not work if all day event)
                    try:
                        event_dict["start_date"] = (event["start"]["dateTime"])
                        event_dict["end_date"] = (event["end"]["dateTime"])
                        event_dict["all_day"] = (False)
                    # Otherwise get just existing date string
                    except:
                        event_dict["start_date"] = event_date_start_string
                        event_dict["end_date"] = event_date_end_string
                        event_dict["all_day"] = (True)

                    # Similarly try to get location, if set
                    try:
                        event_dict["location"] = (event["location"])
                    except:
                        pass

                    record_count = record_count + 1
                    # Insert metrics into the hourly weather table
                    _c.execute("""
                        INSERT INTO Events (
                              event, 
                              event_date, 
                              event_date_end, 
                              multiple_days, 
                              start_date, 
                              end_date, 
                              all_day, 
                              location)
                        VALUES(
                              :event, 
                              :event_date, 
                              :event_date_end, 
                              :multiple_days, 
                              :start_date, 
                              :end_date, 
                              :all_day, 
                              :location)    
                    """,event_dict)
        _db.commit()
        _db.close()

        logging.get_finish_info(record_count)
        logging.write_log()

    except Exception as e:
        logging.get_error_message(e.args[0])
        logging.write_log()
        _db.commit()
        _db.close()