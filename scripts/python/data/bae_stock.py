import yfinance
# Imports
import sqlite3
# Local Imports
from data.utilities import logging

_db = sqlite3.connect('/usr/files/server/database.db')
_c = _db.cursor()

_c.execute("""
    CREATE TABLE IF NOT EXISTS BAE_Stock(
           last_price TEXT,
           last_close TEXT,
           variance TEXT,
           variance_percentage TEXT
            )
    """)

def get_data():
    logging.get_start_info(__name__)
    record_count = 0

    try:
        dat = yfinance.Ticker("BA.L")

        # If data is returned, empty the existing table
        if bool(dat):
            _c.execute("""
            DELETE FROM BAE_Stock
            """)

        last_price = (dat.fast_info['lastPrice'])
        last_close = (dat.fast_info['previousClose'])
        variance = round(last_price - last_close,2)
        variance_percentage = round(last_price / last_close,2)

        stock_details = {
            "last_price" :last_price,
            "last_close" :last_close,
            "variance" :variance,
            "variance_percentage" :variance_percentage
        }

        record_count = record_count + 1

        _c.execute("""
            INSERT INTO BAE_Stock (
                last_price,
                last_close,
                variance,
                variance_percentage)
            VALUES(
                :last_price,
                :last_close,
                :variance,
                :variance_percentage)    
        """,stock_details)
        
        _db.commit()
        _db.close()
        logging.get_finish_info(record_count)
        logging.write_log()

    except Exception as e:
        logging.get_error_message(e.args[0])
        logging.write_log()
        _db.commit()
        _db.close()