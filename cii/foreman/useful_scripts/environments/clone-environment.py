#!/usr/bin/python
#usage: ./script NEW_ENV
#NB: Make sure modules are in /etc/puppet/modules, thats where they are imported from

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

SERVER="cii-foreman.ci.com"
URL="http://" + SERVER + "/api/v2/smart_proxies"
USER="admin"
PASS="admin"
ENV_NAME = sys.argv[1]


def get_org_id():
    URL="http://" + SERVER + "/api/v2/organizations"
    get_orgs=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False)
    return get_orgs
    for i in get_orgs:
      print i
      print get_orgs['results']['id']

def get_proxy_id(SERVER):
    URL="http://" + SERVER + "/api/v2/smart_proxies"
    get_envs=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
    for i in get_envs['results']:
        if SERVER == i['name']:
            return i['id']
        else:
            return "fail"

def create_new_env(dst_env_name):
    URL="http://" + SERVER + "/api/environments"
    ENV={'environment':{'name':dst_env_name}}
    HEADERS={"Accept": "application/json","Content-Type":"application/json"}
    create_env=requests.post(URL,auth=HTTPBasicAuth(USER, PASS), data=json.dumps(ENV), headers=HEADERS,verify=False).json()
    return create_env
    
def get_env_id(env_name):
    URL="http://" + SERVER + "/api/v2/environments"
    get_envs=requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
    for i in get_envs['results']:
        if i['name'] == env_name:
            return i['id']

def import_env(dst_id, src_smt_id):
    URL="http://" + SERVER + "/api/environments/" + str(dst_id) + "/smart_proxies/" + str(src_smt_id) + "/import_puppetclasses"
    PARAMS = {'id'            : str(dst_id)}
    HEADERS={"Accept": "application/json","Content-Type":"application/json"}
    import_classes=requests.post(URL,auth=HTTPBasicAuth(USER, PASS),data=json.dumps(PARAMS),headers=HEADERS,verify=False).json()
    if "Success" in import_classes['message']:
       return "Pass"

PRX_ID  = get_proxy_id(SERVER)
if PRX_ID != "fail":
    NEW_ENV = create_new_env(ENV_NAME)
    NEW_ID  = get_env_id(ENV_NAME)
    IMPORT_ENV = import_env(NEW_ID, PRX_ID)
    if IMPORT_ENV == "Pass":
        print "All modules synced to",ENV_NAME
