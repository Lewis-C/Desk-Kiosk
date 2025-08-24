# Imports
import requests
from dotenv import load_dotenv
import sqlite3
import os
# Local Imports
from data.utilities import logging

load_dotenv('/usr/files/scripts/python/.credentials/.env') 
liverpool_id = 64 
prem_id = 2021

_db = sqlite3.connect('/usr/files/server/database.db')
_c = _db.cursor()

_c.execute("""
    CREATE TABLE IF NOT EXISTS Liverpool_Status(
           competition_name TEXT,
           competition_type TEXT,
           competition_stage TEXT,
           competition_group TEXT,
           team_name TEXT,
           position TEXT,
           games_played TEXT,
           games_won TEXT,
           games_drawn TEXT,
           games_lost TEXT,
           points TEXT,
           goals_scored TEXT,
           goals_conceded TEXT,
           goal_difference TEXT )
    """)

def get_data():
    logging.get_start_info(__name__)
    record_count = 0

    try:
        # Get the full standings data of the entire premier league
        uri = f'https://api.football-data.org/v4/competitions/{prem_id}/standings'
        headers = { 'X-Auth-Token': os.getenv("FOOTBALL_TOKEN") }
        response = requests.get(uri, headers=headers).json()

        # If valid response is given, clear the existing table
        if bool(response):
            _c.execute("""
                DELETE FROM Liverpool_Status
                """)

        # Store base competition details
        competition_name = response['competition']['name']
        competition_type = response['competition']['type'].title()
        competition_stage = response['standings'][0]['stage'].replace("_"," ").title()
        competition_group = response['standings'][0]['group']

        liverpool_index = 0

        # Iterate through each team and if they match liverpool id, store the index
        for index,team in enumerate(response['standings'][0]['table']):
            if team['team']['id'] == liverpool_id:
                liverpool_index = index
                break

        # Create a span of liverpool and the two surrounding teams (second 2 if the liverpool are top) (span exceeds by one for use with range)
        if liverpool_index == 0:
             range_start = 0
             range_end = 3
        else:
             range_start = liverpool_index - 1
             range_end = liverpool_index + 2

        # Return the details of each team within the aformentioned span, then build a dict for each team and store in table
        for team in response['standings'][0]['table'][range_start:range_end]:
            team_position = team['position']
            team_name = team['team']['name']
            team_games_played = team['playedGames']
            team_games_won = team['won']
            team_games_drawn = team['draw']
            team_games_lost = team['lost']
            team_points = team['points']
            team_goals_scored = team['goalsFor']
            team_goals_conceded = team['goalsAgainst']
            team_goal_difference = team['goalDifference']
        
            competition_details = {
                'competition_name' : competition_name,
                'competition_type' : competition_type,
                'competition_stage' : competition_stage,
                'competition_group' : competition_group,
                'position' : team_position,
                'team_name' : team_name,
                'games_played' : team_games_played,
                'games_won' : team_games_won,
                'games_drawn' : team_games_drawn,
                'games_lost' : team_games_lost,
                'points' : team_points,
                'goals_scored' : team_goals_scored ,
                'goals_conceded' : team_goals_conceded ,
                'goal_difference' : team_goal_difference
            }

            record_count = record_count + 1

            _c.execute("""
                INSERT INTO Liverpool_Status (
                    competition_name,
                    competition_type,
                    competition_stage,
                    competition_group,
                    position,
                    team_name,
                    games_played,
                    games_won,
                    games_drawn,
                    games_lost,
                    points,
                    goals_scored,
                    goals_conceded,
                    goal_difference)
                VALUES(
                    :competition_name,
                    :competition_type,
                    :competition_stage,
                    :competition_group,
                    :position,
                    :team_name,
                    :games_played,
                    :games_won,
                    :games_drawn,
                    :games_lost,
                    :points,
                    :goals_scored,
                    :goals_conceded,
                    :goal_difference)    
            """,competition_details)


        _db.commit()
        _db.close()
        logging.get_finish_info(record_count)
        logging.write_log()

    except Exception as e:
        logging.get_error_message(e.args[0])
        logging.write_log()
        _db.commit()
        _db.close()