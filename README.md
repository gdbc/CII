# A Poor Man's guide to Continuous Infrastructure Integration using Jenkins, Foreman and Pulp
===================================================================================================

* Author: Graeme Brooks-Crawford
* Email: graemedbc@gmail.com
* Date: 23/07/2016


## Intro

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
* 1 x Foreman server KVM VM
* 1 x YUM repo server KVM VM
* 1 x Pulp server KVM VM
* 1 x Jenkins server KVM VM

<b>Note:</b> All systems used here are on a libvirtd host, upon which they are guests. This libvirtd servers name is core.ci.com and will be used as a compute resource provider.

## Libvirt Host

This server hosts the CII systems and needs to be enabled for  Foreman to  access and rebuild VM’s.
