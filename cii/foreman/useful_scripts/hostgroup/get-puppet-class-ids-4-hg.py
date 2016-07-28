#!/usr/bin/python
#Usage: ./get-puppet-class-ids-4-hg.py hg-7_dev

import sys
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
URL="http://" + SERVER + "/api/v2/hostgroups"
USER="admin"
PASS="admin"
HG=sys.argv[1]

def get_hg_id(SERVER,HG):
    URL="http://" + SERVER + "/api/v2/hostgroups"
    get_hg=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
    for i in get_hg['results']:
        if i['title'] == HG:
            return i['id']


def get_hg_classes(SERVER,HG_ID):
    URL="http://" + SERVER + "/api/v2/hostgroups/" + str(HG_ID) + "/puppetclass_ids"
    get_classes=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
    return get_classes['results']


getId          = get_hg_id(SERVER, HG)
getClasses     = get_hg_classes(SERVER,getId)
print getClasses
for x in getClasses:
   print x

