FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y curl

RUN echo "Installing puppet..."
RUN apt-get install -y puppet

RUN echo "Installing puppetlabs-stdlib --version 4.14.0..."
RUN puppet module install puppetlabs-stdlib --version 4.14.0

RUN echo "Installing puppetlabls-vcsrepo --version 4.14.0..."
RUN puppet module install puppetlabs-vcsrepo --version 2.0.0

RUN echo "Installing maestrodev-wget --version 1.7.3..."
RUN puppet module install maestrodev-wget --version 1.7.3

RUN echo "Installing stankevich-python --version 1.18.2"
RUN puppet module install stankevich-python --version 1.18.2

RUN echo "Downloading puppet configuration"
RUN curl -skL 'https://raw.githubusercontent.com/tetherless-world/whyis/master/manifests/install.pp' > /tmp/install_whyis.pp

RUN puppet apply /tmp/install_whyis.pp

RUN puppet apply /tmp/install_whyis.pp
