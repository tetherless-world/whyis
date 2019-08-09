FROM ubuntu:18.04

# See https://tickets.puppetlabs.com/browse/FACT-1808
RUN apt-get update &&\
	apt-get install -y\
	lsb-release\
	socat\
	curl

# Puppet
RUN curl -O https://apt.puppetlabs.com/puppetlabs-release-pc1-xenial.deb &&\
	dpkg -i puppetlabs-release-pc1-xenial.deb &&\
	apt-get update

RUN apt-get install -y\
	puppet-agent\
	libaugeas0

ENV PATH="/opt/puppetlabs/bin:${PATH}"

RUN puppet module install\
	puppetlabs-stdlib --version 6.0.0

# Essentially a ubuntu container with puppet
