#!/usr/bin/python

import sys
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
URL="http://" + SERVER + "/api/v2/environments"
USER="admin"
PASS="admin"

get_envs=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

for i in get_envs['results']:
   print "%-20s id: %s" %(i['name'], i['id'])

