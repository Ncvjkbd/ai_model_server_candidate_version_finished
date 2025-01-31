""" This module combines various logging methods into one class."""
import os
import logging
from logging.handlers import RotatingFileHandler

class Logger():
    """ Combination logger class"""
    def __init__(self, logger_name:str, log_file:str) -> None:
        # Create a logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)  # Set the root logger level

        # Check if folder exists
        if not os.path.exists(os.path.dirname(log_file)):
            os.mkdir(os.path.dirname(log_file))

        # Create a file handler
        file_handler = RotatingFileHandler(log_file,
                                           maxBytes=2_048_000,
                                            backupCount=5)
        file_handler.setLevel(logging.DEBUG)  # Set the file handler level

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Set the console handler level

        # Create a formatter and add it to the handlers
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s:-> %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def close(self):
        """ Releases all file handles"""
        logging.shutdown()
