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

The Pulp server syncs and formalizes the repositories from the yum repo server in Repo groups which are bound to environments. Pulp has an API and some smart ways of de-dupping packages in repositories saving space making traditional Yum repositories easier to manage. We’ll be leveraging this API to check for and sync packages between environments. 

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

===========
## Foreman Server

The Foreman will be used by Jenkins to provision systems including setting up host groups, operating systems, puppet environments, compute profiles and kickstarts. 

What we’re doing here is setting up the first environment(7_dev) and from there we can us a script to clone that environment to others.

<b><u>SPECS:</u></b>
* Name: cii-foreman.ci.com
* Storage: n/a
* Memory: 4GB

<b><u>Scripts:</u></b>
* Configure yum repos: create-cii-server-repos.sh
* Kickstart-template: ks-7
* Clone Env: clone-os-hg.py


<b><u>To Do:</u></b>

* Edit the server entry in create-cii-server-repos.sh and run it to setup the yum repos to get our install and upstream packages
* Install Foreman:
```
yum install foreman-installer git python-requests -y 
foreman-installer  --enable-foreman-proxy --foreman-proxy-dns=true --enable-foreman-compute-libvirt --foreman-configure-epel-repo false --foreman-configure-scl-repo false (epel and scl are disabled here as they sync’d and added via create-cii-server-repos.sh)
```
* Lets setup foreman, connect to foreman url as stated in output of install command, change the admin password to “admin”(if changed to something else be sure to change it in scripts used above) and lets get to work.
  * Infrastructure -> Compute Resources -> New Compute Resource
  * Name: “libvirtd” Provider: “Libvirtd” URL: qemu+tcp://<libvirtd hostname>:16509/system (check which ip the port 16509 is running on on the libvirtd host)
   * Create and cp your root public ssh key to the libvirtd server from ci-foreman for the root user
   * "Test Connection" and close
    * If the connection fails you may have to add some iptables rules etc
* Next, setup the first environment, “7_dev”, after that we’ll clone it to uat and prd with clone-os-hg.py that will fill in the blanks in templates etc.
  * First scp your puppet modules and environments over to the Foreman server, make the path: /etc/puppet/environments/7_dev, verify ownership is puppet.root
   * NB: You will need to add your modules to /etc/puppet/modules to facilitate importing into respective environments
   ``` 
cp -r /etc/puppet/environments/7_dev/modules/* /etc/puppet/modules/
   ```
* Configure Compute Profile:
   * Infrastructure -> Compute Profiles -> New Compute Profile
   * Name: “profile-7” CPUs: 4 Memory: 2GB  Network type: Virtual (NAT)-> Submit
* Import 7_dev environment
   * Configure -> Classes -> Import from <foreman server>
   * Select 7_dev -> Update
* Setup autosign for puppet client certs
   * Add “*.domain.name” to /etc/puppet/autosign.conf
   * Make sure permissions are foreman-proxy.puppet on this file
* Create two global parameters that we will override in our templates 
   * Configure -> Global parameters
   pulp-server: <pulp server>
   foreman-server:<foreman server>
* Add the kickstart template
   * Hosts -> Provisioning Templates -> New Template -> Name: ks-7
   * ""ks-7"" FILE
    * Note this a custom kickstart for descriptive purposes. You will probably need to configure your own.
    * CII Repos are kept out of my Puppet code so it doesn’t contaminate the CII project runs.
    * Type: Provision
* Add the 7_dev repositories:
   * Hosts -> Installation Media -> New medium

| Name                      | Path	                                                           | OS Family |    
| ------------------------- | --------------------------------------------------------------- | --------- |
| base-7_dev	               | `http://cii-pulp.ci.com/pulp/repos/base-7_dev/` 	               | Red Hat   |
| epel-7_dev	               | `http://cii-pulp.ci.com/pulp/repos/epel-7_dev/`                 | Red Hat   |
| extras-7_dev	             | `http://cii-pulp.ci.com/pulp/repos/extras-7_dev/`	              | Red Hat	  |
| foreman-7_dev             | `http://cii-pulp.ci.com/pulp/repos/foreman-7_dev/`	             | Red Hat	  |
| foreman-plugins-7_dev     | `http://cii-pulp.ci.com/pulp/repos/foreman-plugins-7_dev/`	     | Red Hat	  |
| jenkins-7_dev	            | `http://cii-pulp.ci.com/pulp/repos/jenkins-7_dev/`	             | Red Hat	  |
| pulp-2-stable-7_dev	      | `http://cii-pulp.ci.com/pulp/repos/pulp-2-stable-7_dev/`        | Red Hat   |
| puppetlabs-deps-7_dev     | `http://cii-pulp.ci.com/pulp/repos/puppetlabs-deps-7_dev/`	     | Red Hat	  |
| puppetlabs-products-7_dev | `http://cii-pulp.ci.com/pulp/repos/puppetlabs-products-7_dev/`  | Red Hat	  |
| updates-7_dev             | `http://cii-pulp.ci.com/pulp/repos/updates-7_dev/`	             | Red Hat   |
| centos-sclo-rh-7_dev      | `http://cii-pulp.ci.com/pulp/repos/centos-sclo-rh-7_dev/`       | Red Hat   |
| centos-sclo-sclo-7_dev    | `http://cii-pulp.ci.com/pulp/repos/centos-sclo-sclo-7_dev/`     | Red Hat   |

* Add the required repositories(if necessary) to the ks-7 kickstart profile to use to install from(see current kickstart as a guide)
```
# Add Repos
repo --name=base             --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/base-<%=@host.environment %> --install 
repo --name=extras           --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/extras-<%=@host.environment %> --install
repo --name=updates          --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/updates-<%=@host.environment %> --install
repo --name=epel             --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/epel-<%=@host.environment %> --install 
repo --name=pulp             --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/pulp-2-stable-<%=@host.environment %> --install 
repo --name=puppet-deps      --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/puppetlabs-deps-<%=@host.environment %> --install  
repo --name=puppet-products  --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/puppetlabs-products-<%=@host.environment %> --install 
repo --name=centos-sclo-sclo --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/centos-sclo-sclo-<%=@host.environment %> --install 
repo --name=centos-sclo-rh   --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/centos-sclo-rh-<%=@host.environment %> -install
repo --name=foreman          --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/foreman-<%=@host.environment %> --install
repo --name=foreman-plugins  --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/foreman-plugins<%=@host.environment %> --install
repo --name=jenkins          --baseurl=http://<%= @host.params['pulp-server'] %>/pulp/repos/jenkins<%=@host.environment %> --install
```

* Configure Subnets
     * Infrastructure -> Subnets -> New Subnet
     * Name: base-network
     * Network address: `<your network address>`
     * Network mask: `<your netmask>`
     * Gateway address: `<your gateway>`
     * Primary DNS: `<ip of foreman server>`
     * Boot Mode: DHCP
     * Domain: ci.com
     * TFTP Proxy: ci-foreman.ci.com
     * DNS/Reverse Proxy: leave blank else you may find yourself editing zone files
     * NB: Because this is on a host that runs libvirt and serves dhcp we need to edit that config to point pxe boots to this foreman server
     * On the libvirtd host server run:
     * virsh net-edit default
     * Add: `“<bootp file='/pxelinux.0' server='<ip of foreman server>'/>”` between the `<dhcp>` tag
       
* Configure Operating systems
     * Hosts -> Operating systems -> New Operating system
     * Name: cent-7_dev 
     * Major version: 7 
     * OS Family: Red Hat
     * Arch: x86_64
     * Partition table: Kickstart default
     * Installation media: `<select all *-7_dev repositories>`
     * Submit

* `“Associate template with Operating System”`
     * Hosts -> Provisioning Templates
     * Find ks-7 -> Association, select `“cent-7_dev 7”` 
     * Submit
     * Find “Kickstart default PXELinux” -> Association, select `“cent-7_dev 7”`
     * Submit
* Back to cent-7_dev 7,  HOST -> OS -> cent-7_dev 7 -> Templates
     * provision: ks-7
     * PXELinux: Kickstart default PXELinux
     * Submit
