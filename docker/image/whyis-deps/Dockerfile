# 20190708 Separate whyis and whyis-deps Docker images (Dockerfiles).
# whyis is the user-facing image, and the one the CI will test. We assume it will change frequently. whyis relies on whyis-deps (FROM).
# whyis-deps sets up the environment (apache, celery, redis) and installs our Python and Java dependencies. We assume it will change infrequently, because dependencies should change infrequently.
# When requirements do change, we should build and push a new whyis-deps to Dockerhub for the CI to incorporate into the whyis build.

FROM ubuntu:16.04

# Installation of required packages
RUN apt-get update && apt-get install -y sudo curl lsb-release

# Puppet
RUN curl -O https://apt.puppetlabs.com/puppetlabs-release-pc1-xenial.deb && sudo dpkg -i puppetlabs-release-pc1-xenial.deb && sudo apt-get update

RUN apt-get install -y puppet-agent libaugeas0

# Add puppet to path
ENV PATH="/opt/puppetlabs/bin:${PATH}"

# Puppet modules
RUN echo '[Docker]: Installing puppet modules'
RUN puppet module install puppetlabs-apt
RUN puppet module install richardc-datacat

COPY /docker/image/whyis-deps/install.pp /
# Need puppet/files in the right place for install.pp to run correctly
COPY /puppet/files /apps/whyis/puppet/files
RUN puppet apply /install.pp
RUN rm /install.pp
# Downstream whyis image will copy in its own /apps/whyis, so remove the files we copied in
RUN rm -fr /apps/whyis

# Install the Python requirements into the (container-)global interpreter rather than creating a virtual environment.
# Don't copy in the code yet, will do that in the whyis Dockerfile.

COPY /requirements/ /requirements
RUN pip3 install -r /requirements/dev.txt
RUN rm -fr /requirements
# Remove the pip package cache
RUN rm -fr /root/.cache

# Install the Java requirements similarly
COPY /whyis-java/pom.xml /pom.xml
RUN sudo -u whyis mvn -q dependency:go-offline -PwhyisProfile
RUN rm /pom.xml