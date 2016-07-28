#!/bin/bash

# NB: Make sure storage is configured
# NB: Make sure you setup a cronjob to continually sync *before* pulp syncs

# Currently sync'd repos:

# CentOS
# CentOS SCL
# Puppet
# Foreman
# EPEL 7
# Jenkins
# Pulp

yum install wget -y

cd /tmp/

# Setup repo files: 

rm -rf /etc/yum.repos.d/*

# CentOS
wget  -r -np -nH --level=0 --cut-dirs=100 --reject "index.html*" -A 'centos-release-7*.rpm' http://mirror.centos.org/centos/7/os/x86_64/Packages/
rpm -ivh centos-release-7*.rpm --force


# Puppet                        
wget  -r -np -nH --level=0 --cut-dirs=100 http://yum.puppetlabs.com/puppetlabs-release-el-7.noarch.rpm
rpm -ivh puppetlabs-release*.rpm --force


# Foreman
wget  -r -np -nH --level=0 --cut-dirs=100 --reject "index.html*" -A 'foreman-release.rpm' http://yum.theforeman.org/releases/latest/el7/x86_64/

rpm -ivh foreman-release*.rpm --force


# EPEL 7
wget  -r -np -nH --level=0 --cut-dirs=100 --reject "index.html*" -A 'epel-release-7*.rpm' http://www.mirrorservice.org/sites/dl.fedoraproject.org/pub/epel/7/x86_64/e/
rpm -ivh epel-release-7*.rpm --force


# Jenkins
wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat-stable/jenkins.repo
sed -i 's/gpgcheck=1/gpgcheck=0/g' /etc/yum.repos.d/jenkins.repo


# Pulp
wget -O /etc/yum.repos.d/rhel-pulp.repo http://repos.fedorapeople.org/repos/pulp/pulp/rhel-pulp.repo

# Install SCL

if rpm -qa |grep centos-release-scl > /dev/null
then
yum reinstall centos-release-scl.noarch -y
else
yum install centos-release-scl.noarch -y
fi
if rpm -qa |grep centos-release-scl-rh > /dev/null
then
yum reinstall centos-release-scl-rh.noarch -y
else
yum install centos-release-scl-rh.noarch -y
fi


# Turn off gpgcheck 

sed -i "s/gpgcheck\=1/gpgcheck\=0/" /etc/yum.repos.d/*

# Install bits and pieces 

yum install createrepo -y
yum install yum-utils -y
yum install httpd -y
systemctl enable httpd
systemctl start httpd
