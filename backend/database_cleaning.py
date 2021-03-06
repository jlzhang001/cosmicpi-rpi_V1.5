'''
This program will clean the sqlite database every now and then to keep it from exploding.

'''


import time
import sqlite3
import configparser
import random

import logging as log
log.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=log.INFO)


def _initilize_DB(_sqlite_location):
    _db_conn = sqlite3.connect(_sqlite_location, timeout=60.0)
    cursor = _db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Events'")
    if cursor.fetchone() == None:
        cursor.execute('''CREATE TABLE Events
         (UTCUnixTime INTEGER, SubSeconds REAL, TemperatureC REAL, Humidity REAL, AccelX REAL,
          AccelY REAL, AccelZ REAL, MagX REAL, MagY REAL, MagZ REAL, Pressure REAL, Longitude REAL,
          Latitude REAL, DetectorName TEXT, DetectorVersion TEXT);''')
        _db_conn.commit()


# settings files
CONFIG_FILE = "../config/CosmicPi.config"

# read configuration
# Todo: Put the config parser into a propper class
# Todo: Implement proper error catching for configparser (e.g. non existent keys or file)
# read configuration
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
sqlite_location = config.get("Storage", "sqlite_location")
max_event_age = config.getint("Storage", "sqlite_max_event_age") * 60. * 60.    # here used in seconds

# setup the program
_initilize_DB(sqlite_location)

# start the cleaning loop
while(True):
    # establish a connection
    db_conn = sqlite3.connect(sqlite_location, timeout=60.0)
    cursor = db_conn.cursor()

    # delete old events
    # get the most recent time
    cursor.execute("SELECT * FROM Events ORDER BY UTCUnixTime DESC, SubSeconds DESC;")
    latest_time = cursor.fetchone()[0]
    limit_time = int(latest_time - max_event_age)

    log.info("Deleting entries older than: {} [s]".format(limit_time))
    # delete old entries and close the connection
    cursor.execute("DELETE FROM Events WHERE UTCUnixTime < ?;", (limit_time,))
    db_conn.commit()
    db_conn.close()

    # sleep for a semi random time
    time_to_wait = int(random.randrange(5*60, 10*60))
    log.info("Sleeping for: {} [s]".format(time_to_wait))
    time.sleep(time_to_wait)
