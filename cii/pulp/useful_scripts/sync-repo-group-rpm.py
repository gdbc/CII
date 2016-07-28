#!/usr/bin/python
# This script assumes you have a pulp feed configured and syncs repositories in a repo group
# and waits for the sync to complete
# Sometimes the other sync doesn't work, need to dig into that, problem with this is it syncs rpms, not errata
import sys
import json
import time
import requests
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()

SRC_ENV    = "master"
DST_ENV    = "eng"
SERVER     = "cii-pulp.ci.com"
URL        = "https://" + SERVER + "/pulp/api/v2/repo_groups/" + DST_ENV + "/"
USER       = "admin"
PASS       = "admin"
TASK_ARRAY = []
SYNCED     = True
SLEEP      = 5
TIMEOUT    = 300
TOTALTIME  = 0


# Get list of repos to compare unit counts

REPO_URL = "https://" + SERVER + "/pulp/api/v2/repositories/"
REPOS    = requests.get(REPO_URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

def checkRepoDiff(srcReps, dstReps, reps):
    src_count = 0
    dst_count = 0
    for rep in reps:
        if str(srcReps).strip() == str(rep['id']).strip():
            src_count = rep['content_unit_counts']['rpm']
        if str(dstReps).strip() == str(rep['id']).strip():
            dst_count = rep['content_unit_counts']['rpm']
    if src_count < dst_count:
        return True
    else:
        return False

def checkTask(tId):
    SRV="https://ci-pulp.example.com/pulp/api/v2/tasks/" + tId + "/"
    tIdCheck=requests.get(SRV,auth=HTTPBasicAuth(USER, PASS),verify=False)
    state = json.loads(tIdCheck.text)
    if state['state'] == "finished":
       return True
    else:
       return False

REPO_GROUPS = requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

for repo in REPO_GROUPS['repo_ids']:
    if checkRepoDiff(repo,repo.replace(DST_ENV, SRC_ENV), REPOS):
        req  = {"source_repo_id": repo.replace(DST_ENV, SRC_ENV), 'criteria':  {"type_ids": ['rpm']},"override_config": {"verify_checksum": False,"verify_size": False}}
        url  = "https://ci-pulp.example.com/pulp/api/v2/repositories/" + str(repo).strip() + "/actions/associate/"
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
          print "Task %s sleeping for %s" %(task, SLEEP)
          TOTALTIME = TOTALTIME + SLEEP
          time.sleep(SLEEP)
          continue
       else:
          print "task %s completed" %task
          break
       if TOTALTIME == TIMEOUT:
          print "Sync is taking too long, failing"
          sys.exit(-1)
