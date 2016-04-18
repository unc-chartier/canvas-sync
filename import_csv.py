#!/usr/bin/python

import requests
import json
import logging
import logging.config
import os
import time
import shutil
import ConfigParser
from pprint import pprint


# 1. Define inputs for the POST/GET request
# Example: https://ian.test.instructure.com/api/v1/accounts/'
connection_url = 'https://unco.test.instructure.com/api/v1/accounts/self/'
config = ConfigParser.ConfigParser()
config.read("token.txt")
token_test = config.get("token_file", "token_test")
token = ('Bearer %s' % token_test)
transfer_header = {'Authorization': token}
# Parameters specific to the initial POST request
mypath = 'CSV_extracts/'
file_name = 'chartier_extract_test.csv'
myfile = mypath + file_name
api_payload = {'import_type': 'instructure_csv', 'extension': 'csv'}
api_data = open(myfile, 'rb').read()


# setup logging to create two file handlers from data in logging.json
def setup_logging(
    default_path = 'logging.json',
    default_level = logging.INFO,
    env_key = 'LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


# 2. Create a response object from the POST request
def myrequest(base_url, header, payload, data):
        logging.debug("base_url: %s" % connection_url)
        logging.debug(transfer_header)
        logging.debug(payload)
        logging.debug(data)
        logging.info("Importing %s to %s" % (myfile, connection_url))
        r = requests.post(base_url + "/sis_imports/", headers=header, params=payload, data=data)
        return r


def request_status(header, import_id):
        logging.debug(import_id)
        logging.debug(header)
        logging.info("Checking on import number: %s" % import_id)
        location_url = connection_url + "/sis_imports/%s" % import_id
        logging.info(location_url)
        r = requests.get(location_url, headers=header)
        return r


# 3. Pull JSON content from the response into a new JSON object
# 4. Place key elements into a dictionary for later reference
def parsejson(r):
    rjson = json.loads(r.text)
    return rjson


# 5. Run the code
def main():
    setup_logging()
    # Create a response object from the POST/GET request
    r = myrequest(connection_url, transfer_header, api_payload, api_data)
    # Parse JSON response
    rjson = parsejson(r)
    # Pretty Print JSON response
    pprint(rjson)
    # Set the var to loop to check the status of the file
    ended = rjson['ended_at']
    logging.debug(ended)
    logging.info("Wait three minutes and check the status of the import.")
    time.sleep(180)
    while ended is None:
        # Set the var for checking the status of the last import
        import_id = rjson['id']
        # Create a response object from the POST/GET request
        r2 = request_status(transfer_header, import_id)
        # Parse JSON response
        r2json = parsejson(r2)
        # Pretty Print JSON response
        pprint(r2json)
        # Set var to display the import progress
        percent_done = r2json['progress']
        # Reset var ended to know when to end the loop.
        ended = r2json['ended_at']
        if ended is None:
            logging.info("Wait five minutes and check import status again. %s percent done." % percent_done)
            time.sleep(300)
        else:
            try:
                # log the warning messages that are returned.
                logging.error("Importing %s to %s" % (myfile, connection_url))
                for v in r2json['processing_warnings']:
                    logging.error(v)
            except:  # when importing there will be no processing warnings
                logging.debug("No processing warnings returned")
            try:
                # logging processing errors that are returned.
                for v in r2json['processing_errors']:
                    logging.error(v)
            except:
                logging.debug("No processing errors returned.")
            logging.debug(myfile)
            logging.info("File uploaded at %s " % ended)
            destination_loc = 'CSV_extracts/archive/'
            file_date = time.strftime("%m_%d_%Y-%H:%M:%S")
            logging.info("Moving %s to %s and adding a timestamp: %s" % (file_name, destination_loc, file_date))
            if mypath is None:
                shutil.move(file_name + destination_loc + file_date + file_name)
            else:
                shutil.move(mypath + file_name, destination_loc + file_date + file_name)
            pass


if __name__ == "__main__":
    main()
