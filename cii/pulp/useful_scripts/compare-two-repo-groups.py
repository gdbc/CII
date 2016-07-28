#!/usr/bin/python
#Usage: ./compare-two-repo-groups.py SOURCE_REPO_GROUP DEST_REPO_GROUP
#Example: ./compare-two-repo-groups.py 7_master 7_dev

import sys
import requests
from blessings import Terminal
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()

SERVER="https://cii-pulp.ci.com/pulp/api/v2/repositories/"
USER="admin"
PASS="admin"
t=Terminal()

SRC_ENV=sys.argv[1]
DST_ENV=sys.argv[2]

repos=requests.get(SERVER,auth=HTTPBasicAuth(USER, PASS),verify=False).json()

# Get repo packages sorted out 

def get_repos(src_env, dst_env, repositories):
   src_dict={}
   dst_dict={}
   for repo in repositories:
      if src_env in repo['id'].split("-")[-1]:
         src_dict[repo['id']] = repo['content_unit_counts']['rpm']
      elif dst_env in repo['id'].split("-")[-1]:
         dst_dict[repo['id']] = repo['content_unit_counts']['rpm']
   return src_dict,dst_dict

def sort_repos(src, dst):
   print "" 
   print "%-60s %-60s" %(SRC_ENV, DST_ENV)
   print "" 
   for repo_name in src:
      short_repo = ("-").join(repo_name.split("-")[:-1])  
      if str(src[repo_name]) != str(dst[short_repo + "-" + DST_ENV]):
         dst_rep_diff = t.red(str(dst[short_repo + "-" + DST_ENV]))
      else:
	 dst_rep_diff = dst[short_repo + "-" + DST_ENV]
      print "%-30s :%-30s%-30s :%-30s" %(repo_name, src[repo_name], short_repo + "-" + DST_ENV, dst_rep_diff)

SRC_DICT, DST_DICT = get_repos(SRC_ENV,DST_ENV,repos) 

sort_repos(SRC_DICT, DST_DICT)
