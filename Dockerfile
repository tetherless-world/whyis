FROM ubuntu:16.04

# Defining build mode variable
ARG BUILD_MODE

# Installing curl and sudo (required for downloading and running the install script)
RUN apt-get update && apt-get install -y sudo && apt-get install -y curl

# Downloading and running the installation script from GitHub (dynamic contingent on $BUILD_MODE)
RUN curl -skL "https://raw.githubusercontent.com/tetherless-world/whyis/$BUILD_MODE/install.sh" > install.sh
RUN sh install.sh

# NOTE: Second puppet apply is a fix for Jetty8 Puppet Bug (see Issue#37)
ENTRYPOINT puppet apply /tmp/install_whyis.pp && puppet apply /tmp/install_whyis.pp && bash
