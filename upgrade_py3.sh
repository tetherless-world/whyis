#!/bin/bash

echo "Archiving Python 2 virtualenv to /apps/py2venv.tgz..."
pushd /apps/whyis
sudo tar cfz /apps/py2venv.tgz venv
sudo rm -rf venv
popd
echo "Done."

sudo service stop jetty8

sudo /opt/puppetlabs/bin/puppet module uninstall stankevich-python
sudo /opt/puppetlabs/bin/puppet module install puppet-python
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-vcsrepo
sudo /opt/puppetlabs/bin/puppet module install maestrodev-wget
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-apt
sudo /opt/puppetlabs/bin/puppet module install richardc-datacat
sudo /opt/puppetlabs/bin/puppet module install puppetlabs-java
sudo /opt/puppetlabs/bin/puppet module install puppet-nodejs --version 7.0.1

sudo /opt/puppetlabs/bin/puppet apply puppet/manifests/install.pp

echo "To complete the upgrade, re-install your whyis app using 'pip install -e' into /apps/whyis/venv and restart apache2 and celeryd."
