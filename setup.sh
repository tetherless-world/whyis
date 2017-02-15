#!/bin/bash

curl -L http://downloads.sourceforge.net/project/bigdata/bigdata/2.1.1/blazegraph.jar > blazegraph.jar
virtualenv --no-site-packages venv
source venv/bin/activate
pip install -r requirements/dev.txt || env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" pip install -r requirements/dev.txt

echo "To run graphene in development mode, run:"
echo ""
echo "  > java -jar blazegraph.jar &"
echo ""
echo "to start the RDF database (Blazegraph)."
echo "And then run the following to start graphene:"
echo ""
echo "  > source venv/bin/activate"
echo "  > python manage.py runserver"
