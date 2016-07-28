#!/usr/bin/python

import sys
import requests
from requests.auth import HTTPBasicAuth

SERVER="ci-foreman.ci.com"
USER="admin"
PASS="admin"
OS_NAME = sys.argv[1]


def get_os_id(USER, PASS, SERVER, OS_NAME):
    OS_ID  = ""
    URL    = "http://" + SERVER + "/api/v2/operatingsystems"
    get_os = requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
    for results in get_os['results']:
        if OS_NAME == results['name']:
            return results['id']

OSID = get_os_id(USER, PASS, SERVER, OS_NAME)
print "OS ID is: ",OSID

