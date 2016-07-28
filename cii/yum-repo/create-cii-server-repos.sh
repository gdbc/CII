#!/bin/bash

REPO_SERVER="cii-repo.ci.com"
REPOPATH="/etc/yum.repos.d/"
REPO_URL="pub/centos7"
REPOIDS="base extras updates puppetlabs-deps puppetlabs-products epel foreman foreman-plugins jenkins pulp-2-stable centos-sclo-sclo centos-sclo-rh"

# Remove existing yum repositories
rm -rf /etc/yum.repos.d/*

for i in $REPOIDS;do

echo "
[$i]
name=$i Repository
baseurl=http://$REPO_SERVER/pub/centos7/$i
gpgcheck=0
enabled=1
" >>                    $REPOPATH/$i.repo

done
