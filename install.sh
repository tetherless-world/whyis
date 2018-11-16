#!/bin/bash

curl -O https://apt.puppetlabs.com/puppetlabs-release-pc1-xenial.deb
sudo dpkg -i puppetlabs-release-pc1-xenial.deb
sudo apt-get update

echo "Installing puppet..."
sudo apt-get install -y puppet-agent libaugeas0

#echo "Installing virtualenv..."
#sudo apt-get install -y python-virtualenv

export PATH=/opt/puppetlabs/bin/:$PATH
echo "Installing puppetlabs-stdlib --version 4.14.0..."
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-stdlib

echo "Installing puppetlabs-vcsrepo --version 4.14.0..."
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-vcsrepo 

echo "Installing maestrodev-wget --version 1.7.3..."
sudo /opt/puppetlabs/bin/puppet module install maestrodev-wget

sudo /opt/puppetlabs/bin/puppet module install stankevich-python

sudo /opt/puppetlabs/bin/puppet module install elastic-elastic_stack
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-apt
sudo /opt/puppetlabs/bin/puppet module install richardc-datacat

sudo /opt/puppetlabs/bin/puppet module install puppetlabs-java

sudo /opt/puppetlabs/bin/puppet module install elastic-elasticsearch

curl -skL 'https://raw.githubusercontent.com/tetherless-world/whyis/release/manifests/install.pp' > /tmp/install_whyis.pp

if [ -f /vagrant/manifests/install.pp ]; then
     cp /vagrant/manifests/install.pp /tmp/install_whyis.pp
fi

sudo /opt/puppetlabs/bin/puppet apply /tmp/install_whyis.pp

echo ""
echo "Please configure Whyis at /apps/whyis/config.py to ensure correct customization."
echo "Whyis is now running at http://localhost/ if you installed locally, and on http://192.168.33.36 if you are using Vagrant."
echo "Follow the instructions for 'Configure Whyis' at http://tetherless-world.github.io/whyis/install."
echo ""
echo "To run whyis in development mode, run the following to start it:"
echo ""
echo "  > sudo su - whyis"
echo "  > cd /apps/whyis"
echo "  > source venv/bin/activate"
echo "  > python manage.py runserver"
echo ""
echo "Follow the instructions for 'Configure Whyis' at http://tetherless-world.github.io/whyis/install."



