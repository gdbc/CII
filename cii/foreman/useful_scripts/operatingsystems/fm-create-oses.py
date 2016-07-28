#!/usr/bin/python
#Usage: ./fm-create-oses.py cent-7_uat 
#NB: Media url base-<argv[1] needs to be created, Templates need to be created as well
#Default arch and part tables are hard-wired from SOURCE_OS

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

USER            = "admin"
PASS            = "admin"
SERVER          = "cii-foreman.ci.com"
HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
URL             = "https://" + SERVER + "/api/v2/operatingsystems"
OS              = sys.argv[1]
OS_NAME         = OS
OS_MAJOR        = int(OS.split('_')[0].split('-')[1])
OS_FAMILY       = "Redhat"
ENV             = OS.split('-')[1]
SOURCE_OS       = "cent-7_dev"


def get_media_id(SERVER, ENV):
    media_name = "base-" + ENV
    URL="https://" + SERVER + "/api/v2/media"
    get_media=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
    for i in get_media['results']:
        if media_name in i['name']:
           return i['id']

def get_details_from_source():
   URL="http://" + SERVER + "/api/v2/operatingsystems"
   get_os=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
   prov_ids      = []
   if SOURCE_OS == get_os['results'][0]['name']:
       OS_ID     = get_os['results'][0]['id']
       URL       = "http://" + SERVER + "/api/v2/operatingsystems/" + str(OS_ID)
       get_os    = requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
       PTABLE_ID = get_os['ptables'][0]['id']
       ARCH_ID   =  get_os['architectures'][0]['id']
       for i in get_os['os_default_templates']:
           prov_ids.append(i['provisioning_template_id'])

       return PTABLE_ID, ARCH_ID, prov_ids

   else: 
       print "No SOURCE OS FOUND, please create or change SOURCE_OS variable" 



ptableID,archID,provIDs = get_details_from_source()
mId = get_media_id(SERVER, ENV)

operatingsystem = {"operatingsystem":{'name':OS_NAME,'major':OS_MAJOR,'family':OS_FAMILY,'medium_ids':[mId], 'architecture_ids':[archID],'ptable_ids':[ptableID],'provisioning_template_ids':provIDs}}
create_os       = requests.post(URL,auth=(USER, PASS),data=json.dumps(operatingsystem),headers=HEADERS,verify=False).json()
