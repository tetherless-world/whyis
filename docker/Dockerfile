FROM ubuntu:16.04

# Repo
ARG BUILD_MODE=master

# Installation of required packages
RUN apt-get update
RUN apt-get install -y sudo curl

# See https://tickets.puppetlabs.com/browse/FACT-1808
# This is neccessary because puppet checks the os codename, and base docker reports Debian instead of xenial
RUN apt-get install -y lsb-release

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

RUN curl -skL "https://raw.githubusercontent.com/tetherless-world/whyis/$BUILD_MODE/manifests/install.pp" > /tmp/install_whyis.pp

RUN puppet apply /tmp/install_whyis.pp

# Delete the puppet installation (checked out from GitHub master) and replace it with the files in this checkout.
RUN rm -fr /apps/whyis
COPY / /apps/whyis
WORKDIR /apps/whyis
# Remove any existing venv
RUN rm -fr venv
RUN apt-get install -y python3-venv
RUN python3 -m venv venv
RUN bash -c "source venv/bin/activate && python3 -m pip install --upgrade pip && pip install -r requirements/dev.txt"

COPY /docker/docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

