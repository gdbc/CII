#!/usr/bin/python

import sys
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
URL="http://" + SERVER + "/api/v2/hostgroups"
USER="admin"
PASS="admin"
ENV="7_dev"
#DST_ENV=sys.argv[2]

get_hg=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

for i in get_hg['results']:
   for x in i.keys():
      print "%s: %s" %(x, i[x])
   print ""
