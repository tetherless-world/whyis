from builtins import range
from builtins import object
import rdflib
import os
import collections
import requests
from whyis.dataurl import DataURLStorage
from werkzeug.utils import secure_filename

import tempfile

from depot.io.utils import FileIntent
from depot.manager import DepotManager

from datetime import datetime
import pytz

from whyis.namespace import np, prov, dc, frbr
from uuid import uuid4

from whyis.datastore import create_id


class Nanopublication(rdflib.Graph):
    _nanopub_resource = None

    new = True

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

    _head = None

    @property
    def head(self):
        if self._head is None:

            assertion = self.nanopub_resource.value(np.hasAssertion)
            if assertion is None:
                if isinstance(self.identifier, rdflib.BNode):
                    assertion = self.resource(rdflib.BNode())
                else:
                    assertion = self.resource(self.identifier + "_assertion")
                assertion.add(rdflib.RDF.type, np.Assertion)
                self.add((self.identifier, np.hasAssertion, assertion.identifier))
            self._assertion = rdflib.Graph(store=self.store, identifier=assertion.identifier)
        return self._assertion

    _assertion = None

    @property
    def assertion(self):
        if self._assertion is None:
            assertion = self.nanopub_resource.value(np.hasAssertion)
            if assertion is None:
                if isinstance(self.identifier, rdflib.BNode):
                    assertion = self.resource(rdflib.BNode())
                else:
                    assertion = self.resource(self.identifier + "_assertion")
                assertion.add(rdflib.RDF.type, np.Assertion)
                self.add((self.identifier, np.hasAssertion, assertion.identifier))
            self._assertion = rdflib.Graph(store=self.store, identifier=assertion.identifier)
        return self._assertion

    _pubinfo = None

    @property
    def pubinfo(self):
        if self._pubinfo is None:
            pubinfo = self.nanopub_resource.value(np.hasPublicationInfo)
            if pubinfo is None:
                if isinstance(self.identifier, rdflib.BNode):
                    pubinfo = self.resource(rdflib.BNode())
                else:
                    pubinfo = self.resource(self.identifier + "_pubinfo")
                pubinfo.add(rdflib.RDF.type, np.PublicationInfo)
                self.add((self.identifier, np.hasPublicationInfo, pubinfo.identifier))
            self._pubinfo = rdflib.Graph(store=self.store, identifier=pubinfo.identifier)
        return self._pubinfo

    _provenance = None

    @property
    def provenance(self):
        if self._provenance is None:
            provenance = self.nanopub_resource.value(np.hasProvenance)
            if provenance is None:
                if isinstance(self.identifier, rdflib.BNode):
                    provenance = self.resource(rdflib.BNode())
                else:
                    provenance = self.resource(self.identifier + "_provenance")
                provenance.add(rdflib.RDF.type, np.Provenance)
                self.add((self.identifier, np.hasProvenance, provenance.identifier))
            self._provenance = rdflib.Graph(store=self.store, identifier=provenance.identifier)
        return self._provenance

    @property
    def modified(self):
        modified = self.pubinfo.value(self.assertion.identifier, dc.modified)
        if modified is not None:
            return modified.value
