#!/bin/bash

#Usage: ./clone-create-environment.sh SOURCE_GRP DESTINATION_GRP FEED_GRP
#Feed group is usually SOURCE_GRP

SRC=$1
DST=$2
FEED=$3

USER="admin"
PASS="admin"
SERVER="cii-pulp.ci.com"
SERVER_URL="http://$SERVER/pulp/repos"

pulp-admin login -u $USER -p $PASS &> /dev/null


# Functions

get_src_env() {

for i in `pulp-admin rpm repo list --field id 2> /dev/null|grep Id| cut -d: -f2`;do echo $i | grep $1$ ;done

}

new_dst_env() {

REPOS=$@
for i in `echo $REPOS | sed "s/$SRC/$DST/g"`;do
echo "$i"
done

}


create_repos() {

NEW_REPOS=$@

for i in `echo $NEW_REPOS`;do 
pulp-admin rpm repo create --repo-id $i
pulp-admin rpm repo update --serve-http true --repo-id $i
done

}


#This needs to change so it can sync from the feed
sync_repos() {

SR=$@

for i in `echo $SR`;do
SRC_REPO=$i
DST_REPO=`echo $i | sed "s/$SRC/$DST/g"`
echo "Syncing $SRC_REPO to $DST_REPO"
pulp-admin rpm repo copy all --from-repo-id $SRC_REPO --to-repo-id $DST_REPO
echo "Syncing $DST_REPO complete"
echo ""
done

}

publish_repos() {

NEW_REPOS=$@

for i in `echo $NEW_REPOS`;do
pulp-admin rpm repo publish run  --repo-id $i
done

}


add_members_to_group() {

echo "Creating group $DST"
GRP=$@
pulp-admin repo group create --group-id $DST
for i in `echo $GRP`;do
echo "Adding $i as member to $DST group"
pulp-admin repo group members add --group-id $DST --repo-id $i
done

}


update_group_feed() {

echo "Updating feeds for $DST"
GRP=$@
for i in `echo $GRP`;do
no_env=`echo $i | rev | cut -d- -f2- | rev`
pulp-admin rpm repo update --serve-http true --feed "$SERVER_URL/$no_env-$FEED" --repo-id "$no_env-$DST"
done

}

SOURCE_REPOS=`get_src_env $SRC`
NEW_REPOS=`new_dst_env $SOURCE_REPOS`
create_repos $NEW_REPOS
add_members_to_group $NEW_REPOS
sync_repos $SOURCE_REPOS
publish_repos $NEW_REPOS
update_group_feed $NEW_REPOS
