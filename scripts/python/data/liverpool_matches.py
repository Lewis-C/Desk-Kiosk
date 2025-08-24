# Imports
import requests
import datetime
from dotenv import load_dotenv 
import sqlite3
import os
# Local Imports
from data.utilities import logging

load_dotenv('/usr/files/scripts/python/.credentials/.env') 
liverpool_id = 64 

_db = sqlite3.connect('/usr/files/server/database.db')
_c = _db.cursor()

_c.execute("""
    CREATE TABLE IF NOT EXISTS Liverpool_Matches(
          match_competition TEXT,
          match_stage TEXT, 
          match_date TEXT, 
          match_time TEXT, 
          home_team TEXT, 
          home_acronym TEXT, 
          home_score TEXT, 
          away_team TEXT, 
          away_acronym TEXT, 
          away_score TEXT)
    """)

def get_data():
    logging.get_start_info(__name__)
    record_count = 0

    try:
        uri = f'https://api.football-data.org/v4/teams/{liverpool_id}/matches'
        headers = { 'X-Auth-Token': os.getenv("FOOTBALL_TOKEN") }

        response = requests.get(uri, headers=headers).json()
        matches = response['matches']

        # If matches found, clear existing table
        if bool(matches):
            _c.execute("""
            DELETE FROM Liverpool_Matches
            """)

        #  Iterate through each match to find the next one's index
        for match_index in range(len(matches)):
            match_date = datetime.datetime.fromisoformat(matches[match_index]['utcDate'][:-1])
            print(match_date)
            if match_date >= datetime.datetime.now():
                next_match_index = match_index
                break

        # Reduce matches to only the last 3 games (if there have been 3 or more games) and the next
        if next_match_index < 3:
            matches = matches[0:]
        else:
            matches = matches[next_match_index - 3:]

        
        _c.execute("""
            DELETE FROM Liverpool_Matches
            """)
        
        for match in matches:
            match_detail = {
                "match_competition" : match['competition']['code'],
                "match_stage": match['stage'].replace("_"," ").title(),
                "match_date" : datetime.datetime.strptime((match['utcDate'][:10]), '%Y-%m-%d').date().strftime('%a %d %b'),
                "match_time": match['utcDate'][11:16],
                "home_team" : match['homeTeam']['name'],
                "home_acronym" : match['homeTeam']['tla'],
                "home_score" : match['score']['fullTime']['home'],
                "away_team" : match['awayTeam']['name'],
                "away_acronym" : match['awayTeam']['tla'],
                "away_score" : match['score']['fullTime']['away']
            }

            record_count = record_count + 1

            _c.execute("""
                INSERT INTO Liverpool_Matches (
                    match_competition,
                    match_stage, 
                    match_date, 
                    match_time, 
                    home_team, 
                    home_acronym, 
                    home_score, 
                    away_team, 
                    away_acronym, 
                    away_score)
                VALUES(
                    :match_competition, 
                    :match_stage, 
                    :match_date, 
                    :match_time, 
                    :home_team, 
                    :home_acronym, 
                    :home_score, 
                    :away_team, 
                    :away_acronym, 
                    :away_score)    
            """,match_detail)

        _db.commit()
        _db.close()

        logging.get_finish_info(record_count)
        logging.write_log()

    except Exception as e:
        logging.get_error_message(e.args[0])
        logging.write_log()
        _db.commit()
        _db.close()