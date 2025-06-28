import logging

def setup_logger():
    logging.basicConfig(filename='logs/app.log', level=logging.INFO)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
