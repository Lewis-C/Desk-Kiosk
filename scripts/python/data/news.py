
# Imports
import sqlite3
import feedparser
from datetime import datetime
# Local Imports
from data.utilities import logging

_db = sqlite3.connect('/usr/files/server/database.db')
_c = _db.cursor()

_c.execute("""
    CREATE TABLE IF NOT EXISTS News(
           location TEXT,
           date TEXT,
           title TEXT
           )
    """)

def get_data():
    logging.get_start_info(__name__)
    record_count = 0

    try:
        # Calls function for each location that news should be retrieved
        _get_entries("UK",'https://feeds.bbci.co.uk/news/uk/rss.xml',record_count)
        _get_entries("World",'https://feeds.bbci.co.uk/news/world/rss.xml',record_count)

        _db.commit()
        _db.close()
        logging.get_finish_info(record_count)
        logging.write_log()
    
    except Exception as e:
        logging.get_error_message(e.args[0])
        logging.write_log()
        _db.commit()
        _db.close()



def _get_entries(location,rss_url,record_count):
    # Function to parse the RSS feed, iterate through and store each entry data in table
    feed = feedparser.parse(rss_url)

    # If the feed returns correctly, remove the existing data
    if bool(feed.entries):
        _c.execute(f"""
        DELETE FROM News WHERE LOCATION = '{location}'
        """)
    
    for entry in feed.entries[0:10]:
        date = entry.published[5:16]
        date = datetime.strptime(date, '%d %b %Y')

        news_entry = {
            'location' : location,
            'date' : date,
            'title' : entry.title
        }

        record_count = record_count + 1

        _c.execute("""
                INSERT INTO News (
                    location,
                    date,
                    title)
                VALUES(
                    :location,
                    :date,
                    :title)    
            """,news_entry)
    

