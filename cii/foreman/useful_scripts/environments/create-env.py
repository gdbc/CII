#!/usr/bin/python
#usage: ./script SRC_ENV_ID SRC_PRX_ID DST_ENV_NAME

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
USER="admin"
PASS="admin"


URL="https://" + SERVER + "/api/v2/environments"
environment={"environment":{"name":"farter"}}
HEADERS = {"Accept": "application/json","Content-Type":"application/json"}

create_env=requests.post(URL,auth=HTTPBasicAuth(USER, PASS), data=json.dumps(environment), headers=HEADERS,verify=False).json()


print create_env

