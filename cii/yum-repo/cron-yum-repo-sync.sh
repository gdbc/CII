#!/bin/bash

REPOIDS="base extras updates puppetlabs-deps puppetlabs-products epel foreman foreman-plugins jenkins pulp-2-stable centos-sclo-sclo centos-sclo-rh"

REPOPATH="/var/www/html/pub/centos7"

# Install apache to host repos
mkdir -p $REPOPATH

for repo in $REPOIDS;do
mkdir -p $REPOPATH/$repo/cachedir

echo "syncing: $repo"
reposync -r $repo -a x86_64 -m -n --download-metadata -p $REPOPATH -e $REPOPATH/$repo/cachedir
if [ $? != 0 ]
then
logger "issue syncing repo: $repo"
fi
echo "finished syncing: $repo"

cd $REPOPATH/$repo/
if [ -f comps.xml ];then
createrepo $REPOPATH/$repo -g $REPOPATH/$repo/comps.xml
else
createrepo $REPOPATH/$repo 
fi

done

chmod 755 -R $REPOPATH

systemctl restart httpd

