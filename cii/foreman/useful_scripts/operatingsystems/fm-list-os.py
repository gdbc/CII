#!/usr/bin/python

import sys
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
USER="admin"
PASS="admin"
OSID = sys.argv[1]
URL="http://" + SERVER + "/api/v2/operatingsystems/" + OSID

get_os=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

for i in get_os:
       print "%s: %s" %(i, get_os[i])
       
print get_os['ptables'][0]['id']
print get_os['architectures'][0]['id']
