#!/usr/bin/python

import requests
import json
import logging
import time
from pprint import pprint


# 1. Define inputs for the POST/GET request
# Example: https://ian.test.instructure.com/api/v1/accounts/'
base_url = 'https://unco.test.instructure.com/api/v1/accounts/self/'
header = {'Authorization': 'Bearer 7227~8qA5twNyOirR9ePFsPQ3cal7ZVlK5SghvznnS8onnRYG3eUHmYaqr84NzzPNToIe'}

# Parameters specific to the initial POST request
# Example: 'SIS_Testing/users.csv'
myfile = 'inst_role_export.csv'
payload = {'import_type': 'instructure_csv', 'extension': 'csv'}
data = open(myfile, 'rb').read()

# If you're checking the status of an import, include the sis_import_id here in quotes.
# For submitting an import leave at None.
#import_id = None
import_id = '9'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

timestr = time.strftime("%H:%M:%S-%Y%m%d")
logfile_name = timestr + ".log"
#print(logfile_name)
handler = logging.FileHandler(logfile_name)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Begin Logging")

# 2. Create a response object from the POST request
def myrequest(base_url, header, payload, data):
    if not import_id:
        print("Sending file: ", myfile)
        logger.info('Sending file: %s', myfile)
        r = requests.post(base_url + "/sis_imports/", headers=header, params=payload, data=data)
    else:
        print("Import ID: ", import_id)
        logger.info('Checking on the status of import %s', import_id)
        r = requests.get(base_url + "/sis_imports/" + import_id, headers=header)
    return r


# 3. Pull JSON content from the response into a new JSON object
# 4. Place key elements into a dictionary for later reference
def parsejson(r):
    rjson = json.loads(r.text)
    return rjson


# 0. Main method
def main():
    # Create a response object from the POST/GET request
    r = myrequest(base_url, header, payload, data)
    # Parse JSON response
    rjson = parsejson(r)
    # Print JSON response
    print("Printing rjson response")
    pprint(rjson)
    print rjson.get("workflow_state", "none")
    for x in rjson.get("processing_warnings", "none"):
        logger.warning(x)
        print(x)
    logger.info('End Logging')

if __name__ == "__main__":
    main()
