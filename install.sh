#!/bin/bash

echo "Installing puppet..."
apt-get install puppet
wait $!

echo "Installing puppetlabs-stdlib --version 4.14.0..."
puppet module install puppetlabs-stdlib --version 4.14.0
wait $!

echo "Installing puppetlabs-vcsrepo --version 4.14.0..."
puppet module install puppetlabs-vcsrepo --version 2.0.0
wait $!

echo "Installing maestrodev-wget --version 1.7.3..."
puppet module install maestrodev-wget --version 1.7.3
wait $!

puppet module install stankevich-python --version 1.18.2
wait $!

if [ ! -f /tmp/install_satoru.pp ]; then
    curl -skL 'https://raw.githubusercontent.com/tetherless-world/satoru/master/manifests/install.pp' > /tmp/install_satoru.pp
fi

echo "Installing blazegraph using puppet..."
puppet apply /tmp/install_satoru.pp
wait $!

echo ""
echo "Satoru is now running at http://localhost/."
echo "Visit http://localhost/register to add a new user."
echo ""
echo "To run satoru in development mode, run the following to start it:"
echo ""
echo "  > sudo su - satoru"
echo "  > cd /apps/satoru"
echo "  > source venv/bin/activate"
echo "  > python manage.py runserver"
echo ""
echo "Visit http://localhost:5000/register to add a new user."



