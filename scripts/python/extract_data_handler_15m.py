# Imports
# Local Imports
from data import weather_hourly, weather_daily, events, news
from data.utilities import logging


if __name__ == "__main__":
        
        logging.init_logging_table()
        
        news.get_data()
        weather_hourly.get_data()
        weather_daily.get_data()
        events.get_data()