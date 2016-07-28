#!/usr/bin/python

import sys
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
URL="http://" + SERVER + "/api/v2/operatingsystems"
USER="admin"
PASS="admin"

get_os=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

for i in get_os['results']:
      for x in i:
         print "%s: %s" %(x, i[x])
      print ""
