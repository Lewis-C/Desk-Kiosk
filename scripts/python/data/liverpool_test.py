# Imports
import requests
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv('/usr/files/scripts/python/.credentials/.env') 
liverpool_id = 64 
prem_id = 2021

uri = f'https://api.football-data.org/v4/teams/{liverpool_id}'
headers = { 'X-Auth-Token': os.getenv("FOOTBALL_TOKEN") }
response = requests.get(uri, headers=headers).json()



uri = f'https://api.football-data.org/v4/competitions/{prem_id}/standings'
headers = { 'X-Auth-Token': os.getenv("FOOTBALL_TOKEN") }
response = requests.get(uri, headers=headers).json()



competition_name = response['competition']['name']
competition_type = response['competition']['type'].title()
competition_stage = response['standings'][0]['stage'].replace("_"," ").title()
competition_group = response['standings'][0]['group']

liverpool_index = 0

for index,team in enumerate(response['standings'][0]['table']):
    if team['team']['id'] == liverpool_id:
        liverpool_index = index
        break

if liverpool_index == 0:
        range_start = 0
        range_end = 3
else:
        range_start = liverpool_index - 1
        range_end = liverpool_index + 2

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

    print(competition_details)