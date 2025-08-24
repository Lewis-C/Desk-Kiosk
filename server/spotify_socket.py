# Imports
from dotenv import load_dotenv 
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys

# Initialise Environment
load_dotenv('/usr/files/server/.credentials/.env') 
scope = "user-read-currently-playing" # Scope string to define user permissions
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,open_browser=False,cache_path='/usr/files/server/.credentials/.cache')) # Authentcates API access using environment variables and scope (environment variables must follow spotipy naming)
user_id = (sp.current_user()['id']) # Variable to get user id, used later to ensure playlists are defined by current user


def get_currently_playing():
    # Function to retrieve current playlist. 
    # Sleeps 3 seconds to avoid overpolling API
    time.sleep(3)
    track = sp.currently_playing()
    track_details = {
        "track_name": None,
        "track_artist": None,
        "track_album": None,
        "track_album_art" : None
    }

    if (track is not None):
        if (track['currently_playing_type'] == "track"):
            track_details = {
                "track_name": track['item']['name'],
                "track_artist": track['item']['artists'][0]['name'],
                "track_album": track['item']['album']['name'],
                "track_album_art" : track['item']['album']['images'][0]['url']
            }
    
    return track_details
