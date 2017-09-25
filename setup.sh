#!/bin/bash

#curl -L http://downloads.sourceforge.net/project/bigdata/bigdata/2.1.1/blazegraph.jar > blazegraph.jar
virtualenv --no-site-packages venv
source venv/bin/activate
pip install --upgrade pip
pip install flask_script
pip install 'rdflib>=4.2.2'
pip install cryptography || env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" pip install cryptography
pip install -r requirements/dev.txt
echo "Installing puppet..."
apt-get install puppet
wait $!

echo "Installing puppetlabs-stdlib --version 4.14.0..."
puppet module install puppetlabs-stdlib --version 4.14.0
wait $!

echo "Installing maestrodev-wget --version 1.7.3..."
puppet module install maestrodev-wget --version 1.7.3
wait $!

echo "Installing blazegraph using puppet..."
puppet apply blazegraph.pp
wait $!

echo "Creating Blazegraph namespaces"
curl -X POST --data-binary @admin.properties -H 'Content-Type:text/plain' http://localhost:9999/blazegraph/namespace
wait $!
echo ""
curl -X POST --data-binary @knowledge.properties -H 'Content-Type:text/plain' http://localhost:9999/blazegraph/namespace
wait $!
echo ""
echo "To run graphene in development mode, run the following to start graphene:"
echo ""
echo "  > source venv/bin/activate"
echo "  > python manage.py runserver"
