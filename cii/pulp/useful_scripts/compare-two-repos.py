#!/usr/bin/python

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()

SERVER  = "cii-pulp.ci.com"
URL     = "https://" + SERVER + "/pulp/api/v2/repositories/"
USER    = "admin"
PASS    = "admin"
SRC_ENV = sys.argv[1]
DST_ENV = sys.argv[2]
repos   = requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

# Get repo packages sorted out 

def get_repos(src_env, dst_env, repositories):
   src_dict=[]
   dst_dict=[]
   for repo in repositories:
      if src_env in repo['id']:
         src_dict.append(repo['id'])
      elif dst_env in repo['id']:
         dst_dict.append(repo['id'])
   return src_dict,dst_dict

def get_env_rpms(repos_array):
   ARR = []
   for repo in repos_array:
      URL = "https://" + SERVER + "/pulp/api/v2/repositories/" + repo + "/search/units/"
      DST = {"criteria": {"fields": {"unit": ["filename"]},"type_ids": ["rpm"]}}
      REQ = requests.post(URL,auth=HTTPBasicAuth(USER, PASS),data=json.dumps(DST),verify=False).json()
      for rpm in REQ:
      # Change filename to name to get just the rpm name
         ARR.append(rpm["metadata"]["filename"])
   return ARR

def get_diff_rpms(src_rpms, dst_rpms):
   #diff_rpms = [x for x in src_rpms if x not in dst_rpms] 
   diff_rpms = []
   for x in src_rpms:
      if x not in dst_rpms:
         diff_rpms.append(x)
   return "\n".join(diff_rpms)

SRC_DICT, DST_DICT = get_repos(SRC_ENV,DST_ENV,repos) 
src_rpms_all = get_env_rpms(SRC_DICT)
dst_rpms_all = get_env_rpms(DST_DICT)
print get_diff_rpms(src_rpms_all,dst_rpms_all)
