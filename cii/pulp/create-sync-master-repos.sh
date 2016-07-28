#!/bin/bash
#Note: yum repos need to be configured
#Note: MASTER_GROUP_ID needs to be constructed as desired and is appended to each pulp repository

REPO_SERVER="cii-repo.ci.com"
REPO_URL="pub/centos7"
REPOIDS="base extras updates puppetlabs-deps puppetlabs-products epel foreman foreman-plugins jenkins pulp-2-stable centos-sclo-sclo centos-sclo-rh"
MASTER_GROUP_ID="7_master"
PULP_USER="admin"
PULP_PASS="admin"


# Login to Pulp
 
pulp-admin login -u $PULP_USER -p $PULP_PASS

# Create master group id 

pulp-admin repo group create --group-id $MASTER_GROUP_ID

# Create repos add them to master group and sync 

for repoid in $REPOIDS;do 

pulp-admin rpm repo create --repo-id $repoid-$MASTER_GROUP_ID --feed http://$REPO_SERVER/$REPO_URL/$repoid --serve-http true --display-name $repoid --relative-url $repoid-$MASTER_GROUP_ID
pulp-admin repo group members add --repo-id $repoid-$MASTER_GROUP_ID --group-id $MASTER_GROUP_ID
pulp-admin rpm repo  sync run  --repo-id $repoid-$MASTER_GROUP_ID
pulp-admin rpm repo publish run  --repo-id $repoid-$MASTER_GROUP_ID

done
