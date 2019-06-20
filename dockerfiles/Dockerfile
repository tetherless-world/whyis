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

WORKDIR /apps/whyis

RUN service jetty9 start;\
	curl -X POST --data-binary "@admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/admin_namespace.log &&\
	curl -X POST --data-binary "@knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/knowledge_namespace.log

RUN echo "\n\
Please configure Whyis at /apps/whyis/config.py to ensure correct customization.\n\
Follow the instructions for 'Configure Whyis' at http://tetherless-world.github.io/whyis/install.\n\
\n\
To run whyis in development mode, run the following to start it:\n\
\n\
 > sudo su - whyis\n\
 > cd /apps/whyis\n\
 > source venv/bin/activate\n\
 > python manage.py runserver\n\
\n"

ENTRYPOINT bash
