#!/bin/bash

set -x

cd /apps/whyis

if [ -d "venv" ]; then
  source venv/bin/activate
fi

python manage.py load -i ../dsa_whyis/ontologies/prov-o.ttl -f ttl
python manage.py load -i ../dsa_whyis/ontologies/sio-subset-labels.owl -f xml
python manage.py load -i ../dsa_whyis/ontologies/geosparql_vocab_all_v1_0_1_updated.rdf -f xml
python manage.py load -i ../dsa_whyis/ontologies/ssrf.ttl -f ttl
python manage.py load -i ../dsa_whyis/ontologies/dsa-t.ttl -f ttl
python manage.py load -i ../dsa_whyis/ontologies/dsa-g.ttl -f ttl
python manage.py load -i ../dsa_whyis/ontologies/dsa-owl.ttl -f ttl
#python manage.py load -i ../dsa_whyis/ontologies/dsa_lgs-rpi_v2b.ttl -f ttl
python manage.py load -i ../dsa_whyis/ontologies/dsa_lgs-rpi_v2b.json -f json-ld

# python manage.py load -i ../dsa_whyis/ontologies/US41.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US44.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US49.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US50.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US41.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US44.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US49.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US50.1.ttl -f ttl

# python manage.py load -i ../dsa_whyis/ontologies/US65.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US65.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US65.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US79.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US92.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US92.3.ttl -f ttl

# python manage.py load -i ../dsa_whyis/ontologies/US92.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US92.2.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US92.2.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US92.2.3.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US382.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US382.1.ttl -f ttl

# python manage.py load -i ../dsa_whyis/ontologies/US33.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US33.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US33.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US33.3.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US33.4.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US33.5.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US33.6.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US67.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US67.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US67.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US70.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US70.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US70.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US84.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US84.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US84.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US254.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US254.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US254.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US254.3.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US254.4.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US255.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US255.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US255.2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US356.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US356.1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US356.2.ttl -f ttl

# python manage.py load -i ../dsa_whyis/ontologies/US69.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US69-1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US69-2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US71.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US71-1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US71-2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US85.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US85-1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US85-2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US87.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US87-1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US87-2.ttl -f ttl

# python manage.py load -i ../dsa_whyis/ontologies/US251.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US251-1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US251-1-Location.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-2.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-3.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-4.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-5.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-1-Location.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-2-Location.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-3-Location.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-4-Location.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-5-Location.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/US36-locations.ttl -f ttl

# python manage.py load -i ../dsa_whyis/ontologies/TestNY1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/TestNY1-1.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/TestNY1-1-Location.ttl -f ttl
# python manage.py load -i ../dsa_whyis/ontologies/StockbridgeAirForceTestFacility.ttl -f ttl

python manage.py load -i ../dsa_whyis/data/mil.ttl -f ttl
python manage.py load -i ../dsa_whyis/data/state.ttl -f ttl
