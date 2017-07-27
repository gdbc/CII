#!/bin/bash

REPO_SERVER="ci-pulp.example.com"
REPOPATH="/etc/yum.repos.d/"
REPO_URL="pulp/repos"
REPOIDS="base extras updates puppetlabs-deps puppetlabs-products epel foreman foreman-plugins jenkins pulp-2-stable centos-sclo-rh centos-sclo-sclo"
ENV="7_master"

# Remove existing yum repositories
rm -rf /etc/yum.repos.d/*

for i in $REPOIDS;do

echo "
[$i]
name=$i Repository
baseurl=http://$REPO_SERVER/$REPO_URL/"$i"-"$ENV"
gpgcheck=0
enabled=1
" >>                    $REPOPATH/$i.repo

done
