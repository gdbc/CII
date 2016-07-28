#!/usr/bin/python
# This script assumes you have a pulp feed configured and syncs repositories in a repo group
# and waits for the sync to complete
# Only variable to change here is DST_ENV as a feed should be setup so it knows where to get its packages
import sys
import json
import time
import requests
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()

DST_ENV    = "7_master"
SERVER     = "https://cii-pulp.ci.com/pulp/api/v2/repo_groups/" + DST_ENV + "/"
USER       = "admin"
PASS       = "admin"
TASK_ARRAY = []
req        = {"override_config": {"verify_checksum": False,"verify_size": False}}
SYNCED     = True
SLEEP      = 15
TIMEOUT    = 600
TOTALTIME  = 0

def checkTask(tId):
    SRV="https://ci-pulp.example.com/pulp/api/v2/tasks/" + tId + "/"
    tIdCheck=requests.get(SRV,auth=HTTPBasicAuth(USER, PASS),verify=False)
    state = json.loads(tIdCheck.text)
    if state['state'] == "finished":
       return True
    else:
       return False

repos=requests.get(SERVER,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
for repo in repos['repo_ids']:
    print repo
    url  = "https://ci-pulp.example.com/pulp/api/v2/repositories/" + str(repo).strip() + "/actions/sync/"
    sync = requests.post(url,auth=HTTPBasicAuth(USER, PASS),data=json.dumps(req),verify=False)
    # might want to add a collective check against status code == 202
    # AND a wait until sync is complete ie: a wait module? 
    print sync.text
    print sync.status_code
    if str(sync.status_code).strip() == "202":
        TASK_ARRAY.append(json.loads(sync.text)['spawned_tasks'][0]['task_id'])
    else:
        print "sync failure code on repo: %s" %repo
        sys.exit(1)

for task in TASK_ARRAY:
    while SYNCED:
       if not checkTask(task):
          print "sleeping for",SLEEP
          time.sleep(SLEEP)
          continue
       else:
          print "task %s completed" %task
          break
    if TOTALTIME == TIMEOUT:
        print "Sync is taking too long, failing"
        sys.exit(-1)
    TOTALTIME = TOTALTIME + SLEEP
