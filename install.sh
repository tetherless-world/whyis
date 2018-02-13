#!/bin/bash

sudo apt-get update

echo "Installing puppet..."
sudo apt-get install -y puppet 

#echo "Installing virtualenv..."
#sudo apt-get install -y python-virtualenv


echo "Installing puppetlabs-stdlib --version 4.14.0..."
sudo puppet module install puppetlabs-stdlib --version 4.14.0

echo "Installing puppetlabs-vcsrepo --version 4.14.0..."
sudo puppet module install puppetlabs-vcsrepo --version 2.0.0

echo "Installing maestrodev-wget --version 1.7.3..."
sudo puppet module install maestrodev-wget --version 1.7.3

sudo puppet module install stankevich-python --version 1.18.2

curl -skL 'https://raw.githubusercontent.com/tetherless-world/satoru/master/manifests/install.pp' > /tmp/install_satoru.pp

if [ -f /vagrant/manifests/install.pp ]; then
     cp /vagrant/manifests/install.pp /tmp/install_satoru.pp
fi

sudo puppet apply /tmp/install_satoru.pp

echo ""
echo "Please configure Satoru at /apps/satoru/config.py to ensure correct customization."
echo "Satoru is now running at http://localhost/ if you installed locally, and on http://192.168.33.36 if you are using Vagrant."
echo "Follow the instructions for 'Configure Satoru' at http://tetherless-world.github.io/satoru/install."
echo ""
echo "To run satoru in development mode, run the following to start it:"
echo ""
echo "  > sudo su - satoru"
echo "  > cd /apps/satoru"
echo "  > source venv/bin/activate"
echo "  > python manage.py runserver"
echo ""
echo "Follow the instructions for 'Configure Satoru' at http://tetherless-world.github.io/satoru/install."



