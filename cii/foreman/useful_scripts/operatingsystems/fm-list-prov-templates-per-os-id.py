#!/usr/bin/python

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
USER="admin"
PASS="admin"
ID=sys.argv[1]
URL="http://" + SERVER + "/api/v2/operatingsystems/" + ID + "/provisioning_templates?per_page=10000"

get_tmps=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

for i in get_tmps['results']:
      for x in i:
         print "%s: %s" %(x, i[x])
