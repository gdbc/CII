#!/usr/bin/python

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()

SERVER             = "cii-pulp.ci.com"
URL                = "https://" + SERVER + "/pulp/api/v2/repositories/"
USER               = "admin"
PASS               = "admin"
REPOS              = requests.get(URL,auth=HTTPBasicAuth(USER, PASS),verify=False).json()
SRC_ENV            = "7_master"
DST_ENV            = "7_dev"
TOKEN              = "cii-run"
JOB_NAME           = "cii-run"
JENKINS_SERVER_URI = "http://cii-jenkins.ci.com:8080/job/cii-run/buildWithParameters?token=" + TOKEN

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


def get_env_rpms_dict(repos_array):
   ARR   = {}
   for repo in repos_array:
      URL = "https://" + SERVER + "/pulp/api/v2/repositories/" + repo + "/search/units/"
      DST = {"criteria": {"fields": {"unit": ["name","filename"]},"type_ids": ["rpm"]}}
      REQ = requests.post(URL,auth=HTTPBasicAuth(USER, PASS),data=json.dumps(DST),verify=False).json()
      for rpm in REQ:
         ARR[str(rpm["metadata"]["filename"])] = rpm["metadata"]["name"]
   return ARR


def get_env_rpms_list(repos_array):
   ARR   = [] 
   for repo in repos_array:
      URL = "https://" + SERVER + "/pulp/api/v2/repositories/" + repo + "/search/units/"
      DST = {"criteria": {"fields": {"unit": ["name","filename"]},"type_ids": ["rpm"]}}
      REQ = requests.post(URL,auth=HTTPBasicAuth(USER, PASS),data=json.dumps(DST),verify=False).json()
      for rpm in REQ:
         ARR.append(rpm["metadata"]["filename"])
   return ARR


def get_diff_rpms(src_rpms, dst_rpms):
   diff_rpms = []
   for x in src_rpms.keys():
      if x not in dst_rpms.keys():
         diff_rpms.append(src_rpms[x])
   return diff_rpms


SRC_DICT, DST_DICT = get_repos(SRC_ENV,DST_ENV,REPOS) 
src_rpms_all = get_env_rpms_dict(SRC_DICT)
dst_rpms_all = get_env_rpms_dict(DST_DICT)
full_list    = get_diff_rpms(src_rpms_all,dst_rpms_all)
if full_list:
    r        = requests.put(JENKINS_SERVER_URI, data={"SRC_ENV":SRC_ENV,"DST_ENV":DST_ENV,"SYNC_ENV":"yes"})   
