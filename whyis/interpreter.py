# from __future__ import print_function
# from future import standard_library
# standard_library.install_aliases()
# from builtins import str
# from builtins import range
import rdflib
from datetime import datetime
from nanopub import Nanopublication
import logging
import sys
import pandas as pd
import configparser
import hashlib

from .autonomic.update_change_service import UpdateChangeService

from whyis.namespace import whyis, prov, sio


class Interpreter(UpdateChangeService):
    kb = ":"
    cb_fn = None
    timeline_fn = None
    data_fn = None
    prefix_fn = "prefixes.txt"
    prefixes = {}
    studyRef = None
    unit_code_list = []
    unit_uri_list = []
    unit_label_list = []

    explicit_entry_list = []
    virtual_entry_list = []

    explicit_entry_tuples = []
    virtual_entry_tuples = []

    cb_tuple = {}
    timeline_tuple = {}

    config = configparser.ConfigParser()

    def __init__(self, config_fn=None):  # prefixes should be
        if config_fn is not None:
            try:
                self.config.read(config_fn)
            except Exception as e:
                logging.exception("Error: Unable to open configuration file: ")
                if hasattr(e, 'message'):
                    logging.exception(e.message)
                else:
                    logging.exception(e)
                sys.exit(1)

            if self.config.has_option('Prefixes', 'prefixes'):
                self.prefix_fn = self.config.get('Prefixes', 'prefixes')
            # prefix_file = open(self.prefix_fn,"r")
            # self.prefixes = prefix_file.readlines()
            prefix_file = pd.read_csv(self.prefix_fn, dtype=object)
            try:
                for row in prefix_file.itertuples():
                    self.prefixes[row.prefix] = row.url
            except Exception as e:
                logging.exception("Error: Something went wrong when trying to read the Prefix File: ")
                if hasattr(e, 'message'):
                    logging.exception(e.message)
                else:
                    logging.exception(e)
                sys.exit(1)

            if self.config.has_option('Prefixes', 'base_uri'):
                self.kb = self.config.get('Prefixes', 'base_uri')

            if self.config.has_option('Source Files', 'dictionary'):
                dm_fn = self.config.get('Source Files', 'dictionary')
                try:
                    dm_file = pd.read_csv(dm_fn, dtype=object)
                    try:  # Populate virtual and explicit entry lists
                        for row in dm_file.itertuples():
                            if pd.isnull(row.Column):
                                logging.exception("Error: The SDD must have a column named 'Column'")
                                sys.exit(1)
                            if row.Column.startswith("??"):
                                self.virtual_entry_list.append(row)
                            else:
                                self.explicit_entry_list.append(row)
                    except Exception as e:
                        logging.exception(
                            "Error: Something went wrong when trying to read the Dictionary Mapping File: ")
                        if hasattr(e, 'message'):
                            logging.exception(e.message)
                        else:
                            logging.exception(e)
                        sys.exit(1)
                except Exception as e:
                    logging.exception("Error: The specified Dictionary Mapping file does not exist: ")
                    if hasattr(e, 'message'):
                        logging.exception(e.message)
                    else:
                        logging.exception(e)
                    sys.exit(1)

            if self.config.has_option('Source Files', 'codebook'):
                self.cb_fn = self.config.get('Source Files', 'codebook')
            if self.cb_fn is not None:
                try:
                    cb_file = pd.read_csv(self.cb_fn, dtype=object)
                    try:
                        inner_tuple_list = []
                        for row in cb_file.itertuples():
                            if (pd.notnull(row.Column) and row.Column not in self.cb_tuple):
                                inner_tuple_list = []
                            inner_tuple = {}
                            inner_tuple["Code"] = row.Code
                            if pd.notnull(row.Label):
                                inner_tuple["Label"] = row.Label
                            if pd.notnull(row.Class):
                                inner_tuple["Class"] = row.Class
                            if "Resource" in row and pd.notnull(row.Resource):
                                inner_tuple["Resource"] = row.Resource
                            inner_tuple_list.append(inner_tuple)
                            self.cb_tuple[row.Column] = inner_tuple_list
                    except Exception as e:
                        logging.warning("Warning: Unable to process Codebook file: ")
                        if hasattr(e, 'message'):
                            logging.warning(e.message)
                        else:
                            logging.warning(e)
                except Exception as e:
                    logging.exception("Error: The specified Codebook file does not exist: ")
                    if hasattr(e, 'message'):
                        logging.exception(e.message)
                    else:
                        logging.exception(e)
                    sys.exit(1)

            if self.config.has_option('Source Files', 'timeline'):
                self.timeline_fn = self.config.get('Source Files', 'timeline')
            if self.timeline_fn is not None:
                try:
                    timeline_file = pd.read_csv(self.timeline_fn, dtype=object)
                    try:
                        inner_tuple_list = []
                        for row in timeline_file.itertuples():
                            if pd.notnull(row.Name) and row.Name not in self.timeline_tuple:
                                inner_tuple_list = []
                            inner_tuple = {}
                            inner_tuple["Type"] = row.Type
                            if pd.notnull(row.Label):
                                inner_tuple["Label"] = row.Label
                            if pd.notnull(row.Start):
                                inner_tuple["Start"] = row.Start
                            if pd.notnull(row.End):
                                inner_tuple["End"] = row.End
                            if pd.notnull(row.Unit):
                                inner_tuple["Unit"] = row.Unit
                            if pd.notnull(row.inRelationTo):
                                inner_tuple["inRelationTo"] = row.inRelationTo
                            inner_tuple_list.append(inner_tuple)
                            self.timeline_tuple[row.Name] = inner_tuple_list
                    except Exception as e:
                        logging.warning("Warning: Unable to process Timeline file: ")
                        if hasattr(e, 'message'):
                            logging.warning(e.message)
                        else:
                            logging.warning(e)
                except Exception as e:
                    logging.exception("Error: The specified Timeline file does not exist: ")
                    if hasattr(e, 'message'):
                        logging.exception(e.message)
                    else:
                        logging.exception(e)
                    sys.exit(1)

            if self.config.has_option('Source Files', 'code_mappings'):
                cmap_fn = self.config.get('Source Files', 'code_mappings')
                code_mappings_reader = pd.read_csv(cmap_fn)
                for code_row in code_mappings_reader.itertuples():
                    if pd.notnull(code_row.code):
                        self.unit_code_list.append(code_row.code)
                    if pd.notnull(code_row.uri):
                        self.unit_uri_list.append(code_row.uri)
                    if pd.notnull(code_row.label):
                        self.unit_label_list.append(code_row.label)

            if self.config.has_option('Source Files', 'data_file'):
                self.data_fn = self.config.get('Source Files', 'data_file')

    def getInputClass(self):
        return whyis.SemanticDataDictionary

    def getOutputClass(self):
        return whyis.SemanticDataDictionaryInterpretation

    def get_query(self):
        return '''SELECT ?s WHERE { ?s ?p ?o .} LIMIT 1\n'''

    def process(self, i, o):
        print("Processing SDD...")
        self.app.db.store.nsBindings = {}
        npub = Nanopublication(store=o.graph.store)
        # prefixes={}
        # prefixes.update(self.prefixes)
        # prefixes.update(self.app.NS.prefixes)
        self.writeVirtualEntryNano(npub)
        self.writeExplicitEntryNano(npub)
        self.interpretData(npub)

    def parseString(self, input_string, delim):
        my_list = input_string.split(delim)
        my_list = [element.strip() for element in my_list]
        return my_list

    def rdflibConverter(self, input_word):
        if "http" in input_word:
            return rdflib.term.URIRef(input_word)

        if ':' in input_word:
            word_list = input_word.split(":")
            term = self.prefixes[word_list[0]] + word_list[1]
            return rdflib.term.URIRef(term)

        return rdflib.Literal(input_word, datatype=rdflib.XSD.string)

    def codeMapper(self, input_word):
        unitVal = input_word
        for unit_label in self.unit_label_list:
            if unit_label == input_word:
                unit_index = self.unit_label_list.index(unit_label)
                unitVal = self.unit_uri_list[unit_index]
        for unit_code in self.unit_code_list:
            if unit_code == input_word:
                unit_index = self.unit_code_list.index(unit_code)
                unitVal = self.unit_uri_list[unit_index]
        return unitVal

    def convertVirtualToKGEntry(self, *args):
        if args[0][:2] == "??":
            if self.studyRef is not None:
                if args[0] == self.studyRef:
                    return self.prefixes[self.kb] + args[0][2:]
            if len(args) == 2:
                return self.prefixes[self.kb] + args[0][2:] + "-" + args[1]
            return self.prefixes[self.kb] + args[0][2:]
        if ':' not in args[0]:
            # Check for entry in column list
            for item in self.explicit_entry_list:
                if args[0] == item.Column:
                    if len(args) == 2:
                        return self.prefixes[self.kb] + args[0].replace(" ", "_").replace(",", "").replace("(",
                                                                                                           "").replace(
                            ")", "").replace("/", "-").replace("\\", "-") + "-" + args[1]
                    return self.prefixes[self.kb] + args[0].replace(" ", "_").replace(",", "").replace("(", "").replace(
                        ")", "").replace("/", "-").replace("\\", "-")
            return '"' + args[0] + "\"^^xsd:string"
        return args[0]

    def checkVirtual(self, input_word):
        try:
            if input_word[:2] == "??":
                return True
            return False
        except Exception as e:
            logging.exception("Something went wrong in Interpreter.checkVirtual(): ")
            if hasattr(e, 'message'):
                logging.exception(e.message)
            else:
                logging.exception(e)
            sys.exit(1)

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def writeVirtualEntryNano(self, nanopub):
        for item in self.virtual_entry_list:
            virtual_tuple = {}
            term = rdflib.term.URIRef(self.prefixes[self.kb] + str(item.Column[2:]))
            nanopub.assertion.add((term, rdflib.RDF.type, rdflib.OWL.Class))
            nanopub.assertion.add(
                (term, rdflib.RDFS.label, rdflib.Literal(str(item.Column[2:]), datatype=rdflib.XSD.string)))
            # Set the rdf:type of the virtual row to either the Attribute or Entity value (or else owl:Individual)
            if (pd.notnull(item.Entity)) and (pd.isnull(item.Attribute)):
                if ',' in item.Entity:
                    entities = self.parseString(item.Entity, ',')
                    for entity in entities:
                        nanopub.assertion.add(
                            (term, rdflib.RDFS.subClassOf, self.rdflibConverter(self.codeMapper(entity))))
                else:
                    nanopub.assertion.add(
                        (term, rdflib.RDFS.subClassOf, self.rdflibConverter(self.codeMapper(item.Entity))))
                virtual_tuple["Column"] = item.Column
                virtual_tuple["Entity"] = self.codeMapper(item.Entity)
                if virtual_tuple["Entity"] == "hasco:Study":
                    self.studyRef = item.Column
                    virtual_tuple["Study"] = item.Column
            elif (pd.isnull(item.Entity)) and (pd.notnull(item.Attribute)):
                if ',' in item.Attribute:
                    attributes = self.parseString(item.Attribute, ',')
                    for attribute in attributes:
                        nanopub.assertion.add(
                            (term, rdflib.RDFS.subClassOf, self.rdflibConverter(self.codeMapper(attribute))))
                else:
                    nanopub.assertion.add(
                        (term, rdflib.RDFS.subClassOf, self.rdflibConverter(self.codeMapper(item.Attribute))))
                virtual_tuple["Column"] = item.Column
                virtual_tuple["Attribute"] = self.codeMapper(item.Attribute)
            else:
                logging.warning(
                    "Warning: Virtual entry not assigned an Entity or Attribute value, or was assigned both.")
                virtual_tuple["Column"] = item.Column

            # If there is a value in the inRelationTo column ...
            if pd.notnull(item.inRelationTo):
                virtual_tuple["inRelationTo"] = item.inRelationTo
                # If there is a value in the Relation column but not the Role column ...
                if (pd.notnull(item.Relation)) and (pd.isnull(item.Role)):
                    nanopub.assertion.add((term, self.rdflibConverter(item.Relation),
                                           self.rdflibConverter(self.convertVirtualToKGEntry(item.inRelationTo))))
                    virtual_tuple["Relation"] = item.Relation
                # If there is a value in the Role column but not the Relation column ...
                elif (pd.isnull(item.Relation)) and (pd.notnull(item.Role)):
                    role = rdflib.BNode()
                    nanopub.assertion.add(
                        (role, rdflib.RDF.type, self.rdflibConverter(self.convertVirtualToKGEntry(item.Role))))
                    nanopub.assertion.add(
                        (role, sio.inRelationTo, self.rdflibConverter(self.convertVirtualToKGEntry(item.inRelationTo))))
                    nanopub.assertion.add((term, sio.hasRole, role))
                    virtual_tuple["Role"] = item.Role
                # If there is a value in the Role and Relation columns ...
                elif (pd.notnull(item.Relation)) and (pd.notnull(item.Role)):
                    virtual_tuple["Relation"] = item.Relation
                    virtual_tuple["Role"] = item.Role
                    nanopub.assertion.add(
                        (term, sio.hasRole, self.rdflibConverter(self.convertVirtualToKGEntry(item.Role))))
                    nanopub.assertion.add((term, self.rdflibConverter(item.Relation),
                                           self.rdflibConverter(self.convertVirtualToKGEntry(item.inRelationTo))))
            nanopub.provenance.add((term, prov.generatedAtTime, rdflib.Literal(
                "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year, datetime.utcnow().month,
                                             datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(
                    datetime.utcnow().hour, datetime.utcnow().minute, datetime.utcnow().second) + "Z",
                datatype=rdflib.XSD.dateTime)))
            if pd.notnull(item.wasDerivedFrom):
                if ',' in item.wasDerivedFrom:
                    derivedFromTerms = self.parseString(item.wasDerivedFrom, ',')
                    for derivedFromTerm in derivedFromTerms:
                        nanopub.provenance.add((term, prov.wasDerivedFrom,
                                                self.rdflibConverter(self.convertVirtualToKGEntry(derivedFromTerm))))
                else:
                    nanopub.provenance.add((term, prov.wasDerivedFrom,
                                            self.rdflibConverter(self.convertVirtualToKGEntry(item.wasDerivedFrom))))
                virtual_tuple["wasDerivedFrom"] = item.wasDerivedFrom
            if pd.notnull(item.wasGeneratedBy):
                if ',' in item.wasGeneratedBy:
                    generatedByTerms = self.parseString(item.wasGeneratedBy, ',')
                    for generatedByTerm in generatedByTerms:
                        nanopub.provenance.add((term, prov.wasGeneratedBy,
                                                self.rdflibConverter(self.convertVirtualToKGEntry(generatedByTerm))))
                else:
                    nanopub.provenance.add((term, prov.wasGeneratedBy,
                                            self.rdflibConverter(self.convertVirtualToKGEntry(item.wasGeneratedBy))))
                virtual_tuple["wasGeneratedBy"] = item.wasGeneratedBy
            self.virtual_entry_tuples.append(virtual_tuple)

        if self.timeline_fn is not None:
            for key in self.timeline_tuple:
                tl_term = self.rdflibConverter(self.convertVirtualToKGEntry(key))
                nanopub.assertion.add((tl_term, rdflib.RDF.type, rdflib.OWL.Class))
                for timeEntry in self.timeline_tuple[key]:
                    if 'Type' in timeEntry:
                        nanopub.assertion.add(
                            (tl_term, rdflib.RDFS.subClassOf, self.rdflibConverter(timeEntry['Type'])))
                    if 'Label' in timeEntry:
                        nanopub.assertion.add((tl_term, rdflib.RDFS.label,
                                               rdflib.Literal(str(timeEntry['Label']), datatype=rdflib.XSD.string)))
                    if 'Start' in timeEntry and 'End' in timeEntry and timeEntry['Start'] == timeEntry['End']:
                        nanopub.assertion.add((tl_term, sio.hasValue, self.rdflibConverter(str(timeEntry['Start']))))
                    if 'Start' in timeEntry:
                        start_time = rdflib.BNode()
                        nanopub.assertion.add((start_time, sio.hasValue, self.rdflibConverter(str(timeEntry['Start']))))
                        nanopub.assertion.add((tl_term, sio.hasStartTime, start_time))
                    if 'End' in timeEntry:
                        end_time = rdflib.BNode()
                        nanopub.assertion.add((end_time, sio.hasValue, self.rdflibConverter(str(timeEntry['End']))))
                        nanopub.assertion.add((tl_term, sio.hasEndTime, end_time))
                    if 'Unit' in timeEntry:
                        nanopub.assertion.add(
                            (tl_term, sio.hasUnit, self.rdflibConverter(self.codeMapper(timeEntry['Unit']))))
                    if 'inRelationTo' in timeEntry:
                        nanopub.assertion.add((tl_term, sio.inRelationTo, self.rdflibConverter(
                            self.convertVirtualToKGEntry(timeEntry['inRelationTo']))))
                nanopub.provenance.add((tl_term, prov.generatedAtTime, rdflib.Literal(
                    "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year, datetime.utcnow().month,
                                                 datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(
                        datetime.utcnow().hour, datetime.utcnow().minute, datetime.utcnow().second) + "Z",
                    datatype=rdflib.XSD.dateTime)))

    def writeExplicitEntryNano(self, nanopub):
        for item in self.explicit_entry_list:
            explicit_entry_tuple = {}
            term = rdflib.term.URIRef(self.prefixes[self.kb] + str(
                item.Column.replace(" ", "_").replace(",", "").replace("(", "").replace(")", "").replace("/",
                                                                                                         "-").replace(
                    "\\", "-")))
            nanopub.assertion.add((term, rdflib.RDF.type, rdflib.OWL.Class))
            if pd.notnull(item.Attribute):
                if ',' in item.Attribute:
                    attributes = self.parseString(item.Attribute, ',')
                    for attribute in attributes:
                        nanopub.assertion.add(
                            (term, rdflib.RDFS.subClassOf, self.rdflibConverter(self.codeMapper(attribute))))
                else:
                    nanopub.assertion.add(
                        (term, rdflib.RDFS.subClassOf, self.rdflibConverter(self.codeMapper(item.Attribute))))
                explicit_entry_tuple["Column"] = item.Column
                explicit_entry_tuple["Attribute"] = self.codeMapper(item.Attribute)
            elif pd.notnull(item.Entity):
                if ',' in item.Entity:
                    entities = self.parseString(item.Entity, ',')
                    for entity in entities:
                        nanopub.assertion.add(
                            (term, rdflib.RDFS.subClassOf, self.rdflibConverter(self.codeMapper(entity))))
                else:
                    nanopub.assertion.add(
                        (term, rdflib.RDFS.subClassOf, self.rdflibConverter(self.codeMapper(item.Entity))))
                explicit_entry_tuple["Column"] = item.Column
                explicit_entry_tuple["Entity"] = self.codeMapper(item.Entity)
            else:
                nanopub.assertion.add((term, rdflib.RDFS.subClassOf, sio.Attribute))
                explicit_entry_tuple["Column"] = item.Column
                explicit_entry_tuple["Attribute"] = self.codeMapper("sio:Attribute")
                logging.warning("Warning: Explicit entry not assigned an Attribute or Entity value.")
            if pd.notnull(item.attributeOf):
                nanopub.assertion.add(
                    (term, sio.isAttributeOf, self.rdflibConverter(self.convertVirtualToKGEntry(item.attributeOf))))
                explicit_entry_tuple["isAttributeOf"] = self.convertVirtualToKGEntry(item.attributeOf)
            else:
                logging.warning("Warning: Explicit entry not assigned an isAttributeOf value.")
            if pd.notnull(item.Unit):
                nanopub.assertion.add(
                    (term, sio.hasUnit, self.rdflibConverter(self.convertVirtualToKGEntry(self.codeMapper(item.Unit)))))
                explicit_entry_tuple["Unit"] = self.convertVirtualToKGEntry(self.codeMapper(item.Unit))
            if pd.notnull(item.Time):
                nanopub.assertion.add(
                    (term, sio.existsAt, self.rdflibConverter(self.convertVirtualToKGEntry(item.Time))))
                explicit_entry_tuple["Time"] = item.Time
            if pd.notnull(item.inRelationTo):
                explicit_entry_tuple["inRelationTo"] = item.inRelationTo
                # If there is a value in the Relation column but not the Role column ...
                if (pd.notnull(item.Relation)) and (pd.isnull(item.Role)):
                    nanopub.assertion.add((term, self.rdflibConverter(item.Relation),
                                           self.rdflibConverter(self.convertVirtualToKGEntry(item.inRelationTo))))
                    explicit_entry_tuple["Relation"] = item.Relation
                # If there is a value in the Role column but not the Relation column ...
                elif (pd.isnull(item.Relation)) and (pd.notnull(item.Role)):
                    role = rdflib.BNode()
                    nanopub.assertion.add(
                        (role, rdflib.RDF.type, self.rdflibConverter(self.convertVirtualToKGEntry(item.Role))))
                    nanopub.assertion.add(
                        (role, sio.inRelationTo, self.rdflibConverter(self.convertVirtualToKGEntry(item.inRelationTo))))
                    nanopub.assertion.add((term, sio.hasRole, role))
                    explicit_entry_tuple["Role"] = item.Role
                # If there is a value in the Role and Relation columns ...
                elif (pd.notnull(item.Relation)) and (pd.notnull(item.Role)):
                    nanopub.assertion.add(
                        (term, sio.hasRole, self.rdflibConverter(self.convertVirtualToKGEntry(item.Role))))
                    nanopub.assertion.add((term, self.rdflibConverter(item.Relation),
                                           self.rdflibConverter(self.convertVirtualToKGEntry(item.inRelationTo))))
                    explicit_entry_tuple["Relation"] = item.Relation
                    explicit_entry_tuple["Role"] = item.Role
            if ("Label" in item and pd.notnull(item.Label)):
                nanopub.assertion.add((term, rdflib.RDFS.label, self.rdflibConverter(item.Label)))
                explicit_entry_tuple["Label"] = item.Label
            if ("Comment" in item and pd.notnull(item.Comment)):
                nanopub.assertion.add((term, rdflib.RDFS.comment, self.rdflibConverter(item.Comment)))
                explicit_entry_tuple["Comment"] = item.Comment
            nanopub.provenance.add((term, prov.generatedAtTime, rdflib.Literal(
                "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year, datetime.utcnow().month,
                                             datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(
                    datetime.utcnow().hour, datetime.utcnow().minute, datetime.utcnow().second) + "Z",
                datatype=rdflib.XSD.dateTime)))
            if pd.notnull(item.wasDerivedFrom):
                if ',' in item.wasDerivedFrom:
                    derivedFromTerms = self.parseString(item.wasDerivedFrom, ',')
                    for derivedFromTerm in derivedFromTerms:
                        nanopub.provenance.add((term, prov.wasDerivedFrom,
                                                self.rdflibConverter(self.convertVirtualToKGEntry(derivedFromTerm))))
                else:
                    nanopub.provenance.add((term, prov.wasDerivedFrom,
                                            self.rdflibConverter(self.convertVirtualToKGEntry(item.wasDerivedFrom))))
                explicit_entry_tuple["wasDerivedFrom"] = item.wasDerivedFrom
            if pd.notnull(item.wasGeneratedBy):
                if ',' in item.wasGeneratedBy:
                    generatedByTerms = self.parseString(item.wasGeneratedBy, ',')
                    for generatedByTerm in generatedByTerms:
                        nanopub.provenance.add((term, prov.wasGeneratedBy,
                                                self.rdflibConverter(self.convertVirtualToKGEntry(generatedByTerm))))
                else:
                    nanopub.provenance.add((term, prov.wasGeneratedBy,
                                            self.rdflibConverter(self.convertVirtualToKGEntry(item.wasGeneratedBy))))
                explicit_entry_tuple["wasGeneratedBy"] = item.wasGeneratedBy

            self.explicit_entry_tuples.append(explicit_entry_tuple)

    def writeVirtualEntry(self, nanopub, vref_list, v_column, index):
        term = self.rdflibConverter(self.convertVirtualToKGEntry(v_column, index))
        try:
            if self.timeline_fn is not None:
                if v_column in self.timeline_tuple:
                    nanopub.assertion.add(
                        (term, rdflib.RDF.type, self.rdflibConverter(self.convertVirtualToKGEntry(v_column))))

                    for timeEntry in self.timeline_tuple[v_column]:
                        if 'Type' in timeEntry:
                            nanopub.assertion.add((term, rdflib.RDF.type, self.rdflibConverter(timeEntry['Type'])))
                        if 'Label' in timeEntry:
                            nanopub.assertion.add((term, rdflib.RDFS.label,
                                                   rdflib.Literal(str(timeEntry['Label']), datatype=rdflib.XSD.string)))
                        if 'Start' in timeEntry and 'End' in timeEntry and timeEntry['Start'] == timeEntry['End']:
                            nanopub.assertion.add((term, sio.hasValue, self.rdflibConverter(str(timeEntry['Start']))))
                        if 'Start' in timeEntry:
                            start_time = rdflib.BNode()
                            nanopub.assertion.add(
                                (start_time, sio.hasValue, self.rdflibConverter(str(timeEntry['Start']))))
                            nanopub.assertion.add((term, sio.hasStartTime, start_time))
                        if 'End' in timeEntry:
                            end_time = rdflib.BNode()
                            nanopub.assertion.add((end_time, sio.hasValue, self.rdflibConverter(str(timeEntry['End']))))
                            nanopub.assertion.add((term, sio.hasEndTime, end_time))
                        if 'Unit' in timeEntry:
                            nanopub.assertion.add(
                                (term, sio.hasUnit, self.rdflibConverter(self.codeMapper(timeEntry['Unit']))))
                        if 'inRelationTo' in timeEntry:
                            nanopub.assertion.add((term, sio.inRelationTo, self.rdflibConverter(
                                self.convertVirtualToKGEntry(timeEntry['inRelationTo']))))
                            if self.checkVirtual(timeEntry['inRelationTo']) and timeEntry[
                                'inRelationTo'] not in vref_list:
                                vref_list.append(timeEntry['inRelationTo'])
            for v_tuple in self.virtual_entry_tuples:
                if v_tuple["Column"] == v_column:
                    if "Study" in v_tuple:
                        continue
                    else:
                        v_term = rdflib.term.URIRef(self.prefixes[self.kb] + str(v_tuple["Column"][2:]) + "-" + index)
                        nanopub.assertion.add((v_term, rdflib.RDF.type,
                                               rdflib.term.URIRef(self.prefixes[self.kb] + str(v_tuple["Column"][2:]))))
                        if "Entity" in v_tuple:
                            if ',' in v_tuple["Entity"]:
                                entities = self.parseString(v_tuple["Entity"], ',')
                                for entity in entities:
                                    nanopub.assertion.add(
                                        (term, rdflib.RDF.type, self.rdflibConverter(self.codeMapper(entity))))
                            else:
                                nanopub.assertion.add(
                                    (term, rdflib.RDF.type, self.rdflibConverter(self.codeMapper(v_tuple["Entity"]))))
                        if "Attribute" in v_tuple:
                            if ',' in v_tuple["Attribute"]:
                                attributes = self.parseString(v_tuple["Attribute"], ',')
                                for attribute in attributes:
                                    nanopub.assertion.add(
                                        (term, rdflib.RDF.type, self.rdflibConverter(self.codeMapper(attribute))))
                            else:
                                nanopub.assertion.add((term, rdflib.RDF.type,
                                                       self.rdflibConverter(self.codeMapper(v_tuple["Attribute"]))))
                        if "Subject" in v_tuple:
                            nanopub.assertion.add((term, sio.hasIdentifier, rdflib.term.URIRef(
                                self.prefixes[self.kb] + v_tuple["Subject"] + "-" + index)))
                        if "inRelationTo" in v_tuple:
                            if ("Role" in v_tuple) and ("Relation" not in v_tuple):
                                role = rdflib.BNode()
                                nanopub.assertion.add((role, rdflib.RDF.type, self.rdflibConverter(
                                    self.convertVirtualToKGEntry(v_tuple["Role"], index))))
                                nanopub.assertion.add((role, sio.inRelationTo, self.rdflibConverter(
                                    self.convertVirtualToKGEntry(v_tuple["inRelationTo"], index))))
                                nanopub.assertion.add((term, sio.hasRole, role))
                            elif ("Role" not in v_tuple) and ("Relation" in v_tuple):
                                nanopub.assertion.add((term, self.rdflibConverter(v_tuple["Relation"]),
                                                       self.rdflibConverter(
                                                           self.convertVirtualToKGEntry(v_tuple["inRelationTo"],
                                                                                        index))))
                            elif ("Role" not in v_tuple) and ("Relation" not in v_tuple):
                                nanopub.assertion.add((term, sio.inRelationTo, self.rdflibConverter(
                                    self.convertVirtualToKGEntry(v_tuple["inRelationTo"], index))))
                        nanopub.provenance.add((term, prov.generatedAtTime, rdflib.Literal(
                            "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year, datetime.utcnow().month,
                                                         datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(
                                datetime.utcnow().hour, datetime.utcnow().minute, datetime.utcnow().second) + "Z",
                            datatype=rdflib.XSD.dateTime)))

                        if "wasGeneratedBy" in v_tuple:
                            if ',' in v_tuple["wasGeneratedBy"]:
                                generatedByTerms = self.parseString(v_tuple["wasGeneratedBy"], ',')
                                for generatedByTerm in generatedByTerms:
                                    nanopub.provenance.add((term, prov.wasGeneratedBy, self.rdflibConverter(
                                        self.convertVirtualToKGEntry(generatedByTerm, index))))
                                    if self.checkVirtual(generatedByTerm) and generatedByTerm not in vref_list:
                                        vref_list.append(generatedByTerm)
                            else:
                                nanopub.provenance.add((term, prov.wasGeneratedBy, self.rdflibConverter(
                                    self.convertVirtualToKGEntry(v_tuple["wasGeneratedBy"], index))))
                                if self.checkVirtual(v_tuple["wasGeneratedBy"]) and v_tuple[
                                    "wasGeneratedBy"] not in vref_list:
                                    vref_list.append(v_tuple["wasGeneratedBy"])
                        if "wasDerivedFrom" in v_tuple:
                            if ',' in v_tuple["wasDerivedFrom"]:
                                derivedFromTerms = self.parseString(v_tuple["wasDerivedFrom"], ',')
                                for derivedFromTerm in derivedFromTerms:
                                    nanopub.provenance.add((term, prov.wasDerivedFrom, self.rdflibConverter(
                                        self.convertVirtualToKGEntry(derivedFromTerm, index))))
                                    if self.checkVirtual(derivedFromTerm) and derivedFromTerm not in vref_list:
                                        vref_list.append(derivedFromTerm)
                            else:
                                nanopub.provenance.add((term, prov.wasDerivedFrom, self.rdflibConverter(
                                    self.convertVirtualToKGEntry(v_tuple["wasDerivedFrom"], index))))
                                if self.checkVirtual(v_tuple["wasDerivedFrom"]) and v_tuple[
                                    "wasDerivedFrom"] not in vref_list:
                                    vref_list.append(v_tuple["wasDerivedFrom"])
            return vref_list

        except Exception as e:
            logging.warning("Warning: Unable to create virtual entry:")
            if hasattr(e, 'message'):
                logging.warning(e.message)
            else:
                logging.warning(e)

    def interpretData(self, nanopub):
        if self.data_fn is not None:
            try:
                data_file = pd.read_csv(self.data_fn, dtype=object)
            except Exception as e:
                logging.exception("Error: The specified Data file does not exist: ")
                if hasattr(e, 'message'):
                    logging.exception(e.message)
                else:
                    logging.exception(e)
                sys.exit(1)
        try:
            col_headers = list(data_file.columns.values)
            try:
                for a_tuple in self.explicit_entry_tuples:
                    if "Attribute" in a_tuple:
                        if ((a_tuple["Attribute"] == "hasco:originalID") or (a_tuple["Attribute"] == "sio:Identifier")):
                            if a_tuple["Column"] in col_headers:
                                for v_tuple in self.virtual_entry_tuples:
                                    if "isAttributeOf" in a_tuple:
                                        if a_tuple["isAttributeOf"] == v_tuple["Column"]:
                                            v_tuple["Subject"] = a_tuple["Column"].replace(" ", "_").replace(",",
                                                                                                             "").replace(
                                                "(", "").replace(")", "").replace("/", "-").replace("\\", "-")
            except Exception as e:
                logging.exception("Error: Something went wrong when processing column headers:")
                if hasattr(e, 'message'):
                    logging.exception(e.message)
                else:
                    logging.exception(e)
            for row in data_file.itertuples():
                id_string = ''
                for element in row:
                    id_string += str(element)
                identifierString = hashlib.md5(id_string).hexdigest()
                try:
                    vref_list = []
                    for a_tuple in self.explicit_entry_tuples:
                        if a_tuple["Column"] in col_headers:
                            try:
                                try:
                                    term = rdflib.term.URIRef(self.prefixes[self.kb] + str(
                                        a_tuple["Column"].replace(" ", "_").replace(",", "").replace("(", "").replace(
                                            ")", "").replace("/", "-").replace("\\", "-")) + "-" + identifierString)
                                    nanopub.assertion.add((term, rdflib.RDF.type, rdflib.term.URIRef(
                                        self.prefixes[self.kb] + str(
                                            a_tuple["Column"].replace(" ", "_").replace(",", "").replace("(",
                                                                                                         "").replace(
                                                ")", "").replace("/", "-").replace("\\", "-")))))
                                    print(term)
                                    if "Attribute" in a_tuple:
                                        if ',' in a_tuple["Attribute"]:
                                            attributes = self.parseString(a_tuple["Attribute"], ',')
                                            for attribute in attributes:
                                                nanopub.assertion.add((term, rdflib.RDF.type, self.rdflibConverter(
                                                    self.codeMapper(attribute))))
                                        else:
                                            nanopub.assertion.add((term, rdflib.RDF.type, self.rdflibConverter(
                                                self.codeMapper(a_tuple["Attribute"]))))
                                    if "Entity" in a_tuple:
                                        if ',' in a_tuple["Entity"]:
                                            entities = self.parseString(a_tuple["Entity"], ',')
                                            for entity in entities:
                                                nanopub.assertion.add((term, rdflib.RDF.type,
                                                                       self.rdflibConverter(self.codeMapper(entity))))
                                        else:
                                            nanopub.assertion.add((term, rdflib.RDF.type, self.rdflibConverter(
                                                self.codeMapper(a_tuple["Entity"]))))
                                    if "isAttributeOf" in a_tuple:
                                        nanopub.assertion.add((term, sio.isAttributeOf, self.rdflibConverter(
                                            self.convertVirtualToKGEntry(a_tuple["isAttributeOf"], identifierString))))
                                        if self.checkVirtual(a_tuple["isAttributeOf"]):
                                            if a_tuple["isAttributeOf"] not in vref_list:
                                                vref_list.append(a_tuple["isAttributeOf"])
                                    if "Unit" in a_tuple:
                                        nanopub.assertion.add(
                                            (term, sio.hasUnit, self.rdflibConverter(self.codeMapper(a_tuple["Unit"]))))
                                    if "Time" in a_tuple:
                                        nanopub.assertion.add((term, sio.existsAt, self.rdflibConverter(
                                            self.convertVirtualToKGEntry(a_tuple["Time"], identifierString))))
                                        if self.checkVirtual(a_tuple["Time"]):
                                            if a_tuple["Time"] not in vref_list:
                                                vref_list.append(a_tuple["Time"])
                                    if "Label" in a_tuple:
                                        nanopub.assertion.add(
                                            (term, rdflib.RDFS.label, self.rdflibConverter(a_tuple["Label"])))
                                    if "Comment" in a_tuple:
                                        nanopub.assertion.add(
                                            (term, rdflib.RDFS.comment, self.rdflibConverter(a_tuple["Comment"])))

                                    if "inRelationTo" in a_tuple:
                                        if ("Role" in a_tuple) and ("Relation" not in a_tuple):
                                            role = rdflib.BNode()
                                            nanopub.assertion.add((role, rdflib.RDF.type, self.rdflibConverter(
                                                self.convertVirtualToKGEntry(a_tuple["Role"], identifierString))))
                                            nanopub.assertion.add((role, sio.inRelationTo, self.rdflibConverter(
                                                self.convertVirtualToKGEntry(a_tuple["inRelationTo"],
                                                                             identifierString))))
                                            nanopub.assertion.add((term, sio.hasRole, role))
                                        elif ("Role" not in a_tuple) and ("Relation" in a_tuple):
                                            nanopub.assertion.add((term, self.rdflibConverter(a_tuple["Relation"]),
                                                                   self.rdflibConverter(self.convertVirtualToKGEntry(
                                                                       a_tuple["inRelationTo"], identifierString))))
                                        elif ("Role" not in a_tuple) and ("Relation" not in a_tuple):
                                            nanopub.assertion.add((term, sio.inRelationTo, self.rdflibConverter(
                                                self.convertVirtualToKGEntry(a_tuple["inRelationTo"],
                                                                             identifierString))))
                                except Exception as e:
                                    logging.exception("Error: something went wrong for initial assertions:")
                                    if hasattr(e, 'message'):
                                        print(e.message)
                                    else:
                                        print(e)
                                    sys.exit(1)
                                try:
                                    if row[col_headers.index(a_tuple["Column"]) + 1] != "":
                                        if self.cb_fn is not None:
                                            if a_tuple["Column"] in self.cb_tuple:
                                                for tuple_row in self.cb_tuple[a_tuple["Column"]]:
                                                    if ("Code" in tuple_row) and (str(tuple_row['Code']) == str(
                                                            row[col_headers.index(a_tuple["Column"]) + 1])):
                                                        if ("Class" in tuple_row) and (tuple_row['Class'] != ""):
                                                            if ',' in tuple_row['Class']:
                                                                classTerms = self.parseString(tuple_row['Class'], ',')
                                                                for classTerm in classTerms:
                                                                    nanopub.assertion.add((term, rdflib.RDF.type,
                                                                                           self.rdflibConverter(
                                                                                               self.codeMapper(
                                                                                                   classTerm))))
                                                            else:
                                                                nanopub.assertion.add((term, rdflib.RDF.type,
                                                                                       self.rdflibConverter(
                                                                                           self.codeMapper(
                                                                                               tuple_row['Class']))))
                                                        if ("Resource" in tuple_row) and (tuple_row['Resource'] != ""):
                                                            if ',' in tuple_row['Resource']:
                                                                resourceTerms = self.parseString(tuple_row['Resource'],
                                                                                                 ',')
                                                                for resourceTerm in resourceTerms:
                                                                    nanopub.assertion.add((term, rdflib.OWL.sameAs,
                                                                                           self.rdflibConverter(
                                                                                               self.convertVirtualToKGEntry(
                                                                                                   self.codeMapper(
                                                                                                       resourceTerm)))))
                                                            else:
                                                                nanopub.assertion.add((term, rdflib.OWL.sameAs,
                                                                                       self.rdflibConverter(
                                                                                           self.convertVirtualToKGEntry(
                                                                                               self.codeMapper(
                                                                                                   tuple_row[
                                                                                                       'Resource'])))))
                                                        if ("Label" in tuple_row) and (tuple_row['Label'] != ""):
                                                            nanopub.assertion.add((term, rdflib.RDFS.label,
                                                                                   self.rdflibConverter(
                                                                                       tuple_row["Label"])))
                                        try:
                                            if str(row[col_headers.index(a_tuple["Column"]) + 1]) == "nan":
                                                pass
                                            elif str(row[col_headers.index(a_tuple["Column"]) + 1]).isdigit():
                                                nanopub.assertion.add((term, sio.hasValue, rdflib.Literal(
                                                    str(row[col_headers.index(a_tuple["Column"]) + 1]),
                                                    datatype=rdflib.XSD.integer)))
                                            elif self.isfloat(str(row[col_headers.index(a_tuple["Column"]) + 1])):
                                                nanopub.assertion.add((term, sio.hasValue, rdflib.Literal(
                                                    str(row[col_headers.index(a_tuple["Column"]) + 1]),
                                                    datatype=rdflib.XSD.float)))
                                            else:
                                                nanopub.assertion.add((term, sio.hasValue, rdflib.Literal(
                                                    str(row[col_headers.index(a_tuple["Column"]) + 1]),
                                                    datatype=rdflib.XSD.string)))
                                        except Exception as e:
                                            logging.warning("Warning: Unable to add assertion: %s",
                                                            row[col_headers.index(a_tuple["Column"]) + 1] + ":")
                                            if hasattr(e, 'message'):
                                                logging.warning(e.message)
                                            else:
                                                logging.warning(e)
                                except Exception as e:
                                    logging.exception("Error: Something went wrong when asserting data value: %s",
                                                      row[col_headers.index(a_tuple["Column"]) + 1] + ":")
                                    if hasattr(e, 'message'):
                                        logging.exception(e.message)
                                    else:
                                        logging.exception(e)
                                try:
                                    nanopub.provenance.add((term, prov.generatedAtTime, rdflib.Literal(
                                        "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year, datetime.utcnow().month,
                                                                     datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(
                                            datetime.utcnow().hour, datetime.utcnow().minute,
                                            datetime.utcnow().second) + "Z", datatype=rdflib.XSD.dateTime)))
                                    if "wasDerivedFrom" in a_tuple:
                                        if ',' in a_tuple["wasDerivedFrom"]:
                                            derivedFromTerms = self.parseString(a_tuple["wasDerivedFrom"], ',')
                                            for derivedFromTerm in derivedFromTerms:
                                                nanopub.provenance.add((term, prov.wasDerivedFrom, self.rdflibConverter(
                                                    self.convertVirtualToKGEntry(derivedFromTerm, identifierString))))
                                                if self.checkVirtual(derivedFromTerm):
                                                    if derivedFromTerm not in vref_list:
                                                        vref_list.append(derivedFromTerm)
                                        else:
                                            nanopub.provenance.add((term, prov.wasDerivedFrom, self.rdflibConverter(
                                                self.convertVirtualToKGEntry(a_tuple["wasDerivedFrom"],
                                                                             identifierString))))
                                        if self.checkVirtual(a_tuple["wasDerivedFrom"]):
                                            if a_tuple["wasDerivedFrom"] not in vref_list:
                                                vref_list.append(a_tuple["wasDerivedFrom"])
                                    if "wasGeneratedBy" in a_tuple:
                                        if ',' in a_tuple["wasGeneratedBy"]:
                                            generatedByTerms = self.parseString(a_tuple["wasGeneratedBy"], ',')
                                            for generatedByTerm in generatedByTerms:
                                                nanopub.provenance.add((term, prov.wasGeneratedBy, self.rdflibConverter(
                                                    self.convertVirtualToKGEntry(generatedByTerm, identifierString))))
                                                if self.checkVirtual(generatedByTerm):
                                                    if generatedByTerm not in vref_list:
                                                        vref_list.append(generatedByTerm)
                                        else:
                                            nanopub.provenance.add((term, prov.wasGeneratedBy, self.rdflibConverter(
                                                self.convertVirtualToKGEntry(a_tuple["wasGeneratedBy"],
                                                                             identifierString))))
                                        if self.checkVirtual(a_tuple["wasGeneratedBy"]):
                                            if a_tuple["wasGeneratedBy"] not in vref_list:
                                                vref_list.append(a_tuple["wasGeneratedBy"])
                                except Exception as e:
                                    logging.exception("Error: Something went wrong when adding provenance:")
                                    if hasattr(e, 'message'):
                                        print(e.message)
                                    else:
                                        print(e)
                            except Exception as e:
                                logging.warning("Warning: Unable to process tuple %s", a_tuple.__str__() + ":")
                                if hasattr(e, 'message'):
                                    print(e.message)
                                else:
                                    print(e)
                    try:
                        for vref in vref_list:
                            vref_list = self.writeVirtualEntry(nanopub, vref_list, vref, identifierString)
                    except Exception as e:
                        logging.warning("Warning: Something went writing vref entries:")
                        if hasattr(e, 'message'):
                            print(e.message)
                        else:
                            print(e)
                except Exception as e:
                    logging.exception("Error: Something went wrong when processing explicit tuples:")
                    if hasattr(e, 'message'):
                        print(e.message)
                    else:
                        print(e)
                    sys.exit(1)
        except Exception as e:
            logging.warning("Warning: Unable to process Data file:")
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
