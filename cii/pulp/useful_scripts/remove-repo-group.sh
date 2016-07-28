#!/bin/bash

#./remove-repo-group.sh REPO_GROUP

REPO_GROUP=$1

USER="admin"
PASS="admin"

pulp-admin login -u $USER -p $PASS &> /dev/null
pulp-admin repo group delete --group-id $REPO_GROUP &> /dev/null
for i in `pulp-admin rpm repo list --fields "id" | grep $REPO_GROUP$ | cut -d: -f2`;do
pulp-admin rpm repo delete --repo-id $i
done
