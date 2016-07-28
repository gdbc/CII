#!/usr/bin/python

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
#URL="http://" + SERVER + "/api/v2/provisioning_templates"
URL="http://" + SERVER + "/api/v2/config_templates"
USER="admin"
PASS="admin"

get_tmps=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

for i in get_tmps['results']:
      for x in i:
         print "%s: %s" %(x, i[x])
