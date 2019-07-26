from __future__ import print_function
from builtins import range
from builtins import object
import rdflib
import os
import collections
import requests
from dataurl import DataURLStorage
from werkzeug.utils import secure_filename

import tempfile

from depot.io.utils import FileIntent
from depot.manager import DepotManager

from datetime import datetime
import pytz

from whyis.namespace import np, prov, dc, frbr
from uuid import uuid4

from datastore import create_id


class Nanopublication(rdflib.ConjunctiveGraph):
    _nanopub_resource = None

    @property
    def nanopub_resource(self):
        if self._nanopub_resource is None:
            self._nanopub_resource = self.resource(self.identifier)
            if not self._nanopub_resource[rdflib.RDF.type: np.Nanopublication]:
                self._nanopub_resource.add(rdflib.RDF.type, np.Nanopublication)
        return self._nanopub_resource

    @property
    def assertion_resource(self):
        return self.resource(self.assertion.identifier)

    @property
    def pubinfo_resource(self):
        return self.resource(self.pubinfo.identifier)

    @property
    def provenance_resource(self):
        return self.resource(self.provenance.identifier)

    _assertion = None

    @property
    def assertion(self):
        if self._assertion is None:
            assertion = self.nanopub_resource.value(np.hasAssertion)
            if assertion is None:
                assertion = self.resource(self.identifier + "_assertion")
                assertion.add(rdflib.RDF.type, np.Assertion)
                self.nanopub_resource.add(np.hasAssertion, assertion)
            self._assertion = rdflib.Graph(store=self.store, identifier=assertion.identifier)
        return self._assertion

    _pubinfo = None

    @property
    def pubinfo(self):
        if self._pubinfo is None:
            pubinfo = self.nanopub_resource.value(np.hasPublicationInfo)
            if pubinfo is None:
                pubinfo = self.resource(self.identifier + "_pubinfo")
                pubinfo.add(rdflib.RDF.type, np.PublicationInfo)
                self.nanopub_resource.add(np.hasPublicationInfo, pubinfo)
            self._pubinfo = rdflib.Graph(store=self.store, identifier=pubinfo.identifier)
        return self._pubinfo

    _provenance = None

    @property
    def provenance(self):
        if self._provenance is None:
            provenance = self.nanopub_resource.value(np.hasProvenance)
            if provenance is None:
                provenance = self.resource(self.identifier + "_provenance")
                provenance.add(rdflib.RDF.type, np.Provenance)
                self.nanopub_resource.add(np.hasProvenance, provenance)
            self._provenance = rdflib.Graph(store=self.store, identifier=provenance.identifier)
        return self._provenance

    @property
    def modified(self):
        modified = self.pubinfo.value(self.assertion.identifier, dc.modified)
        if modified is not None:
            return modified.value
