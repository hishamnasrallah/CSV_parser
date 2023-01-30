"""
setup logging
"""
from os import path
import logging.config

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')

logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
