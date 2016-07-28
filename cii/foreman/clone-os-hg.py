#!/usr/bin/python
#Usage: /clone-os-hg.py <source HG to clone; format hg-7_dev> <destination HG name>

import sys
import json
import time
import requests
from requests.auth import HTTPBasicAuth

SERVER              = "cii-foreman.ci.com"
USER                = "admin"
PASS                = "admin"
SOURCE_HG           = sys.argv[1]
NAME                = sys.argv[2]
HEADERS             = {'content-type': 'application/json'}
OS_URL              = "https://" + SERVER + "/api/v2/operatingsystems"
OS                  = NAME.replace("hg","cent")
OS_NAME             = OS
OS_MAJOR            = int(OS.split('_')[0].split('-')[1])
OS_FAMILY           = "Redhat"
ENV                 = OS.split('-')[1]
SRC_ENV             = "7_" + SOURCE_HG.split("_")[1]
NEW_ENV             = "7_" + NAME.split("_")[1]
SOURCE_OS           = SOURCE_HG.replace("hg","cent")

def get_proxy_id(user, password, server):
    URL             = "http://" + server + "/api/smart_proxies"
    get_smart_id    = requests.get(URL,auth=HTTPBasicAuth(user, password),verify=False).json()
    if server       == get_smart_id['results'][0]['name']:
        return get_smart_id['results'][0]['id']
    else:
      print "You have more than one smart proxy, edit the above code #lazy"
      sys.exit(-1)

def get_media_id(user, password, server, env):
    media_name      = "base-" + env
    URL             = "https://" + server + "/api/v2/media"
    get_media       = requests.get(URL,auth=HTTPBasicAuth(user, password),verify=False).json()
    for i in get_media['results']:
        if media_name in i['name']:
           return i['id']

def get_details_from_source(user, password, server):
   URL              = "http://" + server + "/api/v2/operatingsystems"
   get_os=requests.get(URL,auth=HTTPBasicAuth(user, password),verify=False).json()
   prov_ids         = []
   if SOURCE_OS     == get_os['results'][0]['name']:
       OS_ID        = get_os['results'][0]['id']
       URL          = "https://" + server + "/api/v2/operatingsystems/" + str(OS_ID)
       get_os       = requests.get(URL,auth=HTTPBasicAuth(user, password),verify=False).json()
       PTABLE_ID    = get_os['ptables'][0]['id']
       ARCH_ID      = get_os['architectures'][0]['id']
       for i in get_os['os_default_templates']:
           prov_ids.append(i['provisioning_template_id'])
       return PTABLE_ID, ARCH_ID, prov_ids
   else:
       print "No SOURCE OS FOUND, please create or change SOURCE_OS variable"
       sys.exit(-1)

def get_source_id(user, password, server, source_hg):
    URL             = "https://" + server + "/api/v2/hostgroups"
    get_hg          = requests.get(URL,auth=HTTPBasicAuth(user, password),verify=False).json()
    results         = get_hg['results']
    for i in results:
        if i['name'] == source_hg:
            return i['id']

def get_hg_classes(user, password, server, hg_id):
    URL             = "https://" + server + "/api/v2/hostgroups/" + str(hg_id) + "/puppetclass_ids"
    GET_CLASSES     = requests.get(URL,auth=HTTPBasicAuth(user, password),verify=False).json()
    return GET_CLASSES['results']

def update_classes(server, hg_id, puppet_classes):
    HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
    DATA            = {"hostgroup_id": hg_id, "puppetclass_id": puppet_classes[0]}
    URL             = "https://" + server + "/api/v2/hostgroups/" + str(hg_id) + "/puppetclass_ids"
    UPD_CLASSES     = requests.post(URL,auth=HTTPBasicAuth(User, password),data=json.dumps(DATA),headers=HEADERS,verify=False).json()
    return UPD_CLASSES

def create_env(user, password, server,new_env):
    URL             = "https://" + server + "/api/v2/environments"
    ENVIRONMENT     = {"environment":{"name":new_env}}
    HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
    CREATE_ENV      = requests.post(URL,auth=HTTPBasicAuth(user, password), data=json.dumps(ENVIRONMENT), headers=HEADERS,verify = False).json()
    return CREATE_ENV['id']

def clone_hg(user, password, server, name, hg_id):
    PARAMS          = {'name': name}
    URL             = "https://" + server + "/api/v2/hostgroups/" + str(hg_id) + "/clone"
    HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
    CLONE_HG        = requests.post(URL,params=PARAMS,auth=HTTPBasicAuth(user, password),headers=HEADERS,verify=False).json()
    return CLONE_HG

def import_classes(user, password, server, env_id, proxy_id):
    URL             = "https://" + server + "/api/v2/environments/" + str(env_id)+ "/smart_proxies/" + str(proxy_id) + "/import_puppetclasses"
    HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
    IMPORT_CLASS    = requests.post(URL,auth=HTTPBasicAuth(user, password),headers=HEADERS,verify=False)
    return IMPORT_CLASS 

def update_hg(user, password, server, new_hg_id, os_id, media_id, env_id):
    URL             = "https://" + server + "/api/hostgroups/" + str(new_hg_id)
    HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
    DATA            = {"hostgroup":{"medium_id": media_id,'operatingsystem_id':os_id,'environment_id':env_id}}
    UPD_HG          = requests.put(URL,data=json.dumps(DATA),auth=HTTPBasicAuth(user, password),verify=False,headers=HEADERS).json()
    return UPD_HG

def clone_media(user, password, server, src_env, dst_env):
    OS              = "Redhat"
    URL             = "https://" + server + "/api/media?per_page=10000"
    HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
    GET_MEDIA       = requests.get(URL,auth=HTTPBasicAuth(user, password),verify=False).json()
    for i in GET_MEDIA['results']:
        if src_env in i['name']:
            NAME    = i['name'].replace(src_env,dst_env).strip()
            PATH    = i['path'].replace(src_env,dst_env).strip()
            PARAMS  = {'medium':{'name':NAME,'path':PATH,'os_family':OS}}
            CREATE_MEDIA = requests.post(URL,auth=HTTPBasicAuth(user, password),data=json.dumps(PARAMS),headers=HEADERS,verify=False)

def get_templates(user, password, server, os_id):
    HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
    OS_URL          = "https://" + server + "/api/v2/operatingsystems/" + str(os_id) + "/os_default_templates"
    OS_TEMPS        = requests.get(OS_URL,auth=(user, password),headers=HEADERS,verify=False).json()
    return OS_TEMPS 

def get_os_id(user, password, server, os_name):
    URL             = "https://" + server + "/api/v2/operatingsystems"
    GET_OS          = requests.get(URL,auth=HTTPBasicAuth(user, password),verify=False).json()
    for results in GET_OS['results']:
        if os_name  == results['name']:
            return results['id']

def update_templates(user, password, server, os_id, src_templates):
    OS_URL          = "https://" + server + "/api/v2/operatingsystems/" + str(os_id) + "/os_default_templates"
    HEADERS         = {"Accept": "application/json","Content-Type":"application/json"}
    for temps in src_templates['results']:
        update_os   = requests.post(OS_URL,auth=(user, password),data=json.dumps(temps),headers=HEADERS,verify=False)

# Clone Media 
clone_media(USER, PASS, SERVER, SRC_ENV, NEW_ENV)
print "Cloned Media"
    
# Clone OS
ptableID,archID,provIDs = get_details_from_source(USER, PASS, SERVER)
mId                 = get_media_id(USER, PASS, SERVER, NEW_ENV)

# Create OS
operatingsystem     = {"operatingsystem":{'name':OS_NAME,'major':OS_MAJOR,'family':OS_FAMILY,'medium_ids':[mId], 'architecture_ids':[archID],'ptable_ids':[ptableID],"os_default_templates":[{'provisioning_template_id':provIDs[0],"provisioning_template_name":"test"}],'provisioning_template_ids':provIDs}}
create_os           = requests.post(OS_URL,auth=(USER, PASS),data=json.dumps(operatingsystem),headers=HEADERS,verify=False).json()
print "Cloned OS"

# Update Templates
src_os_id           = get_os_id(USER, PASS, SERVER, SOURCE_OS)
os_templates        = get_templates(USER, PASS, SERVER, src_os_id)
updated_temps       = update_templates(USER, PASS, SERVER, create_os['id'], os_templates)

# Clone Host 0roup
pId                 = get_proxy_id(USER, PASS, SERVER)
osId                = create_os['id']
sourceId            = get_source_id(USER, PASS, SERVER, SOURCE_HG)
pClasses            = get_hg_classes(USER, PASS, SERVER, sourceId)
newHg               = clone_hg(USER, PASS, SERVER, NAME, sourceId)
newHgId             = newHg['id']
newEnvId            = create_env(USER, PASS, SERVER, NEW_ENV)
importClasses       = import_classes(USER, PASS, SERVER, newEnvId, pId)
updateHg            = update_hg(USER, PASS, SERVER, newHgId, osId, mId, newEnvId)
print "Cloned HG"
