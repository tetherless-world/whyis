#!/usr/bin/env bash

sudo apt-get install ntp
sudo update-rc.d ntp defaults
sudo service ntp start

pushd /tmp
wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb
sudo dpkg -i puppetlabs-release-trusty.deb
sudo apt-get update
popd

mkdir -p /etc/puppet/modules

# puppet module install puppetlabs-apache
puppet module install puppetlabs-vcsrepo
puppet module install puppetlabs-stdlib
puppet module install puppetlabs-concat
puppet module install stankevich-python
puppet module install puppetlabs-firewall
puppet module install puppetlabs-apt
puppet module install maestrodev-wget
puppet module install saz-ssh
puppet module install saz-sudo
puppet module install rohlfs-gconf
puppet module install maestrodev-maven

whoami

true
