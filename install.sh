#!/bin/bash

WHYIS_BRANCH="${WHYIS_BRANCH:-release}"

sudo apt-get install -y lsb-release
version=$(lsb_release -cs)
if [ "$version" == "bionic" ]; then
    curl -s -O https://apt.puppetlabs.com/puppet-release-bionic.deb
    sudo dpkg -i puppet-release-bionic.deb
elif [ "$version" == "xenial" ]; then
    curl -s -O https://apt.puppetlabs.com/puppet-release-xenial.deb
    sudo dpkg -i puppet-release-xenial.deb
fi
sudo apt-get update

echo "Installing puppet..."
sudo apt-get install -y puppet-agent libaugeas0

#echo "Installing virtualenv..."
#sudo apt-get install -y python-virtualenv

export PATH=/opt/puppetlabs/bin/:$PATH

sudo /opt/puppetlabs/bin/puppet module install puppet-python
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-vcsrepo
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-apt
sudo /opt/puppetlabs/bin/puppet module install richardc-datacat
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-java
sudo /opt/puppetlabs/bin/puppet module install puppet-nodejs --version 7.0.1

if [ -f /vagrant/manifests/install.pp ]; then
     cp /vagrant/manifests/install.pp /tmp/install_whyis.pp
else
     curl -skL "https://raw.githubusercontent.com/tetherless-world/whyis/$WHYIS_BRANCH/puppet/manifests/install.pp" > /tmp/install_whyis.pp
fi
echo "Whyis branch: $WHYIS_BRANCH"

sudo FACTER_WHYIS_BRANCH=$WHYIS_BRANCH /opt/puppetlabs/bin/puppet apply /tmp/install_whyis.pp

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



