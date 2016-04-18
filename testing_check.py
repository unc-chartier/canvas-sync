import requests
import json
import time
import ConfigParser
from pprint import pprint


config = ConfigParser.ConfigParser()
config.read("token.txt")
token_test = config.get("token_file", "token_test")
token = ('Bearer %s' % token_test)
base_url = 'https://unco.test.instructure.com/api/v1/accounts/self/'
header = {'Authorization': token}


def request_status(header, import_id):
        location_url = base_url + "/sis_imports/%s" %import_id
        print(location_url)
        r2 = requests.get(location_url, headers=header)
        return r2


def parsejson(r):
    rjson = json.loads(r.text)
    return rjson

ended = None


while ended is None:
    import_id = 11
    r2 = request_status(header, import_id)
    r2json = parsejson(r2)
    pprint(r2json)
    percent_done = r2json['progress']
    # errors = r2json['processing_errors']
    ended = r2json['ended_at']
    if ended is None:
        print("Wait two minutes and try again. %s percent done." % percent_done)
        time.sleep(120)
    else:
        print("File uploded at %s" % ended)
        try:
            for v in r2json['processing_errors']:
                print(v)
        except:
            print("No processing errors.")