# A Poor Man's guide to Continuous Infrastructure Integration using Jenkins, Foreman and Pulp
===================================================================================================

* Author: Graeme Brooks-Crawford
* Email: graemedbc@gmail.com
* Date: 23/07/2016


## Introduction

This is a poor man's guide to building an Automated Continuous Infrastructure Integration or CII on RPM based Linux distributions that use Puppet and GIT. 

Use this guide if you want to sync and test newly synced packages in an environment automatically, as well as test new or edited puppet code and post install TAP compliant scripts to test, verify and graph build environment integrity after packages have been installed and puppet has been run.

This is called “The poor man’s guide” as we leverage most of the FOSS upstream tools bundled into Red Hat’s Satellite Server(Foreman, Pulp, Puppet) and combine them via API scripts and Jenkins to produce automated patch, configuration and testing of Operating System builds. So if you don't have Red Hat Satellite in your environment but need automated testing of code and packages on your builds, then this guide is for you.

 For a good CII template based on Red Hat’s Satellite server, please look at Dr Nick Strugnell's excellent guide here: https://github.com/RedHatSatellite/soe-ci.
 
 This guide will show you how to to setup and configure an CII engine that can be initialized from 3 execution points.

These three points:

* Automate testing of new packages synced into environment repositories
* Automate testing of added/edited puppet configuration in GIT
* Automate execution and graphing of Bash Automated Testing(BAT: https://github.com/sstephenson/bats) which is Test      Anything Protocol (TAP: https://testanything.org/producers.html) compliant, when tests are added or edited in GIT. These tests are run post build and used for verification of build integrity to justify functionality in a designated environment.

This enables infrastructure teams to release patches and configuration and automatically test the results of those changes and those patches and configuration will work in the target environments, be it DEV, UAT or PRD, reducing or negating manual effort to achieve and document the same results.

Even if you have a staggered release cycle, it still pays to use CII to do the work up until you release.

## Environment Configuration

We’re going to work with 3 environments 7_dev, 7_uat and 7_prd. These three environments coincide with Pulp repo groups with the same name, Foreman Puppet environments with the same name, similarly named Foreman Host Groups(hg-7_dev...) and Foreman Operating Systems (cent-7_dev...). The OS used in this guide is CentOS 7, though any RPM based distro should work.

Follow this guide to the end and a much clearer picture of what we’re doing will be revealed.

## System Requirements

* 1 x Libvirtd host
* 1 x Yum repo server KVM VM
* 1 x Pulp server KVM VM
* 1 x Foreman server KVM VM
* 1 x Jenkins server KVM VM

**Note:** All systems used here are on a libvirtd host, upon which they are guests. This libvirtd servers name is core.ci.com and will be used as a compute resource provider.

## Libvirt Host

This server hosts the CII systems and needs to be enabled for  Foreman to  access and rebuild VM’s.

<b><u>SPECS:</u></b>
* Name: core.ci.com
* Storage: Mount: /var/lib/libvirt/images Size: 1TB
* Memory: 32GB

We dont have too much to do here except open up a port for foreman to use and to do this we need to edit <b>/etc/libvirt/libvirtd.conf</b>
```
listen_tls = 0
listen_tcp = 1
listen_addr = “0.0.0.0”
auth_tcp = "none"
```

And lastly change /etc/sysconfig/libvirtd and uncomment/add the following:
```
 LIBVIRTD_ARGS=”--listen”
```
Restart the server or libvirtd

=============
## Yum Repo Server

This server probably exists in your environment already as a provider of yum repositories to your clients. Here we're using it merely as a proof of concept for completion purposes.

This server is connected to external, upstream yum repository providers as well as being able to host local company specific repos with custom rpms, it's the upstream source of where the Pulp server will source its content for our CII engine, serving primarily the 7_master Pulp repo group. 

```
Edit (<<yum-server-repo-srv-config.sh>>) to change, and create your repos. Again, if you have a yum repository server already ignore this script.
```
Here we setup a cron job (<<cron-yum-repo-sync.sh>>) to continually sync from our upstream repositories. We will create a sync between Pulp and the repository server so we can determine diffs in repositories within each Pulp repo groups repositories. This will be one of our build triggers and configured later.

<b><u>SPECS:</u></b>
* Name: cii-repo.ci.com
* Storage: Mount: /var/www/html Size: 100GB
* Memory: 4GB

<b><u>Scripts:</u></b>
* Configuration Script: (<<yum-server-repo-srv-config.sh>>)
* Cron Script: (<<cron-yum-repo-sync.sh>>)

<b><u>To Do:</u></b>

* Edit yum-server-repo-srv-config.sh to include or exclude the yum repositories required
* Run the yum-server-repo-srv-config.sh which will configure upstream yum repos to sync. 
* Add cron-yum-repo-sync.sh to run in a cron which periodically syncs the configured repositories. I’ve set this up to run hourly by cp’ing it into /etc/cron.hourly. There will be a Pulp script that pulls these repo’s into a “master” repo and diffs it against ongoing environments which initialize Jenkins jobs to test the new packages.
* Copy the.treeinfo, .discinfo files and the images and LiveOS folders from the “base” upstream repository to /var/www/html/pub/centos7/base/ This will ensure that you get the yum groups needed for installation and the pxe files needed to install systems that require yum groups.

========================
## Pulp Repository Server

The Pulp server syncs and formalizes the repositories from the yum repo server. It has an API and some smart ways of de-dupping packages in repositories saving space and making the repositories easy to manage. We’ll be leveraging this api to check for and sync packages between environments. 

Installing the Pulp server is out of scope as there's sufficient documentation on the project's site. FYI: I’ve included a very basic install script<<install-pulp.sh> which you may want to use if you fancy, however your distance may vary.

<b><u>SPECS:</u></b>
* Name: cii-pulp.ci.com
* Storage: Mount: /var/lib/pulp Size: 100GB
* Storage 1: Mount: /var/lib/mongodb Size: 50GB
* Memory: 8GB

<b><u>Scripts:</u></b>
* Install Pulp Server: install-pulp.sh
* Configure yum repos: create-cii-server-repos.sh
* Create, sync master repo: create-sync-master-repos.sh
* Sync master repo group: sync-master-repo-group.py
* Pulp environment diff check: pulp-env-diff-check.py

<b><u>To Do:</u></b> 

* Configure mount point /var/lib/pulp and /var/lib/mongodb
* Edit the server entry in create-cii-server-repos.sh and run it to setup the yum repos we will use as our upstream source.
* Change REPO_SERVER and MASTER_GROUP_ID in create-sync-master-repos.sh and execute. This will create the master pulp repo group and repos that syncs directly from the repo server. This repo will be used to determine diffs against the eng environment, then eng against dev and so on to determine a difference and kickoff a jenkins jobs.
* Change USER/PASS SERVER_URL in clone-create-repo-group.sh and create your other environments.
  * Syntax: ./clone-create-repo-group.sh SRC_GRP DST_GRP FEED_GRP
  … where FEED_GRP is the repo group you’ll be syncing from ie: dev -> uat -> prd eg:
   ```
   ./clone-create-repo-group.sh 7_master 7_dev 7_master
   ./clone-create-repo-group.sh 7_dev 7_uat 7_dev
   ./clone-create-repo-group.sh 7_uat 7_prd 7_uat
   ```
* Change SERVER, DST_ENV and USER/PASS in sync-master-repo-group.py and copy it to /etc/cron.daily
* Create three or however many copies of pulp-env-diff-check.py, one for each repo group or environment, this involves changing SERVER, SRC_ENV, DST_ENV and the JENKINS_SERVER_URI. This script compares a repository group against one that it syncs from(source). This enables us to determine if new packages are found upstream and if there are, a jenkins job is triggered to test these new packages. 
  * Example: For the DEV environment, SRC_ENV would be “7_master” and DST_ENV would be “7_dev”. What this means is a diff between the “7_master” and “7_dev” repo group is run periodically and if a diff exists (more packages in the 7_master repo), a jenkins job will be started.
  * Put these script in cron.daily or whatever suites or in line with business requirements.
 
<b><u>NB:</u></b> Many of the scripts following rely on the environment matching this MASTER_GROUP_ID in particular the pulp repo names: puppetlabs-deps-7_master. They end in 7_master, split on an “-” which demarcates the environment. We’re going to use this elsewhere in Jenkins and Foreman.

