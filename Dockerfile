FROM ubuntu:16.04

# Installing curl and sudo (required for downloading and running the install script)
RUN apt-get update && apt-get install -y sudo && apt-get install -y curl
RUN curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/master/install.sh > install.sh
RUN sh install.sh && sudo puppet apply /tmp/install_whyis.pp
# NOTE: Second puppet apply is a fix for Jetty8 Puppet Bug (see Issue#37)
