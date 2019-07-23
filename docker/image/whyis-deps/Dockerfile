# 20190708 Separate whyis and whyis-deps Docker images (Dockerfiles).
# whyis is the user-facing image, and the one the CI will test. We assume it will change frequently. whyis relies on whyis-deps (FROM).
# whyis-deps sets up the environment (apache, celery, redis) and installs our Python and Java dependencies. We assume it will change infrequently, because dependencies should change infrequently.
# When requirements do change, we should build and push a new whyis-deps to Dockerhub for the CI to incorporate into the whyis build.

FROM ubuntu:16.04

# Installation of required packages
RUN apt-get update
RUN apt-get install -y sudo curl

# See https://tickets.puppetlabs.com/browse/FACT-1808
# This is neccessary because puppet checks the os codename, and base docker reports Debian instead of xenial
RUN apt-get install -y lsb-release

# Add nodejs
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs

# RUN apt-get install -y default-jdk build-essential automake subversion libapache2-mod-wsgi libblas3 libblas-dev celeryd redis-server apache2 libffi-dev libssl-dev maven python3-dev libdb5.3-dev

# Puppet
RUN curl -O https://apt.puppetlabs.com/puppetlabs-release-pc1-xenial.deb && sudo dpkg -i puppetlabs-release-pc1-xenial.deb && sudo apt-get update

RUN apt-get install -y puppet-agent libaugeas0

# Add puppet to path
ENV PATH="/opt/puppetlabs/bin:${PATH}"

# Puppet modules
RUN echo '[Docker]: Installing puppet modules'
RUN puppet module install puppet-python
RUN puppet module install puppetlabs-vcsrepo
RUN puppet module install maestrodev-wget
RUN puppet module install puppetlabs-apt
RUN puppet module install richardc-datacat
RUN puppet module install puppetlabs-java
RUN puppet module install puppetlabs-nodejs

# RUN curl -skL "https://raw.githubusercontent.com/tetherless-world/whyis/$BUILD_MODE/manifests/install.pp" > /tmp/install_whyis.pp
# RUN puppet apply /tmp/install_whyis.pp
COPY /docker/image/whyis-deps/install.pp /
RUN puppet apply /install.pp
RUN rm /install.pp

# Install the Python requirements into the (container-)global interpreter rather than creating a virtual environment.
# Don't copy in the code yet, will do that in the whyis Dockerfile.
COPY /requirements/ /requirements
RUN pip3 install -r /requirements/dev.txt
RUN rm -fr /requirements
RUN rm -fr /root/.cache

# Install the Java requirements similarly
COPY /whyis-java/pom.xml /pom.xml
RUN sudo -u whyis mvn -q dependency:go-offline -PwhyisProfile
RUN rm /pom.xml