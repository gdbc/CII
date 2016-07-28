#!/usr/bin/python

import sys
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
URL="http://" + SERVER + "/api/v2/media?per_page=10000"
USER="admin"
PASS="admin"
ENV=sys.argv[1]

get_media=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
#print get_media 
for i in get_media['results']:
    if ENV in i['name']:
       print "Name: %-30s Id: %-3s Path: %-50s" %(i['name'],i['id'],i['path'])
