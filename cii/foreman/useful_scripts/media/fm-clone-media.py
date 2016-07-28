#!/usr/bin/python
#./fm-clone-media.py 7_dev 7_uat

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
URL="https://" + SERVER + "/api/media"
USER="admin"
PASS="admin"
OS = "Redhat"

SRC_ENV=sys.argv[1]
DST_ENV=sys.argv[2]

HEADERS = {"Accept": "application/json","Content-Type":"application/json"}

get_media=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
for i in get_media['results']:
    if SRC_ENV in i['name']:
       NAME   = i['name'].replace(SRC_ENV,DST_ENV).strip()
       PATH   = i['path'].replace(SRC_ENV,DST_ENV).strip()
       print "%s, %s" %(NAME,PATH)
       PARAMS = {'medium':{'name':NAME,'path':PATH,'os_family':OS}}
       #PARAMS = {'medium':{'name':NAME,'path':PATH}}
       create_media = requests.post(URL,auth=HTTPBasicAuth(USER, PASS),data=json.dumps(PARAMS),headers=HEADERS,verify=False)
       print create_media.text
