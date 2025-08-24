# Local Imports
from data import warton_flight, liverpool_matches, liverpool_status, bae_stock
from data.utilities import logging


if __name__ == "__main__":
        
        logging.init_logging_table()
        
        liverpool_matches.get_data()
        liverpool_status.get_data()
        bae_stock.get_data()
        warton_flight.get_data()
