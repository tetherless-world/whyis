#import urllib2
import csv
import sys
import re
from datetime import datetime
import time
import pandas as pd
import configparser
import hashlib
import os
import rdflib
import logging
logging.getLogger().disabled = True
if sys.version_info[0] == 3:
    from importlib import reload
reload(sys)
if sys.version_info[0] == 2:
    sys.setdefaultencoding('utf8')

whyis = rdflib.Namespace('http://vocab.rpi.edu/whyis/')
np = rdflib.Namespace("http://www.nanopub.org/nschema#")
prov = rdflib.Namespace("http://www.w3.org/ns/prov#")
dc = rdflib.Namespace("http://purl.org/dc/terms/")
sio = rdflib.Namespace("http://semanticscience.org/resource/")
setl = rdflib.Namespace("http://purl.org/twc/vocab/setl/")
pv = rdflib.Namespace("http://purl.org/net/provenance/ns#")
skos = rdflib.Namespace("http://www.w3.org/2008/05/skos#")
rdfs = rdflib.RDFS
rdf = rdflib.RDF
owl = rdflib.OWL
xsd = rdflib.XSD

def parseString(input_string, delim) :
    my_list = input_string.split(delim)
    for i in range(0,len(my_list)) :
        my_list[i] = my_list[i].strip()
    return my_list

def codeMapper(input_word) :
    unitVal = input_word
    for unit_label in unit_label_list :
        if (unit_label == input_word) :
            unit_index = unit_label_list.index(unit_label)
            unitVal = unit_uri_list[unit_index]
    for unit_code in unit_code_list :
        if (unit_code == input_word) :
            unit_index = unit_code_list.index(unit_code)
            unitVal = unit_uri_list[unit_index]
    return unitVal    

def convertImplicitToKGEntry(*args) :
    if (args[0][:2] == "??") :
        if (studyRef is not None ) :
            if (args[0]==studyRef) :
                return "<" + prefixes[kb] + args[0][2:] + ">"
        if (len(args) == 2) :
            return "<" + prefixes[kb] + args[0][2:] + "-" + args[1] + ">"
        else : 
            return "<" + prefixes[kb] + args[0][2:] + ">"
    elif ('http:' not in args[0]) or ('https:' not in args[0]) :
        # Check for entry in column list
        for item in explicit_entry_list :
            if args[0] == item.Column :
                if (len(args) == 2) :
                    return "<" + prefixes[kb] + args[0].replace(" ","_").replace(",","").replace("(","").replace(")","").replace("/","-").replace("\\","-") + "-" + args[1] + ">"
                else :
                    return "<" + prefixes[kb] + args[0].replace(" ","_").replace(",","").replace("(","").replace(")","").replace("/","-").replace("\\","-") + ">"
        #return '"' + args[0] + "\"^^xsd:string"
        return args[0]
    else :
        return args[0]

def checkImplicit(input_word) :
    try:
        if (input_word[:2] == "??") :
            return True
        else :
            return False
    except Exception as e:
        print("Something went wrong in checkImplicit()" + str(e))
        sys.exit(1)

def isfloat(term):
    try:
        float(term)
        return True
    except ValueError:
        return False

def isURI(term):
    try:
        if any(c in term for c in ("http://","https://")) :
            return True
        else:
            return False
    except ValueError:
        return False

def isSchemaVar(term) :
    for entry in explicit_entry_list :
        if term == entry[1] :
            return True
    return False

def assignVID(implicit_entry_tuples,timeline_tuple,a_tuple,column, npubIdentifier) :
    v_id = npubIdentifier
    for v_tuple in implicit_entry_tuples : # referenced in implicit list
        if v_tuple["Column"] == a_tuple[column]:
            v_id = hashlib.md5((str(v_tuple) + str(npubIdentifier)).encode("utf-8")).hexdigest()
    if v_id == None : # maybe it's referenced in the timeline
        for t_tuple in timeline_tuple:
            if t_tuple["Column"] == a_tuple[column]:
                #print("Got here")
                v_id = hashlib.md5((str(t_tuple) + str(npubIdentifier)).encode("utf-8")).hexdigest()
    if v_id == npubIdentifier : # if it's not in implicit list or timeline
        print("Warning, " + column + " ID assigned to nanopub ID:" + a_tuple[column])
    return v_id

def assignTerm(col_headers, column, implicit_entry_tuples, a_tuple, row, v_id) :
    termURI = None
    for v_tuple in implicit_entry_tuples : # referenced in implicit list
        if v_tuple["Column"] == a_tuple[column]:
            if "Template" in v_tuple :
                template_term = extractTemplate(col_headers,row,v_tuple["Template"])
                termURI = "<" + prefixes[kb] + template_term + ">"
    if termURI is None :
        termURI = convertImplicitToKGEntry(a_tuple[column],v_id)
    return termURI



'''def processPrefixes(output_file,query_file):
    if 'prefixes' in config['Prefixes']:
        prefix_fn = config['Prefixes']['prefixes']
    else:
        prefix_fn="prefixes.txt"
    prefix_file = open(prefix_fn,"r")
    prefixes = prefix_file.readlines()
    for prefix in prefixes :
        #print(prefix.find(">"))
        output_file.write(prefix)
        query_file.write(prefix[1:prefix.find(">")+1])
        query_file.write("\n")
    prefix_file.close()
    output_file.write("\n")'''

def checkTemplate(term) :
    if "{" in term and "}" in term:
        return True
    return False

def extractTemplate(col_headers,row,term) :
    while checkTemplate(term) :
        open_index = term.find("{")
        close_index = term.find("}")
        key = term[open_index+1:close_index]
        term = term[:open_index] + str(row[col_headers.index(key)+1]) + term[close_index+1:]
    return term

def extractExplicitTerm(col_headers,row,term) : # need to write this function
    while checkTemplate(term) :
        open_index = term.find("{")
        close_index = term.find("}")
        key = term[open_index+1:close_index]
        if isSchemaVar(key) :
            for entry in explicit_entry_list :
                if entry.Column == key :
                    if pd.notnull(entry.Template) :
                        term = extractTemplate(col_headers,row,entry.Template)
                    else :
                        typeString = ""
                        if pd.notnull(entry.Attribute) :
                            typeString += str(entry.Attribute)
                        if pd.notnull(entry.Entity) :
                            typeString += str(entry.Entity)
                        if pd.notnull(entry.Label) :
                            typeString += str(entry.Label)
                        if pd.notnull(entry.Unit) :
                            typeString += str(entry.Unit)
                        if pd.notnull(entry.Time) :
                            typeString += str(entry.Time)
                        if pd.notnull(entry.inRelationTo) :
                            typeString += str(entry.inRelationTo)
                        if pd.notnull(entry.wasGeneratedBy) :
                            typeString += str(entry.wasGeneratedBy)
                        if pd.notnull(entry.wasDerivedFrom) :
                            typeString += str(entry.wasDerivedFrom)
                        identifierKey = hashlib.md5((str(row[col_headers.index(key)+1])+typeString).encode("utf-8")).hexdigest()
                        term = entry.Column.replace(" ","_").replace(",","").replace("(","").replace(")","").replace("/","-").replace("\\","-") + "-" + identifierKey
                        #return extractTemplate(col_headers,row,entry.Template)
        else : # What does it mean for a template reference to not be a schema variable?
            print("Warning: Template reference " + term + " is not be a schema variable")
            term = term[:open_index] + str(row[col_headers.index(key)+1]) + term[close_index+1:] # Needs updating probably, at least checking
    return term


def writeClassAttributeOrEntity(item, term, input_tuple, assertionString, whereString, swrlString) :
    if (pd.notnull(item.Entity)) and (pd.isnull(item.Attribute)) :
        if ',' in item.Entity :
            entities = parseString(item.Entity,',')
            for entity in entities :
                assertionString += " ;\n        <" + rdfs.subClassOf + ">    " + codeMapper(entity)
                whereString += codeMapper(entity) + " "
                swrlString += codeMapper(entity) + "(" + term + ") ^ "
                if entities.index(entity) + 1 != len(entities) :
                    whereString += ", "
        else :
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    " + codeMapper(item.Entity)
            whereString += codeMapper(item.Entity) + " "
            swrlString += codeMapper(item.Entity) + "(" + term + ") ^ "
        input_tuple["Entity"]=codeMapper(item.Entity)
        if (input_tuple["Entity"] == "hasco:Study") :
            global studyRef
            studyRef = item.Column
            input_tuple["Study"] = item.Column
    elif (pd.isnull(item.Entity)) and (pd.notnull(item.Attribute)) :
        if ',' in item.Attribute :
            attributes = parseString(item.Attribute,',')
            for attribute in attributes :
                assertionString += " ;\n        <" + rdfs.subClassOf + ">    " + codeMapper(attribute)
                whereString += codeMapper(attribute) + " "
                swrlString += codeMapper(attribute) + "(" + term + ") ^ "
                if attributes.index(attribute) + 1 != len(attributes) :
                    whereString += ", "
        else :
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    " + codeMapper(item.Attribute)
            whereString += codeMapper(item.Attribute) + " "
            swrlString += codeMapper(item.Attribute) + "(" + term + ") ^ "
        input_tuple["Attribute"]=codeMapper(item.Attribute)
    else :
        print("Warning: Entry not assigned an Entity or Attribute value, or was assigned both.")
        input_tuple["Attribute"]=codeMapper("sio:Attribute")
        assertionString += " ;\n        <" + rdfs.subClassOf + ">    sio:Attribute"
        whereString += "sio:Attribute "
        swrlString += "sio:Attribute(" + term + ") ^ "
    return [input_tuple, assertionString, whereString, swrlString]

def writeClassAttributeOf(item, term, input_tuple, assertionString, whereString, swrlString) :
    if (pd.notnull(item.attributeOf)) :
        if checkTemplate(item.attributeOf) :
            open_index = item.attributeOf.find("{")
            close_index = item.attributeOf.find("}")
            key = item.attributeOf[open_index+1:close_index]
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.allValuesFrom + ">    " + convertImplicitToKGEntry(key) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["attributeOf"] + "> ]" 
            #assertionString += " ;\n        <" + properties_tuple["attributeOf"] + ">    " + convertImplicitToKGEntry(key)
            whereString += " ;\n    <" + properties_tuple["attributeOf"] + ">    ?" +  key.lower() + "_E"
            swrlString += properties_tuple["attributeOf"] + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
        else :
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.allValuesFrom + ">    " + convertImplicitToKGEntry(item.attributeOf) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["attributeOf"] + "> ]" 
            #assertionString += " ;\n        <" + properties_tuple["attributeOf"] + ">    " + convertImplicitToKGEntry(item.attributeOf)
            whereString += " ;\n    <" + properties_tuple["attributeOf"] + ">    " +  [item.attributeOf + " ",item.attributeOf[1:] + "_V "][checkImplicit(item.attributeOf)]
            swrlString += properties_tuple["attributeOf"] + "(" + term + " , " + [item.attributeOf,item.attributeOf[1:] + "_V"][checkImplicit(item.attributeOf)] + ") ^ "
        input_tuple["isAttributeOf"]=item.attributeOf
    return [input_tuple, assertionString, whereString, swrlString]

def writeClassUnit(item, term, input_tuple, assertionString, whereString, swrlString) :
    if (pd.notnull(item.Unit)) :
        if checkTemplate(item.Unit) :
            open_index = item.Unit.find("{")
            close_index = item.Unit.find("}")
            key = item.Unit[open_index+1:close_index]
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.hasValue + ">    " + convertImplicitToKGEntry(key) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Unit"] + "> ]" 
            #assertionString += " ;\n        <" + properties_tuple["Unit"] + ">    " + convertImplicitToKGEntry(key)
            whereString += " ;\n    <" + properties_tuple["Unit"] + ">    ?" +  key.lower() + "_E"
            swrlString += properties_tuple["Unit"] + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
            input_tuple["Unit"] = key
        else :
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.hasValue + ">    " + str(codeMapper(item.Unit)) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Unit"] + "> ]" 
            #assertionString += " ;\n        <" + properties_tuple["Unit"] + ">    " + str(codeMapper(item.Unit))
            whereString += " ;\n    <" + properties_tuple["Unit"] + ">    " + str(codeMapper(item.Unit))
            swrlString += properties_tuple["Unit"] + "(" + term + " , " + str(codeMapper(item.Unit)) + ") ^ "
            input_tuple["Unit"] = codeMapper(item.Unit)
    # Incorporate item.Format here
    return [input_tuple, assertionString, whereString, swrlString]

def writeClassTime(item, term, input_tuple, assertionString, whereString, swrlString) :
    if (pd.notnull(item.Time)) :
        if checkTemplate(item.Time) :
            open_index = item.Time.find("{")
            close_index = item.Time.find("}")
            key = item.Time[open_index+1:close_index]
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Time"] + "> ;\n                <" + owl.someValuesFrom + ">    " + convertImplicitToKGEntry(key) + " ]"
            #assertionString += " ;\n        <" + properties_tuple["Time"] + ">    " + convertImplicitToKGEntry(key)
            whereString += " ;\n    <" + properties_tuple["Time"] + ">    ?" +  key.lower() + "_E"
            swrlString += properties_tuple["Time"] + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
        else :
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Time"] + "> ;\n                <" + owl.someValuesFrom + ">    " + convertImplicitToKGEntry(item.Time) + " ]" 
            #assertionString += " ;\n        <" + properties_tuple["Time"] + ">    " + convertImplicitToKGEntry(item.Time)
            whereString += " ;\n    <" + properties_tuple["Time"] + ">     " + [item.Time + " ",item.Time[1:] + "_V "][checkImplicit(item.Time)]
            swrlString += properties_tuple["Time"] + "(" + term + " , " + [item.Time + " ",item.Time[1:] + "_V "][checkImplicit(item.Time)] + ") ^ "
        input_tuple["Time"]=item.Time
    return [input_tuple, assertionString, whereString, swrlString]

def writeClassRelation(item, term, input_tuple, assertionString, whereString, swrlString) :
    if (pd.notnull(item.inRelationTo)) :
        input_tuple["inRelationTo"]=item.inRelationTo
        key = item.inRelationTo
        if checkTemplate(item.inRelationTo) :
            open_index = item.inRelationTo.find("{")
            close_index = item.inRelationTo.find("}")
            key = item.inRelationTo[open_index+1:close_index]
        # If there is a value in the Relation column but not the Role column ...
        if (pd.notnull(item.Relation)) and (pd.isnull(item.Role)) :
            assertionString += " ;\n        " + item.Relation + " " + convertImplicitToKGEntry(key)
            if(isSchemaVar(key)):
                whereString += " ;\n    " + item.Relation + " ?" + key.lower() + "_E "
                swrlString += item.Relation + "(" + term + " , " + "?" + key.lower() + "_E) ^ "
            else :
                whereString += " ;\n    " + item.Relation + " " + [key + " ",key[1:] + "_V "][checkImplicit(key)]
                swrlString += item.Relation + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
            input_tuple["Relation"]=item.Relation
        # If there is a value in the Role column but not the Relation column ...
        elif (pd.isnull(item.Relation)) and (pd.notnull(item.Role)) :
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Role"] + "> ;\n                <" + owl.someValuesFrom + ">    [ <" + rdf.type + ">    <" + owl.Class + "> ;\n                    <" + owl.intersectionOf + "> ( \n                        [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                        <" + owl.allValuesFrom + "> " + [key,convertImplicitToKGEntry(key)][checkImplicit(key)] + " ;\n                        <" + owl.onProperty + "> <" + properties_tuple["inRelationTo"] + "> ] <" + item.Role + "> ) ]    ]" 
            #assertionString += " ;\n        <" + properties_tuple["Role"] + ">    [ <" + rdf.type + ">    " + item.Role + " ;\n            <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(key) + " ]"
            whereString += " ;\n    <" + properties_tuple["Role"] + ">    [ <" + rdf.type + "> " + item.Role + " ;\n      <" + properties_tuple["inRelationTo"] + ">    " + [key + " ",key[1:] + "_V "][checkImplicit(key)] + " ]"
            swrlString += "" # add appropriate swrl term
            input_tuple["Role"]=item.Role
        # If there is a value in the Role and Relation columns ...
        elif (pd.notnull(item.Relation)) and (pd.notnull(item.Role)) :
            input_tuple["Relation"]=item.Relation
            input_tuple["Role"]=item.Role
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Role"] + "> ;\n                <" + owl.someValuesFrom + ">    [ <" + rdf.type + ">    <" + owl.Class + "> ;\n                    <" + owl.intersectionOf + "> ( \n                        [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                        <" + owl.allValuesFrom + "> " + [key,convertImplicitToKGEntry(key)][checkImplicit(key)] + " ;\n                        <" + owl.onProperty + "> <" + item.Relation + "> ] <" + item.Role + "> ) ]    ]" 
            #assertionString += " ;\n        <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(key)
            if(isSchemaVar(key)):
                whereString += " ;\n    <" + properties_tuple["inRelationTo"] + ">    ?" + key.lower() + "_E "
                swrlString += "" # add appropriate swrl term
            else :
                whereString += " ;\n    <" + properties_tuple["inRelationTo"] + ">    " + [key + " ",key[1:] + "_V "][checkImplicit(key)]
                swrlString += "" # add appropriate swrl term
        elif (pd.isnull(item.Relation)) and (pd.isnull(item.Role)) :
            assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.allValuesFrom + ">    " + convertImplicitToKGEntry(key) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["inRelationTo"] + "> ]" 
            #assertionString += " ;\n        <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(key)
            if(isSchemaVar(key)):
                whereString += " ;\n    <" + properties_tuple["inRelationTo"] + ">    ?" + key.lower() + "_E "
                swrlString += properties_tuple["inRelationTo"] + "(" + term + " , " + "?" + key.lower() + "_E) ^ "
            else :
                whereString += " ;\n    <" + properties_tuple["inRelationTo"] + ">    " + [key + " ",key[1:] + "_V "][checkImplicit(key)] 
                swrlString += properties_tuple["inRelationTo"] + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
    elif (pd.notnull(item.Role)) : # if there is a role, but no in relation to
        input_tuple["Role"]=item.Role
        assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Role"] + "> ;\n                <" + owl.someValuesFrom + ">    [ <" + rdf.type + ">    <" + item.Role + ">    ]    ]" 
        #assertionString += " ;\n        <" + properties_tuple["Role"] + ">    [ <" + rdf.type + ">    " + item.Role + " ]"
        whereString += " ;\n    <" + properties_tuple["Role"] + ">    [ <" + rdf.type + "> " + item.Role + " ]"
        swrlString += ""  # add appropriate swrl term
    return [input_tuple, assertionString, whereString, swrlString]

def writeClassWasDerivedFrom(item, term, input_tuple, provenanceString, whereString, swrlString) :
    if pd.notnull(item.wasDerivedFrom) :
        if ',' in item.wasDerivedFrom :
            derivatives = parseString(item.wasDerivedFrom,',')
            for derivative in derivatives :
                provenanceString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.someValuesFrom + ">    " + convertImplicitToKGEntry(derivative) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["wasDerivedFrom"] + "> ]" 
                #provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(derivative)
                input_tuple["wasDerivedFrom"]=derivative
                if(isSchemaVar(derivative)):
                    whereString += " ;\n    <" + properties_tuple["wasDerivedFrom"] + ">    ?" + derivative.lower() + "_E "
                    swrlString += properties_tuple["wasDerivedFrom"] + "(" + term + " , " + "?" + derivative.lower() + "_E) ^ " 
                elif checkTemplate(derivative) :
                    open_index = derivative.find("{")
                    close_index = derivative.find("}")
                    key = derivative[open_index+1:close_index]
                    print(convertImplicitToKGEntry(key))
                    provenanceString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.someValuesFrom + ">    " + convertImplicitToKGEntry(key) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["wasDerivedFrom"] + "> ]" 
                    #provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(key)
                    whereString += " ;\n    <" + properties_tuple["wasDerivedFrom"] + ">    ?" +  key.lower() + "_E"
                    swrlString += properties_tuple["wasDerivedFrom"] + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
                else :
                    whereString += " ;\n    <" + properties_tuple["wasDerivedFrom"] + ">    " + [derivative + " ",derivative[1:] + "_V "][checkImplicit(derivative)]
                    swrlString += properties_tuple["wasDerivedFrom"] + "(" + term + " , " + [derivative,derivative[1:] + "_V"][checkImplicit(derivative)] + ") ^ " 
        else :
            provenanceString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.someValuesFrom + ">    " + convertImplicitToKGEntry(item.wasDerivedFrom) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["wasDerivedFrom"] + "> ]" 
            #provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(item.wasDerivedFrom)
            input_tuple["wasDerivedFrom"]=item.wasDerivedFrom
            if(isSchemaVar(item.wasDerivedFrom)):
                whereString += " ;\n    <" + properties_tuple["wasDerivedFrom"] + ">    ?" + item.wasDerivedFrom.lower() + "_E "
                swrlString += properties_tuple["wasDerivedFrom"] + "(" + term + " , " + "?" + item.wasDerivedFrom.lower() + "_E) ^ " 
            elif checkTemplate(item.wasDerivedFrom) :
                open_index = item.wasDerivedFrom.find("{")
                close_index = item.wasDerivedFrom.find("}")
                key = item.wasDerivedFrom[open_index+1:close_index]
                provenanceString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.someValuesFrom + ">    " + convertImplicitToKGEntry(key) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["wasDerivedFrom"] + "> ]" 
                #provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(key)
                whereString += " ;\n    <" + properties_tuple["wasDerivedFrom"] + ">    ?" +  key.lower() + "_E"
                swrlString += properties_tuple["wasDerivedFrom"] + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
            else :
                whereString += " ;\n    <" + properties_tuple["wasDerivedFrom"] + ">    " + [item.wasDerivedFrom + " ",item.wasDerivedFrom[1:] + "_V "][checkImplicit(item.wasDerivedFrom)]
                swrlString += properties_tuple["wasDerivedFrom"] + "(" + term + " , " + [item.wasDerivedFrom,item.wasDerivedFrom[1:] + "_V"][checkImplicit(item.wasDerivedFrom)] + ") ^ " 
    return [input_tuple, provenanceString, whereString, swrlString]

def writeClassWasGeneratedBy(item, term, input_tuple, provenanceString, whereString, swrlString) :
    if pd.notnull(item.wasGeneratedBy) :
        if ',' in item.wasGeneratedBy :
            generators = parseString(item.wasGeneratedBy,',')
            for generator in generators :
                provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(generator)
                input_tuple["wasGeneratedBy"]=generator
                if(isSchemaVar(generator)):
                    whereString += " ;\n    <" + properties_tuple["wasGeneratedBy"] + ">    ?" + generator.lower() + "_E "
                    swrlString += properties_tuple["wasGeneratedBy"] + "(" + term + " , " + "?" + generator.lower() + "_E) ^ " 
                elif checkTemplate(generator) :
                    open_index = generator.find("{")
                    close_index = generator.find("}")
                    key = generator[open_index+1:close_index]
                    assertionString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(key)
                    whereString += " ;\n    <" + properties_tuple["wasGeneratedBy"] + ">    ?" +  key.lower() + "_E"
                    swrlString += properties_tuple["wasGeneratedBy"] + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
                else :
                    whereString += " ;\n    <" + properties_tuple["wasGeneratedBy"] + ">    " + [generator + " ",generator[1:] + "_V "][checkImplicit(generator)]
                    swrlString += properties_tuple["wasGeneratedBy"] + "(" + term + " , " + [generator,generator[1:] + "_V"][checkImplicit(generator)] + ") ^ " 
        else :
            provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(item.wasGeneratedBy)
            input_tuple["wasGeneratedBy"]=item.wasGeneratedBy
            if(isSchemaVar(item.wasGeneratedBy)):
                whereString += " ;\n    <" + properties_tuple["wasGeneratedBy"] + ">    ?" + item.wasGeneratedBy.lower() + "_E "
                swrlString += properties_tuple["wasGeneratedBy"] + "(" + term + " , " + "?" + item.wasGeneratedBy.lower() + "_E) ^ " 
            elif checkTemplate(item.wasGeneratedBy) :
                open_index = item.wasGeneratedBy.find("{")
                close_index = item.wasGeneratedBy.find("}")
                key = item.wasGeneratedBy[open_index+1:close_index]
                assertionString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(key)
                whereString += " ;\n    <" + properties_tuple["wasGeneratedBy"] + ">    ?" +  key.lower() + "_E"
                swrlString += properties_tuple["wasGeneratedBy"] + "(" + term + " , " + [key,key[1:] + "_V"][checkImplicit(key)] + ") ^ "
            else :
                whereString += " ;\n    <" + properties_tuple["wasGeneratedBy"] + ">    " + [item.wasGeneratedBy + " ",item.wasGeneratedBy[1:] + "_V "][checkImplicit(item.wasGeneratedBy)]
                swrlString += properties_tuple["wasGeneratedBy"] + "(" + term + " , " + [item.wasGeneratedBy,item.wasGeneratedBy[1:] + "_V"][checkImplicit(item.wasGeneratedBy)] + ") ^ " 
    return [input_tuple, provenanceString, whereString, swrlString]

def writeImplicitEntryTuples(implicit_entry_list, timeline_tuple, output_file, query_file, swrl_file, dm_fn) :
    implicit_entry_tuples = []
    assertionString = ''
    provenanceString = ''
    whereString = '\n'
    swrlString = ''
    datasetIdentifier = hashlib.md5(dm_fn.encode('utf-8')).hexdigest()
    if nanopublication_option == "enabled" :
        output_file.write("<" +  prefixes[kb] + "head-implicit_entry-" + datasetIdentifier + "> { ")
        output_file.write("\n    <" +  prefixes[kb] + "nanoPub-implicit_entry-" + datasetIdentifier + ">    <" + rdf.type + ">    <" +  np.Nanopublication + ">")
        output_file.write(" ;\n        <" +  np.hasAssertion + ">    <" +  prefixes[kb] + "assertion-implicit_entry-" + datasetIdentifier + ">")
        output_file.write(" ;\n        <" +  np.hasProvenance + ">    <" +  prefixes[kb] + "provenance-implicit_entry-" + datasetIdentifier + ">")
        output_file.write(" ;\n        <" +  np.hasPublicationInfo + ">    <" +  prefixes[kb] + "pubInfo-implicit_entry-" + datasetIdentifier + ">")
        output_file.write(" .\n}\n\n")
    col_headers=list(pd.read_csv(dm_fn).columns.values)
    for item in implicit_entry_list :
        implicit_tuple = {}
        if "Template" in col_headers and pd.notnull(item.Template) :
            implicit_tuple["Template"]=item.Template
        assertionString += "\n    <" + prefixes[kb] + item.Column[2:] + ">    <" + rdf.type + ">    owl:Class"
        term_implicit = item.Column[1:] + "_V"
        whereString += "  " + term_implicit + " <" + rdf.type + "> " 
        implicit_tuple["Column"]=item.Column
        if (hasattr(item,"Label") and pd.notnull(item.Label)) :
            implicit_tuple["Label"]=item.Label
            if ',' in item.Label :
                labels = parseString(item.Label,',')
                for label in labels :
                    assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + label + "\"^^xsd:string"
            else :
                assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + item.Label + "\"^^xsd:string" 
        else :
            assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + item.Column[2:] + "\"^^xsd:string"
            implicit_tuple["Label"]=item.Column[2:]
        if (hasattr(item,"Comment") and pd.notnull(item.Comment)) :
            assertionString += " ;\n        <" + properties_tuple["Comment"] + ">    \"" + item.Comment + "\"^^xsd:string"
            implicit_tuple["Comment"]=item.Comment
        [implicit_tuple, assertionString, whereString, swrlString] = writeClassAttributeOrEntity(item, term_implicit, implicit_tuple, assertionString, whereString, swrlString)
        [implicit_tuple, assertionString, whereString, swrlString] = writeClassAttributeOf(item, term_implicit, implicit_tuple, assertionString, whereString, swrlString)
        [implicit_tuple, assertionString, whereString, swrlString] = writeClassUnit(item, term_implicit, implicit_tuple, assertionString, whereString, swrlString)
        [implicit_tuple, assertionString, whereString, swrlString] = writeClassTime(item, term_implicit, implicit_tuple, assertionString, whereString, swrlString)
        [implicit_tuple, assertionString, whereString, swrlString] = writeClassRelation(item, term_implicit, implicit_tuple, assertionString, whereString, swrlString)
        assertionString += " .\n"
        provenanceString += "\n    <" + prefixes[kb] + item.Column[2:] + ">" 
        provenanceString +="\n        <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime"
        [implicit_tuple, provenanceString, whereString, swrlString] = writeClassWasGeneratedBy(item, term_implicit, implicit_tuple, provenanceString, whereString, swrlString)
        [implicit_tuple, provenanceString, whereString, swrlString] = writeClassWasDerivedFrom(item, term_implicit, implicit_tuple, provenanceString, whereString, swrlString)
        provenanceString += " .\n"
        whereString += ".\n\n"
        implicit_entry_tuples.append(implicit_tuple)

    if timeline_tuple != {}:
        for key in timeline_tuple :
            assertionString += "\n    " + convertImplicitToKGEntry(key) + "    <" + rdf.type + ">    owl:Class "
            for timeEntry in timeline_tuple[key] :
                if 'Type' in timeEntry :
                    assertionString += " ;\n        rdfs:subClassOf    " + timeEntry['Type']
                if 'Label' in timeEntry :
                    assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + timeEntry['Label'] + "\"^^xsd:string"
                if 'Start' in timeEntry and 'End' in timeEntry and timeEntry['Start'] == timeEntry['End']:
                    assertionString += " ;\n        <" + properties_tuple["Value"] + "> " + str(timeEntry['Start']) # rewrite this as a restriction
                if 'Start' in timeEntry :
                    if 'Unit' in timeEntry :
                        assertionString += " ;\n        <" + rdfs.subClassOf + ">\n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.allValuesFrom + ">\n                    [ <" + rdf.type + ">    <" + owl.Class + "> ;\n                        <" + owl.intersectionOf + "> ( [ <" + rdf.type + "> <" + owl.Restriction + "> ;\n                            <" + owl.hasValue + "> " + str(timeEntry['Start']) +" ;\n                            <" + owl.onProperty + "> <" + properties_tuple["Value"] + "> ] " + str(codeMapper(timeEntry['Unit'])) + " ) ] ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Start"] + "> ] "
                    else : # update restriction that gets generated if unit is not specified
                        assertionString += " ;\n        <" + properties_tuple["Start"] + "> [ <" + properties_tuple["Value"] + "> " + str(timeEntry['Start']) + " ]"
                if 'End' in timeEntry :
                    if 'Unit' in timeEntry :
                        assertionString += " ;\n        <" + rdfs.subClassOf + ">\n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.allValuesFrom + ">\n                    [ <" + rdf.type + ">    <" + owl.Class + "> ;\n                        <" + owl.intersectionOf + "> ( [ <" + rdf.type + "> <" + owl.Restriction + "> ;\n                            <" + owl.hasValue + "> " + str(timeEntry['End']) +" ;\n                            <" + owl.onProperty + "> <" + properties_tuple["Value"] + "> ] " + str(codeMapper(timeEntry['Unit'])) + " ) ] ;\n                <" + owl.onProperty + ">    <" + properties_tuple["End"] + "> ] "
                    else : # update restriction that gets generated if unit is not specified
                        assertionString += " ;\n        <" + properties_tuple["End"] + "> [ <" + properties_tuple["Value"] + "> " + str(timeEntry['End']) + " ]"
                if 'Unit' in timeEntry :
                    assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.hasValue + ">    " + str(codeMapper(timeEntry['Unit'])) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Unit"] + "> ]" 
                    #assertionString += " ;\n        <" + properties_tuple["Unit"] + ">    " + timeEntry['Unit']
                if 'inRelationTo' in timeEntry :
                    assertionString += " ;\n        <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(timeEntry['inRelationTo'])
                assertionString += " .\n"
            provenanceString += "\n    " + convertImplicitToKGEntry(key) + "    <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .\n"
    if nanopublication_option == "enabled" :
        output_file.write("<" +  prefixes[kb] + "assertion-implicit_entry-" + datasetIdentifier + "> {" + assertionString + "\n}\n\n")
        output_file.write("<" +  prefixes[kb] + "provenance-implicit_entry-" + datasetIdentifier + "> {")
        provenanceString = "\n    <" +  prefixes[kb] + "assertion-implicit_entry-" + datasetIdentifier + ">    <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .\n" + provenanceString
        output_file.write(provenanceString + "\n}\n\n")
        output_file.write("<" +  prefixes[kb] + "pubInfo-implicit_entry-" + datasetIdentifier + "> {\n    <" +  prefixes[kb] + "nanoPub-implicit_entry-" + datasetIdentifier + ">    <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .\n}\n\n")
    else :
        output_file.write(assertionString + "\n")
        output_file.write(provenanceString + "\n")
    whereString += "}"
    query_file.write(whereString)
    swrl_file.write(swrlString[:-2])
    return implicit_entry_tuples

def writeExplicitEntryTuples(explicit_entry_list, output_file, query_file, swrl_file, dm_fn) :
    explicit_entry_tuples = []
    assertionString = ''
    provenanceString = ''
    publicationInfoString = ''
    selectString = "SELECT DISTINCT "
    whereString = "WHERE {\n"
    swrlString = ""
    datasetIdentifier = hashlib.md5(dm_fn.encode('utf-8')).hexdigest()
    if nanopublication_option == "enabled" :
        output_file.write("<" +  prefixes[kb] + "head-explicit_entry-" + datasetIdentifier + "> { ")
        output_file.write("\n    <" +  prefixes[kb] + "nanoPub-explicit_entry-" + datasetIdentifier + ">    <" + rdf.type + ">    <" +  np.Nanopublication + ">")
        output_file.write(" ;\n        <" +  np.hasAssertion + ">    <" +  prefixes[kb] + "assertion-explicit_entry-" + datasetIdentifier + ">")
        output_file.write(" ;\n        <" +  np.hasProvenance + ">    <" +  prefixes[kb] + "provenance-explicit_entry-" + datasetIdentifier + ">")
        output_file.write(" ;\n        <" +  np.hasPublicationInfo + ">    <" +  prefixes[kb] + "pubInfo-explicit_entry-" + datasetIdentifier + ">")
        output_file.write(" .\n}\n\n")
    col_headers=list(pd.read_csv(dm_fn).columns.values)
    for item in explicit_entry_list :
        explicit_entry_tuple = {}
        if "Template" in col_headers and pd.notnull(item.Template) :
            explicit_entry_tuple["Template"]=item.Template
        term = item.Column.replace(" ","_").replace(",","").replace("(","").replace(")","").replace("/","-").replace("\\","-")
        assertionString += "\n    <" + prefixes[kb] + term + ">    <" + rdf.type + ">    owl:Class"
        selectString += "?" + term.lower() + " "
        whereString += "  ?" + term.lower() + "_E <" + rdf.type + "> "
        term_expl = "?" + term.lower() + "_E"
        #print(item.Column
        explicit_entry_tuple["Column"]=item.Column
        [explicit_entry_tuple, assertionString, whereString, swrlString] = writeClassAttributeOrEntity(item, term_expl, explicit_entry_tuple, assertionString, whereString, swrlString)
        [explicit_entry_tuple, assertionString, whereString, swrlString] = writeClassAttributeOf(item, term_expl, explicit_entry_tuple, assertionString, whereString, swrlString)
        [explicit_entry_tuple, assertionString, whereString, swrlString] = writeClassUnit(item, term_expl, explicit_entry_tuple, assertionString, whereString, swrlString)
        [explicit_entry_tuple, assertionString, whereString, swrlString] = writeClassTime(item, term_expl, explicit_entry_tuple, assertionString, whereString, swrlString)
        [explicit_entry_tuple, assertionString, whereString, swrlString] = writeClassRelation(item, term_expl, explicit_entry_tuple, assertionString, whereString, swrlString)
        if "Label" in col_headers and (pd.notnull(item.Label)) :
            if ',' in item.Label :
                labels = parseString(item.Label,',')
                for label in labels :
                    assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + label + "\"^^xsd:string"
            else :
                assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + item.Label + "\"^^xsd:string" 
            explicit_entry_tuple["Label"]=item.Label
        if "Comment" in col_headers and (pd.notnull(item.Comment)) :
            assertionString += " ;\n        <" + properties_tuple["Comment"] + ">    \"" + item.Comment + "\"^^xsd:string"
            explicit_entry_tuple["Comment"]=item.Comment
        if "Format" in col_headers and (pd.notnull(item.Format)) :
            explicit_entry_tuple["Format"]=item.Format
        assertionString += " .\n" 
        
        provenanceString += "\n    <" + prefixes[kb] + term + ">"
        provenanceString += "\n        <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime"
        [explicit_entry_tuple, provenanceString, whereString, swrlString] = writeClassWasGeneratedBy(item, term_expl, explicit_entry_tuple, provenanceString, whereString, swrlString)
        [explicit_entry_tuple, provenanceString, whereString, swrlString] = writeClassWasDerivedFrom(item, term_expl, explicit_entry_tuple, provenanceString, whereString, swrlString)
        provenanceString += " .\n"
        whereString += " ;\n    <" + properties_tuple["Value"] + "> ?" + term.lower() + " .\n\n"
        if "hasPosition" in col_headers and pd.notnull(item.hasPosition) :
            publicationInfoString += "\n    <" + prefixes[kb] + term + ">    hasco:hasPosition    \"" + str(item.hasPosition) + "\"^^xsd:integer ."
            explicit_entry_tuple["hasPosition"]=item.hasPosition
        explicit_entry_tuples.append(explicit_entry_tuple)
    if nanopublication_option == "enabled" :
        output_file.write("<" +  prefixes[kb] + "assertion-explicit_entry-" + datasetIdentifier + "> {" + assertionString + "\n}\n\n")
        output_file.write("<" +  prefixes[kb] + "provenance-explicit_entry-" + datasetIdentifier + "> {")
        provenanceString = "\n    <" +  prefixes[kb] + "assertion-explicit_entry-" + datasetIdentifier + ">    <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .\n" + provenanceString
        output_file.write(provenanceString + "\n}\n\n")
        output_file.write("<" +  prefixes[kb] + "pubInfo-explicit_entry-" + datasetIdentifier + "> {\n    <" +  prefixes[kb] + "nanoPub-explicit_entry-" + datasetIdentifier + ">    <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .")
        output_file.write(publicationInfoString + "\n}\n\n")
    else :
        output_file.write(assertionString + "\n")
        output_file.write(provenanceString + "\n")
    query_file.write(selectString)
    query_file.write(whereString)
    swrl_file.write(swrlString)
    return explicit_entry_tuples

def writeImplicitEntry(assertionString, provenanceString,publicationInfoString, explicit_entry_tuples, implicit_entry_tuples, timeline_tuple, vref_list, v_column, index, row, col_headers) : 
    try :
        #col_headers=list(pd.read_csv(dm_fn).columns.values)
        if timeline_tuple != {} :
            if v_column in timeline_tuple :
                v_id = hashlib.md5((str(timeline_tuple[v_column]) + str(index)).encode("utf-8")).hexdigest()
                assertionString += "\n    " + convertImplicitToKGEntry(v_column, v_id) + "    <" + rdf.type + ">    " + convertImplicitToKGEntry(v_column)
                for timeEntry in timeline_tuple[v_column] :
                    if 'Type' in timeEntry :
                        assertionString += " ;\n        <" + rdf.type + ">    " + timeEntry['Type']
                    if 'Label' in timeEntry :
                        assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + timeEntry['Label'] + "\"^^xsd:string"
                    if 'Start' in timeEntry and 'End' in timeEntry and timeEntry['Start'] == timeEntry['End']:
                        assertionString += " ;\n        <" + properties_tuple["Value"] + "> " + str(timeEntry['Start'])
                    if 'Start' in timeEntry :
                        assertionString += " ;\n        <" + properties_tuple["Start"] + "> [ <" + properties_tuple["Value"] + "> " + str(timeEntry['Start']) + " ]"
                    if 'End' in timeEntry :
                        assertionString += " ;\n        <" + properties_tuple["End"] + "> [ <" + properties_tuple["Value"] + "> " + str(timeEntry['End']) + " ]"
                    if 'Unit' in timeEntry :
                        assertionString += " ;\n        <" + rdfs.subClassOf + ">    \n            [ <" + rdf.type + ">    <" + owl.Restriction + "> ;\n                <" + owl.hasValue + ">    " + str(codeMapper(timeEntry['Unit'])) + " ;\n                <" + owl.onProperty + ">    <" + properties_tuple["Unit"] + "> ]" 
                        #assertionString += " ;\n        <" + properties_tuple["Unit"] + ">    " + timeEntry['Unit']
                    if 'inRelationTo' in timeEntry :
                        assertionString += " ;\n        <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(timeEntry['inRelationTo'], v_id)
                        if checkImplicit(timeEntry['inRelationTo']) and timeEntry['inRelationTo'] not in vref_list :
                            vref_list.append(timeEntry['inRelationTo'])
                assertionString += " .\n"
        for v_tuple in implicit_entry_tuples :
            if (v_tuple["Column"] == v_column) :
                if "Study" in v_tuple :
                    continue
                else :
                    v_id = hashlib.md5((str(v_tuple) + str(index)).encode("utf-8")).hexdigest()
                    if "Template" in v_tuple :
                        template_term = extractTemplate(col_headers,row,v_tuple["Template"])
                        termURI = "<" + prefixes[kb] + template_term + ">"
                    else :
                        termURI = "<" + prefixes[kb] + v_tuple["Column"][2:] + "-" + v_id + ">"
                    assertionString += "\n    " + termURI + "    <" + rdf.type + ">    <" + prefixes[kb] + v_tuple["Column"][2:] + ">"
                    if "Entity" in v_tuple :
                        if ',' in v_tuple["Entity"] :
                            entities = parseString(v_tuple["Entity"],',')
                            for entity in entities :
                                assertionString += " ;\n        <" + rdf.type + ">    " + entity
                        else :
                            assertionString += " ;\n        <" + rdf.type + ">    " + v_tuple["Entity"]
                    if "Attribute" in v_tuple :
                        if ',' in v_tuple["Attribute"] :
                            attributes = parseString(v_tuple["Attribute"],',')
                            for attribute in attributes :
                                assertionString += " ;\n        <" + rdf.type + ">    " + attribute
                        else :
                            assertionString += " ;\n        <" + rdf.type + ">    " + v_tuple["Attribute"]
                    # Need to get the right ID uri if we put this in.. Commenting out identifier for now
                    #if "Subject" in v_tuple :
                    #    assertionString += " ;\n        sio:hasIdentifier <" + prefixes[kb] + v_tuple["Subject"] + "-" + v_id + ">" #should be actual ID
                    if "Label" in v_tuple :
                        if ',' in v_tuple["Label"] :
                            labels = parseString(v_tuple["Label"],',')
                            for label in labels :
                                assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + label + "\"^^xsd:string"
                        else :
                            assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + v_tuple["Label"] + "\"^^xsd:string"
                    if "Time" in v_tuple :
                        if checkImplicit(v_tuple["Time"]) :
                            for vr_tuple in implicit_entry_tuples :
                                if (vr_tuple["Column"] == v_tuple["Time"]) :
                                    timeID = hashlib.md5((str(vr_tuple) + str(index)).encode("utf-8")).hexdigest()
                            assertionString += " ;\n        <" + properties_tuple["Time"] + ">    " + convertImplicitToKGEntry(v_tuple["Time"], timeID)
                            if v_tuple["Time"] not in vref_list :
                                vref_list.append(v_tuple["Time"])
                        else :
                            assertionString += " ;\n        <" + properties_tuple["Time"] + ">    " + convertImplicitToKGEntry(v_tuple["Time"], v_id) #should be actual ID
                    if "inRelationTo" in v_tuple :
                        relationToID = None
                        for vr_tuple in implicit_entry_tuples :
                            if (vr_tuple["Column"] == v_tuple["inRelationTo"]) :
                                relationToID = hashlib.md5((str(vr_tuple) + str(index)).encode("utf-8")).hexdigest()
                        if ("Role" in v_tuple) and ("Relation" not in v_tuple) :
                            assertionString += " ;\n        <" + properties_tuple["Role"] + ">    [ <" + rdf.type + ">    " + v_tuple["Role"] + " ;\n            <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(v_tuple["inRelationTo"], relationToID) + " ]"
                        elif ("Role" not in v_tuple) and ("Relation" in v_tuple) :
                            assertionString += " ;\n        " + v_tuple["Relation"] + " " + convertImplicitToKGEntry(v_tuple["inRelationTo"],v_id)
                            assertionString += " ;\n        " + v_tuple["Relation"] + " " + convertImplicitToKGEntry(v_tuple["inRelationTo"],relationToID)
                        elif ("Role" not in v_tuple) and ("Relation" not in v_tuple) :
                            assertionString += " ;\n        <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(v_tuple["inRelationTo"],relationToID)
                    elif "Role" in v_tuple :
                        assertionString += " ;\n        <" + properties_tuple["Role"] + ">    [ <" + rdf.type + ">    " + v_tuple["Role"] + " ]"
                    assertionString += " .\n"
                    provenanceString += "\n    " + termURI + "    <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime"
                    if "wasGeneratedBy" in v_tuple : 
                        if ',' in v_tuple["wasGeneratedBy"] :
                            generatedByTerms = parseString(v_tuple["wasGeneratedBy"],',')
                            for generatedByTerm in generatedByTerms :
                                provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(generatedByTerm,v_id)
                                if checkImplicit(generatedByTerm) and generatedByTerm not in vref_list :
                                    vref_list.append(generatedByTerm)
                        else :
                            provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(v_tuple["wasGeneratedBy"],v_id)
                            if checkImplicit(v_tuple["wasGeneratedBy"]) and v_tuple["wasGeneratedBy"] not in vref_list :
                                vref_list.append(v_tuple["wasGeneratedBy"]);
                    if "wasDerivedFrom" in v_tuple : 
                        if ',' in v_tuple["wasDerivedFrom"] :
                            derivedFromTerms = parseString(v_tuple["wasDerivedFrom"],',')
                            for derivedFromTerm in derivedFromTerms :
                                provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(derivedFromTerm,v_id)
                                if checkImplicit(derivedFromTerm) and derivedFromTerm not in vref_list :
                                    vref_list.append(derivedFromTerm);
                        else :
                            provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(v_tuple["wasDerivedFrom"],v_id)
                            if checkImplicit(v_tuple["wasDerivedFrom"]) and v_tuple["wasDerivedFrom"] not in vref_list :
                                vref_list.append(v_tuple["wasDerivedFrom"]);
                    #if  "wasGeneratedBy" in v_tuple or "wasDerivedFrom" in v_tuple  :
                    provenanceString += " .\n"
        return [assertionString,provenanceString,publicationInfoString,vref_list]
    except Exception as e :
        print("Warning: Unable to create implicit entry: " + str(e))

def processInfosheet(output_file, dm_fn, cb_fn, cmap_fn, timeline_fn):
    infosheet_tuple = {}
    if 'infosheet' in config['Source Files'] :
        infosheet_fn = config['Source Files']['infosheet']
        try :
            infosheet_file = pd.read_csv(infosheet_fn, dtype=object)
        except Exception as e :
            print("Warning: Collection metadata will not be written to the output file.\nThe specified Infosheet file does not exist or is unreadable: " + str(e))
            return [dm_fn, cb_fn, cmap_fn, timeline_fn]
        for row in infosheet_file.itertuples() :
            if(pd.notnull(row.Value)):
                infosheet_tuple[row.Attribute]=row.Value   
        # If SDD files included in Infosheet, they override the config declarations
        if "Dictionary Mapping" in infosheet_tuple :
            dm_fn = infosheet_tuple["Dictionary Mapping"] 
        if "Codebook" in infosheet_tuple : 
            cb_fn = infosheet_tuple["Codebook"]
        if "Code Mapping" in infosheet_tuple : 
            cmap_fn = infosheet_tuple["Code Mapping"]
        if "Timeline" in infosheet_tuple : 
            timeline_fn = infosheet_tuple["Timeline"]
        datasetIdentifier = hashlib.md5(dm_fn.encode('utf-8')).hexdigest()
        if nanopublication_option == "enabled" :
            output_file.write("<" +  prefixes[kb] + "head-collection_metadata-" + datasetIdentifier + "> { ")
            output_file.write("\n    <" +  prefixes[kb] + "nanoPub-collection_metadata-" + datasetIdentifier + ">    <" + rdf.type + ">    <" +  np.Nanopublication + ">")
            output_file.write(" ;\n        <" +  np.hasAssertion + ">    <" +  prefixes[kb] + "assertion-collection_metadata-" + datasetIdentifier + ">")
            output_file.write(" ;\n        <" +  np.hasProvenance + ">    <" +  prefixes[kb] + "provenance-collection_metadata-" + datasetIdentifier + ">")
            output_file.write(" ;\n        <" +  np.hasPublicationInfo + ">    <" +  prefixes[kb] + "pubInfo-collection_metadata-" + datasetIdentifier + ">")
            output_file.write(" .\n}\n\n")
        assertionString = "<" +  prefixes[kb] + "collection-" + datasetIdentifier + ">"
        provenanceString = "    <" +  prefixes[kb] + "collection-" + datasetIdentifier + ">    <http://www.w3.org/ns/prov#generatedAtTime>    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime"
        if "Type" in infosheet_tuple :
            assertionString += "    <" + rdf.type + ">    " + [infosheet_tuple["Type"],"<" + infosheet_tuple["Type"] + ">"][isURI(infosheet_tuple["Type"])]
        else :
            assertionString += "    <" + rdf.type + ">    <http://purl.org/dc/dcmitype/Collection>"
            #print("Warning: The Infosheet file is missing the Type value declaration")
            #sys.exit(1)
        if "Title" in infosheet_tuple :
            assertionString += " ;\n        <http://purl.org/dc/terms/title>    \"" + infosheet_tuple["Title"] + "\"^^xsd:string"
        if "Alternative Title" in infosheet_tuple : 
            if ',' in infosheet_tuple["Alternative Title"] :
                alt_titles = parseString(infosheet_tuple["Alternative Title"],',')
                for alt_title in alt_titles :
                    assertionString += " ;\n        <http://purl.org/dc/terms/alternative>    \"" + alt_title + "\"^^xsd:string"
            else :
                assertionString += " ;\n        <http://purl.org/dc/terms/alternative>    \"" + infosheet_tuple["Alternative Title"] + "\"^^xsd:string"
        if "Comment" in infosheet_tuple :
            assertionString += " ;\n        <http://www.w3.org/2000/01/rdf-schema#comment>    \"" + infosheet_tuple["Comment"] + "\"^^xsd:string"
        if "Description" in infosheet_tuple :
            assertionString += " ;\n        <http://purl.org/dc/terms/description>    \"" + infosheet_tuple["Description"] + "\"^^xsd:string"
        if "Date Created" in infosheet_tuple :
            provenanceString += " ;\n        <http://purl.org/dc/terms/created>    \"" + infosheet_tuple["Date Created"] + "\"^^xsd:date"
        if "Creators" in infosheet_tuple : 
            if ',' in infosheet_tuple["Creators"] :
                creators = parseString(infosheet_tuple["Creators"],',')
                for creator in creators :
                    provenanceString += " ;\n        <http://purl.org/dc/terms/creator>    " + ["\"" + creator + "\"^^xsd:string","<" + creator + ">"][isURI(creator)]
            else :
                provenanceString += " ;\n        <http://purl.org/dc/terms/creator>    " + ["\"" + infosheet_tuple["Creators"] + "\"^^xsd:string","<" + infosheet_tuple["Creators"] + ">"][isURI(infosheet_tuple["Creators"])]
        if "Contributors" in infosheet_tuple : 
            if ',' in infosheet_tuple["Contributors"] :
                contributors = parseString(infosheet_tuple["Contributors"],',')
                for contributor in contributors :
                    provenanceString += " ;\n        <http://purl.org/dc/terms/contributor>    " + ["\"" + contributor + "\"^^xsd:string","<" + contributor + ">"][isURI(contributor)]
            else :
                provenanceString += " ;\n        <http://purl.org/dc/terms/contributor>    " + ["\"" + infosheet_tuple["Contributors"] + "\"^^xsd:string","<" + infosheet_tuple["Contributors"] + ">"][isURI(infosheet_tuple["Contributors"])]
        if "Publisher" in infosheet_tuple :
            if ',' in infosheet_tuple["Publisher"] :
                publishers = parseString(infosheet_tuple["Publisher"],',')
                for publisher in publishers :
                    provenanceString += " ;\n        <http://purl.org/dc/terms/publisher>    " + ["\"" + publisher + "\"^^xsd:string","<" + publisher + ">"][isURI(publisher)]
            else :
                provenanceString += " ;\n        <http://purl.org/dc/terms/publisher>    " + ["\"" + infosheet_tuple["Publisher"] + "\"^^xsd:string","<" + infosheet_tuple["Publisher"] + ">"][isURI(infosheet_tuple["Publisher"])]
        if "Date of Issue" in infosheet_tuple :
            provenanceString += " ;\n        <http://purl.org/dc/terms/issued>    \"" + infosheet_tuple["Date of Issue"] + "\"^^xsd:date"
        if "Link" in infosheet_tuple :
            assertionString += " ;\n        <http://xmlns.com/foaf/0.1/page>    <" + infosheet_tuple["Link"] + ">"
        if "Identifier" in infosheet_tuple :
            assertionString += " ;\n        <http://semanticscience.org/resource/hasIdentifier>    \n            [ <" + rdf.type + ">    <http://semanticscience.org/resource/Identifier> ; \n            <http://semanticscience.org/resource/hasValue>    \"" + infosheet_tuple["Identifier"] + "\"^^xsd:string ]"
        if "Keywords" in infosheet_tuple :
            if ',' in infosheet_tuple["Keywords"] :
                keywords = parseString(infosheet_tuple["Keywords"],',')
                for keyword in keywords :
                    assertionString += " ;\n        <http://www.w3.org/ns/dcat#keyword>    \"" + keyword + "\"^^xsd:string"
            else :
                assertionString += " ;\n        <http://www.w3.org/ns/dcat#keyword>    \"" + infosheet_tuple["Keywords"] + "\"^^xsd:string"
        if "License" in infosheet_tuple : 
            if ',' in infosheet_tuple["License"] :
                licenses = parseString(infosheet_tuple["License"],',')
                for license in licenses :
                    assertionString += " ;\n        <http://purl.org/dc/terms/license>    " + ["\"" + license + "\"^^xsd:string","<" + license + ">"][isURI(license)]
            else :
                assertionString += " ;\n        <http://purl.org/dc/terms/license>    " + ["\"" + infosheet_tuple["License"] + "\"^^xsd:string","<" + infosheet_tuple["License"] + ">"][isURI(infosheet_tuple["License"])]
        if "Rights" in infosheet_tuple :
            if ',' in infosheet_tuple["Rights"] :
                rights = parseString(infosheet_tuple["Rights"],',')
                for right in rights :
                    assertionString += " ;\n        <http://purl.org/dc/terms/rights>    " + ["\"" + right + "\"^^xsd:string","<" + right + ">"][isURI(right)]
            else :
                assertionString += " ;\n        <http://purl.org/dc/terms/rights>    " + ["\"" + infosheet_tuple["Rights"] + "\"^^xsd:string","<" + infosheet_tuple["Rights"] + ">"][isURI(infosheet_tuple["Rights"])]
        if "Language" in infosheet_tuple :
            assertionString += " ;\n        <http://purl.org/dc/terms/language>    \"" + infosheet_tuple["Language"] + "\"^^xsd:string"
        if "Version" in infosheet_tuple :
            provenanceString += " ;\n        <http://purl.org/pav/version>    " + ["\"" + infosheet_tuple["Version"] + "\"^^xsd:string","<" + infosheet_tuple["Version"] + ">"][isURI(infosheet_tuple["Version"])]
            provenanceString += " ;\n        <http://www.w3.org/2002/07/owl/versionInfo>    " + ["\"" + infosheet_tuple["Version"] + "\"^^xsd:string","<" + infosheet_tuple["Version"] + ">"][isURI(infosheet_tuple["Version"])]
        if "Previous Version" in infosheet_tuple :
            provenanceString += " ;\n        <http://purl.org/pav/previousVersion>    " + ["\"" + infosheet_tuple["Previous Version"] + "\"^^xsd:string","<" + infosheet_tuple["Previous Version"] + ">"][isURI(infosheet_tuple["Previous Version"])]
        if "Version Of" in infosheet_tuple :
            provenanceString += " ;\n        <http://purl.org/dc/terms/isVersionOf>    " + ["\"" + infosheet_tuple["Version Of"] + "\"^^xsd:string","<" + infosheet_tuple["Version Of"] + ">"][isURI(infosheet_tuple["Version Of"])]
        if "Standards" in infosheet_tuple : 
            if ',' in infosheet_tuple["Standards"] :
                standards = parseString(infosheet_tuple["Standards"],',')
                for standard in standards :
                    assertionString += " ;\n        <http://purl.org/dc/terms/conformsTo>    " + ["\"" + standard + "\"^^xsd:string","<" + standard + ">"][isURI(standard)]
            else :
                assertionString += " ;\n        <http://purl.org/dc/terms/conformsTo>    " + ["\"" + infosheet_tuple["Standards"] + "\"^^xsd:string","<" + infosheet_tuple["Standards"] + ">"][isURI(infosheet_tuple["Standards"])]
        if "Source" in infosheet_tuple : 
            if ',' in infosheet_tuple["Source"] :
                sources = parseString(infosheet_tuple["Source"],',')
                for source in sources :
                    provenanceString += " ;\n        <http://purl.org/dc/terms/source>    \"" + source + "\"^^xsd:string"
            else :
                provenanceString += " ;\n        <http://purl.org/dc/terms/source>    " + ["\"" + infosheet_tuple["Source"] + "\"^^xsd:string","<" + infosheet_tuple["Source"] + ">"][isURI(infosheet_tuple["Source"])]
        if "File Format" in infosheet_tuple :
            assertionString += " ;\n        <http://purl.org/dc/terms/format>    \"" + infosheet_tuple["File Format"] + "\"^^xsd:string"
        if "Documentation" in infosheet_tuple : # currently encoded as URI, should confirm that it really is one
            provenanceString += " ;\n        <http://www.w3.org/ns/dcat#landingPage>    <" + infosheet_tuple["Documentation"] + ">"   
        if "Imports" in infosheet_tuple :
            if ',' in infosheet_tuple["Imports"] :
                imports = parseString(infosheet_tuple["Imports"],',')
                for imp in imports :
                    assertionString += " ;\n        <http://www.w3.org/2002/07/owl#imports>    " + [imp,"<" + imp + ">"][isURI(imp)]
            else :
                assertionString += " ;\n        <http://www.w3.org/2002/07/owl#imports>    " + [infosheet_tuple["Imports"],"<" + infosheet_tuple["Imports"] + ">"][isURI(infosheet_tuple["Imports"])]
        assertionString += " .\n"
        provenanceString += " .\n"
        if nanopublication_option == "enabled" :
            output_file.write("<" +  prefixes[kb] + "assertion-collection_metadata-" + datasetIdentifier + "> {\n    " + assertionString + "\n}\n\n")
            output_file.write("<" +  prefixes[kb] + "provenance-collection_metadata-" + datasetIdentifier + "> {\n    <" +  prefixes[kb] + "assertion-dataset_metadata-" + datasetIdentifier + ">    <http://www.w3.org/ns/prov#generatedAtTime>    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .\n" + provenanceString + "\n}\n\n")
            output_file.write("<" +  prefixes[kb] + "pubInfo-collection_metadata-" + datasetIdentifier + "> {")
            publicationInfoString = "\n    <" +  prefixes[kb] + "nanoPub-collection_metadata-" + datasetIdentifier + ">    <http://www.w3.org/ns/prov#generatedAtTime>    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .\n"
            output_file.write(publicationInfoString + "\n}\n\n")
        else :
            output_file.write(assertionString +"\n\n")
            output_file.write(provenanceString + "\n")
    return [dm_fn, cb_fn, cmap_fn, timeline_fn]

def processPrefixes(output_file,query_file):
    prefixes = {}
    if 'prefixes' in config['Prefixes']:
        prefix_fn = config['Prefixes']['prefixes']
    else:
        prefix_fn="prefixes.csv"
    try:
        prefix_file = pd.read_csv(prefix_fn, dtype=object)
        for row in prefix_file.itertuples() :
            prefixes[row.prefix] = row.url
        for prefix in prefixes :
            #print(prefix.find(">"))
            output_file.write("@prefix " + prefix + ": <" + prefixes[prefix] + "> .\n")
            query_file.write("prefix " + prefix + ": <" + prefixes[prefix] + "> \n")
        query_file.write("\n")
        output_file.write("\n")
    except Exception as e :
        print("Warning: Something went wrong when trying to read the prefixes file: " + str(e))
    return prefixes
    
def processCodeMappings(cmap_fn):
    unit_code_list = []
    unit_uri_list = []
    unit_label_list = []
    if cmap_fn is not None :
        try :
            code_mappings_reader = pd.read_csv(cmap_fn)
            #Using itertuples on a data frame makes the column heads case-sensitive
            for code_row in code_mappings_reader.itertuples() :
                if pd.notnull(code_row.code):
                    unit_code_list.append(code_row.code)
                if pd.notnull(code_row.uri):
                    unit_uri_list.append(code_row.uri)
                if pd.notnull(code_row.label):
                    unit_label_list.append(code_row.label)
        except Exception as e :
            print("Warning: Something went wrong when trying to read the Code Mappings file: " + str(e))
    return [unit_code_list,unit_uri_list,unit_label_list]

def processProperties():
    properties_tuple = {'Comment': rdfs.comment, 'attributeOf': sio.isAttributeOf, 'Attribute': rdf.type, 'Definition' : skos.definition, 'Value' : sio.hasValue, 'wasDerivedFrom': prov.wasDerivedFrom, 'Label': rdfs.label, 'inRelationTo': sio.inRelationTo, 'Role': sio.hasRole, 'Start' : sio.hasStartTime, 'End' : sio.hasEndTime, 'Time': sio.existsAt, 'Entity': rdf.type, 'Unit': sio.hasUnit, 'wasGeneratedBy': prov.wasGeneratedBy}
    if 'properties' in config['Source Files'] :
        properties_fn = config['Source Files']['properties']
        try :
            properties_file = pd.read_csv(properties_fn, dtype=object)
        except Exception as e :
            print("Warning: The specified Properties file does not exist or is unreadable: " + str(e))
            return properties_tuple
        for row in properties_file.itertuples() :
            if(hasattr(row,"Property") and pd.notnull(row.Property)):
                if(("http://" in row.Property) or ("https://" in row.Property)) :
                    properties_tuple[row.Column]=row.Property
                elif(":" in row.Property) :
                    terms = row.Property.split(":")
                    properties_tuple[row.Column]=rdflib.term.URIRef(prefixes[terms[0]]+terms[1])
                elif("." in row.Property) :
                    terms = row.Property.split(".")
                    properties_tuple[row.Column]=rdflib.term.URIRef(prefixes[terms[0]]+terms[1])
    return properties_tuple

def processTimeline(timeline_fn):
    timeline_tuple = {}
    if timeline_fn is not None :
        try :
            timeline_file = pd.read_csv(timeline_fn, dtype=object)
            try :
                inner_tuple_list = []
                row_num=0
                for row in timeline_file.itertuples():
                    if (pd.notnull(row.Name) and row.Name not in timeline_tuple) :
                        inner_tuple_list=[]
                    inner_tuple = {}
                    inner_tuple["Type"]=row.Type
                    if(hasattr(row,"Label") and pd.notnull(row.Label)):
                        inner_tuple["Label"]=row.Label
                    if(pd.notnull(row.Start)) :
                        inner_tuple["Start"]=row.Start
                    if(pd.notnull(row.End)) :
                        inner_tuple["End"]=row.End
                    if(hasattr(row,"Unit") and pd.notnull(row.Unit)) :
                        inner_tuple["Unit"]=row.Unit
                    if(hasattr(row,"inRelationTo") and pd.notnull(row.inRelationTo)) :
                        inner_tuple["inRelationTo"]=row.inRelationTo
                    inner_tuple_list.append(inner_tuple)
                    timeline_tuple[row.Name]=inner_tuple_list
                    row_num += 1
            except Exception as e :
                print("Warning: Unable to process Timeline file: " + str(e))

        except Exception as e :
            print("Warning: The specified Timeline file does not exist: " + str(e))
            #sys.exit(1)
    return timeline_tuple

def processDictionaryMapping(dm_fn):
    try :
        dm_file = pd.read_csv(dm_fn, dtype=object)
    except Exception as e:
        print("Current directory: " + os.getcwd() + "/ - " + str(os.path.isfile(dm_fn)) )
        print("Error: The processing DM file \"" + dm_fn + "\": " + str(e))
        sys.exit(1)
    try: 
        # Set implicit and explicit entries
        for row in dm_file.itertuples() :
            if (pd.isnull(row.Column)) :
                print("Error: The DM must have a column named 'Column'")
                sys.exit(1)
            if row.Column.startswith("??") :
                implicit_entry_list.append(row)
            else :
                explicit_entry_list.append(row)
    except Exception as e :
        print("Something went wrong when trying to read the DM: " + str(e))
        sys.exit(1)
    return [explicit_entry_list,implicit_entry_list]

def processCodebook(cb_fn):
    cb_tuple = {}
    if cb_fn is not None :
        try :
            cb_file = pd.read_csv(cb_fn, dtype=object)
        except Exception as e:
            print("Error: The processing Codebook file: " + str(e))
            sys.exit(1)
        try :
            inner_tuple_list = []
            row_num=0
            for row in cb_file.itertuples():
                if (pd.notnull(row.Column) and row.Column not in cb_tuple) :
                    inner_tuple_list=[]
                inner_tuple = {}
                inner_tuple["Code"]=row.Code
                if(hasattr(row,"Label") and pd.notnull(row.Label)):
                    inner_tuple["Label"]=row.Label
                if(hasattr(row,"Class") and pd.notnull(row.Class)) :
                    inner_tuple["Class"]=row.Class
                if (hasattr(row,"Resource") and pd.notnull(row.Resource)) : # "Resource" in row and 
                    inner_tuple["Resource"]=row.Resource
                if (hasattr(row,"Comment") and pd.notnull(row.Comment)) : 
                    inner_tuple["Comment"]=row.Comment
                if (hasattr(row,"Definition") and pd.notnull(row.Definition)) :  
                    inner_tuple["Definition"]=row.Definition
                inner_tuple_list.append(inner_tuple)
                cb_tuple[row.Column]=inner_tuple_list
                row_num += 1
        except Exception as e :
            print("Warning: Unable to process Codebook file: " + str(e))
    return cb_tuple

def processData(data_fn, output_file, query_file, swrl_file, cb_tuple, timeline_tuple, explicit_entry_tuples, implicit_entry_tuples):
    xsd_datatype_list = ["anyURI", "base64Binary", "boolean", "date", "dateTime", "decimal", "double", "duration", "float", "hexBinary", "gDay", "gMonth", "gMonthDay", "gYear", "gYearMonth", "NOTATION", "QName", "string", "time" ]
    if data_fn != None :
        try :
            data_file = pd.read_csv(data_fn, dtype=object)
        except Exception as e :
            print("Error: The specified Data file does not exist: " + str(e))
            sys.exit(1)
        try :
            # ensure that there is a column annotated as the sio:Identifier or hasco:originalID in the data file:
            # TODO make sure this is getting the first available ID property for the _subject_ (and not anything else)
            col_headers=list(data_file.columns.values)
            #id_index=None
            try :
                for a_tuple in explicit_entry_tuples :
                    if "Attribute" in a_tuple :
                        if ((a_tuple["Attribute"] == "hasco:originalID") or (a_tuple["Attribute"] == "sio:Identifier")) :
                            if(a_tuple["Column"] in col_headers) :
                                #print(a_tuple["Column"])
                                #id_index = col_headers.index(a_tuple["Column"])# + 1
                                #print(id_index)
                                for v_tuple in implicit_entry_tuples :
                                    if "isAttributeOf" in a_tuple :
                                        if (a_tuple["isAttributeOf"] == v_tuple["Column"]) :
                                            v_tuple["Subject"]=a_tuple["Column"].replace(" ","_").replace(",","").replace("(","").replace(")","").replace("/","-").replace("\\","-")
            except Exception as e :
                print("Error processing column headers: " + str(e))
            for row in data_file.itertuples() :
                #print(row)
                assertionString = ''
                provenanceString = ''
                publicationInfoString = ''           
                id_string=''
                for term in row[1:] :
                    if term is not None:
                        id_string+=str(term)
                npubIdentifier = hashlib.md5(id_string.encode("utf-8")).hexdigest()
                try:
                    if nanopublication_option == "enabled" :
                        output_file.write("<" +  prefixes[kb] + "head-" + npubIdentifier + "> {")
                        output_file.write("\n    <" +  prefixes[kb] + "nanoPub-" + npubIdentifier + ">")
                        output_file.write("\n        <" + rdf.type + ">    <" +  np.Nanopublication + ">")
                        output_file.write(" ;\n        <" +  np.hasAssertion + ">    <" +  prefixes[kb] + "assertion-" + npubIdentifier + ">")
                        output_file.write(" ;\n        <" +  np.hasProvenance + ">    <" +  prefixes[kb] + "provenance-" + npubIdentifier + ">")
                        output_file.write(" ;\n        <" +  np.hasPublicationInfo + ">    <" +  prefixes[kb] + "pubInfo-" + npubIdentifier + ">")
                        output_file.write(" .\n}\n\n")# Nanopublication head

                    vref_list = []
                    for a_tuple in explicit_entry_tuples :
                        #print(a_tuple["Column"])
                        #print(col_headers)
                        #print("\n")
                        if (a_tuple["Column"] in col_headers ) :                     
                            typeString = ""
                            if "Attribute" in a_tuple :
                                typeString += str(a_tuple["Attribute"])
                            if "Entity" in a_tuple :
                                typeString += str(a_tuple["Entity"])
                            if "Label" in a_tuple :
                                typeString += str(a_tuple["Label"])
                            if "Unit" in a_tuple :
                                typeString += str(a_tuple["Unit"])
                            if "Time" in a_tuple :
                                typeString += str(a_tuple["Time"])
                            if "inRelationTo" in a_tuple :
                                typeString += str(a_tuple["inRelationTo"])
                            if "wasGeneratedBy" in a_tuple :
                                typeString += str(a_tuple["wasGeneratedBy"])
                            if "wasDerivedFrom" in a_tuple :
                                typeString += str(a_tuple["wasDerivedFrom"])
                            identifierString = hashlib.md5((str(row[col_headers.index(a_tuple["Column"])+1])+typeString).encode("utf-8")).hexdigest()
                            try :
                                if "Template" in a_tuple :
                                    template_term = extractTemplate(col_headers,row,a_tuple["Template"])
                                    termURI = "<" + prefixes[kb] + template_term + ">"
                                else :
                                    termURI = "<" + prefixes[kb] + a_tuple["Column"].replace(" ","_").replace(",","").replace("(","").replace(")","").replace("/","-").replace("\\","-") + "-" + identifierString + ">"
                                try :
                                    #print(termURI)
                                    #print("\n\n")
                                    assertionString += "\n    " + termURI + "\n        <" + rdf.type + ">    <" + prefixes[kb] + a_tuple["Column"].replace(" ","_").replace(",","").replace("(","").replace(")","").replace("/","-").replace("\\","-") + ">"
                                    if "Attribute" in a_tuple :
                                        if ',' in a_tuple["Attribute"] :
                                            attributes = parseString(a_tuple["Attribute"],',')
                                            for attribute in attributes :
                                                assertionString += " ;\n        <" + properties_tuple["Attribute"] + ">    " + attribute
                                        else :
                                            assertionString += " ;\n        <" + properties_tuple["Attribute"] + ">    " + a_tuple["Attribute"]
                                    if "Entity" in a_tuple :
                                        if ',' in a_tuple["Entity"] :
                                            entities = parseString(a_tuple["Entity"],',')
                                            for entity in entities :
                                                assertionString += " ;\n        <" + properties_tuple["Entity"] + ">    " + entity
                                        else :
                                            assertionString += " ;\n        <" + properties_tuple["Entity"] + ">    " + a_tuple["Entity"]
                                    if "isAttributeOf" in a_tuple :
                                        if checkImplicit(a_tuple["isAttributeOf"]) :
                                            v_id = assignVID(implicit_entry_tuples,timeline_tuple,a_tuple,"isAttributeOf", npubIdentifier)
                                            vTermURI = assignTerm(col_headers, "isAttributeOf", implicit_entry_tuples, a_tuple, row, v_id)
                                            assertionString += " ;\n        <" + properties_tuple["attributeOf"] + ">    " + vTermURI
                                            if a_tuple["isAttributeOf"] not in vref_list :
                                                vref_list.append(a_tuple["isAttributeOf"])
                                        elif checkTemplate(a_tuple["isAttributeOf"]):
                                            assertionString += " ;\n        <" + properties_tuple["attributeOf"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,a_tuple["isAttributeOf"])) + ">"
                                        else :
                                            assertionString += " ;\n        <" + properties_tuple["attributeOf"] + ">    " + convertImplicitToKGEntry(a_tuple["isAttributeOf"],identifierString)
                                    if "Unit" in a_tuple :
                                        if checkImplicit(a_tuple["Unit"]) :
                                            v_id = assignVID(implicit_entry_tuples,timeline_tuple,a_tuple,"Unit", npubIdentifier)
                                            vTermURI = assignTerm(col_headers, "Unit", implicit_entry_tuples, a_tuple, row, v_id)
                                            assertionString += " ;\n        <" + properties_tuple["Unit"] + ">    " + vTermURI
                                            if a_tuple["Unit"] not in vref_list :
                                                vref_list.append(a_tuple["Unit"])
                                        elif checkTemplate(a_tuple["Unit"]):
                                            assertionString += " ;\n        <" + properties_tuple["Unit"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,a_tuple["Unit"])) + ">"
                                        else :
                                            assertionString += " ;\n        <" + properties_tuple["Unit"] + ">    " + a_tuple["Unit"]
                                    if "Time" in a_tuple :
                                        if checkImplicit(a_tuple["Time"]) :
                                            foundBool = False
                                            for v_tuple in implicit_entry_tuples : # referenced in implicit list
                                                if v_tuple["Column"] == a_tuple["Time"]:
                                                    foundBool = True
                                            if(foundBool) :
                                                v_id = assignVID(implicit_entry_tuples,timeline_tuple,a_tuple,"Time", npubIdentifier)
                                                vTermURI = assignTerm(col_headers, "Time", implicit_entry_tuples, a_tuple, row, v_id)
                                                assertionString += " ;\n        <" + properties_tuple["Time"] + ">    " + vTermURI
                                            else : # Check timeline
                                                for t_tuple in timeline_tuple :
                                                    if t_tuple == a_tuple["Time"] :
                                                        vTermURI = convertImplicitToKGEntry(t_tuple)
                                                        assertionString += " ;\n        <" + properties_tuple["Time"] + ">    [     rdf:type    " + vTermURI + "     ] "
                                                    #if t_tuple["Column"] == a_tuple["Time"]:
                                            #if a_tuple["Time"] not in vref_list :
                                            #    vref_list.append(a_tuple["Time"])
                                        elif checkTemplate(a_tuple["Time"]):
                                            assertionString += " ;\n        <" + properties_tuple["Time"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,a_tuple["Time"])) + ">"
                                        else :
                                            assertionString += " ;\n        <" + properties_tuple["Time"] + ">    " + convertImplicitToKGEntry(a_tuple["Time"], identifierString)
                                    if "Label" in a_tuple :
                                        if ',' in a_tuple["Label"] :
                                            labels = parseString(a_tuple["Label"],',')
                                            for label in labels :
                                                assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + label + "\"^^xsd:string"
                                        else :
                                            assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + a_tuple["Label"] + "\"^^xsd:string"
                                    if "Comment" in a_tuple :
                                        assertionString += " ;\n        <" + properties_tuple["Comment"] + ">    \"" + a_tuple["Comment"] + "\"^^xsd:string"
                                    if "inRelationTo" in a_tuple :
                                        if checkImplicit(a_tuple["inRelationTo"]) :   
                                            v_id = assignVID(implicit_entry_tuples,timeline_tuple,a_tuple,"inRelationTo", npubIdentifier)
                                            vTermURI = assignTerm(col_headers, "inRelationTo", implicit_entry_tuples, a_tuple, row, v_id)
                                            if a_tuple["inRelationTo"] not in vref_list :
                                                vref_list.append(a_tuple["inRelationTo"])
                                            if "Relation" in a_tuple :
                                                assertionString += " ;\n        " + a_tuple["Relation"] + "    " + vTermURI
                                            elif "Role" in a_tuple :
                                                assertionString += " ;\n        <" + properties_tuple["Role"] + ">    [ <" + rdf.type + ">    " + a_tuple["Role"] + " ;\n            <" + properties_tuple["inRelationTo"] + ">    " + vTermURI + " ]"
                                            else :
                                                assertionString += " ;\n        <" + properties_tuple["inRelationTo"] + ">    " + vTermURI
                                        elif checkTemplate(a_tuple["inRelationTo"]):
                                            if "Relation" in a_tuple :
                                                assertionString += " ;\n        " + a_tuple["Relation"] + "    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,a_tuple["inRelationTo"])) + ">"
                                            elif "Role" in a_tuple :
                                                assertionString += " ;\n        <" + properties_tuple["Role"] + ">    [ <" + rdf.type + ">    " + a_tuple["Role"] + " ;\n            <" + properties_tuple["inRelationTo"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,a_tuple["inRelationTo"])) + "> ]"

                                            else:
                                                assertionString += " ;\n        <" + properties_tuple["inRelationTo"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,a_tuple["inRelationTo"])) + ">"
                                        else:
                                            if "Relation" in a_tuple :
                                                assertionString += " ;\n        " + a_tuple["Relation"] + "    " + convertImplicitToKGEntry(a_tuple["inRelationTo"], identifierString)
                                            elif "Role" in a_tuple :
                                                assertionString += " ;\n        <" + properties_tuple["Role"] + ">    [ <" + rdf.type + ">    " + a_tuple["Role"] + " ;\n            <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(a_tuple["inRelationTo"],identifierString) + " ]"
                                            else :
                                                assertionString += " ;\n        <" + properties_tuple["inRelationTo"] + ">    " + convertImplicitToKGEntry(a_tuple["inRelationTo"], identifierString)                       
                                except Exception as e:
                                    print("Error writing initial assertion elements: ")
                                    if hasattr(e, 'message'):
                                        print(e.message)
                                    else:
                                        print(e)
                                try :
                                    if row[col_headers.index(a_tuple["Column"])+1] != "" :
                                        #print(row[col_headers.index(a_tuple["Column"])])
                                        if cb_tuple != {} :
                                            if a_tuple["Column"] in cb_tuple :
                                                #print(a_tuple["Column"])
                                                for tuple_row in cb_tuple[a_tuple["Column"]] :
                                                    #print(tuple_row)
                                                    if ("Code" in tuple_row) and (str(tuple_row['Code']) == str(row[col_headers.index(a_tuple["Column"])+1]) ):
                                                        #print(tuple_row['Code'])
                                                        if ("Class" in tuple_row) and (tuple_row['Class'] != "") :
                                                            if ',' in tuple_row['Class'] :
                                                                classTerms = parseString(tuple_row['Class'],',')
                                                                for classTerm in classTerms :
                                                                    assertionString += " ;\n        <" + rdf.type + ">    " + convertImplicitToKGEntry(codeMapper(classTerm))
                                                            else :
                                                                assertionString += " ;\n        <" + rdf.type + ">    "+ convertImplicitToKGEntry(codeMapper(tuple_row['Class']))
                                                        if ("Resource" in tuple_row) and (tuple_row['Resource'] != "") :
                                                            if ',' in tuple_row['Resource'] :
                                                                classTerms = parseString(tuple_row['Resource'],',')
                                                                for classTerm in classTerms :
                                                                    assertionString += " ;\n        <" + rdf.type + ">    " + convertImplicitToKGEntry(codeMapper(classTerm))
                                                            else :
                                                                assertionString += " ;\n        <" + rdf.type + ">    " + convertImplicitToKGEntry(codeMapper(tuple_row['Resource']))
                                                        if ("Label" in tuple_row) and (tuple_row['Label'] != "") :
                                                            assertionString += " ;\n        <" + properties_tuple["Label"] + ">    \"" + tuple_row['Label'] + "\"^^xsd:string"
                                                        if ("Comment" in tuple_row) and (tuple_row['Comment'] != "") :
                                                            assertionString += " ;\n        <" + properties_tuple["Comment"] + ">    \"" + tuple_row['Comment'] + "\"^^xsd:string"
                                                        if ("Definition" in tuple_row) and (tuple_row['Definition'] != "") :
                                                            assertionString += " ;\n        <" + properties_tuple["Definition"] + ">    \"" + tuple_row['Definition'] + "\"^^xsd:string"
                                        #print(str(row[col_headers.index(a_tuple["Column"])]))
                                        try :
                                            if str(row[col_headers.index(a_tuple["Column"])+1]) == "nan" :
                                                pass
                                            # Check if Format was populated in the DM row of the current data point
                                            if ("Format" in a_tuple) and (a_tuple['Format'] != "") :
                                                # Check if an xsd prefix is included in the populated Format cell
                                                if("xsd:" in a_tuple['Format']):
                                                    assertionString += " ;\n        <" + properties_tuple["Value"] + ">    \"" + str(row[col_headers.index(a_tuple["Column"])+1]) + "\"^^" + a_tuple['Format']
                                                # If the Format cell is populated, but the xsd prefix isn't specified, do a string match over the set of primitive xsd types
                                                elif a_tuple['Format'] in xsd_datatype_list :
                                                    assertionString += " ;\n        <" + properties_tuple["Value"] + ">    \"" + str(row[col_headers.index(a_tuple["Column"])+1]) + "\"^^xsd:" + a_tuple['Format']
                                            # If the Format cell isn't populated, check is the data value is an integer
                                            elif str(row[col_headers.index(a_tuple["Column"])+1]).isdigit() :
                                                assertionString += " ;\n        <" + properties_tuple["Value"] + ">    \"" + str(row[col_headers.index(a_tuple["Column"])+1]) + "\"^^xsd:integer"
                                            # Next check if it is a float
                                            elif isfloat(str(row[col_headers.index(a_tuple["Column"])+1])) :
                                                assertionString += " ;\n        <" + properties_tuple["Value"] + ">    \"" + str(row[col_headers.index(a_tuple["Column"])+1]) + "\"^^xsd:float"
                                            # By default, assign 'xsd:string' as the datatype
                                            else :
                                                assertionString += " ;\n        <" + properties_tuple["Value"] + ">    \"" + str(row[col_headers.index(a_tuple["Column"])+1]).replace("\"","'") + "\"^^xsd:string"
                                        except Exception as e :
                                            print("Warning: unable to write value to assertion string:", row[col_headers.index(a_tuple["Column"])+1] + ": " + str(e))
                                    assertionString += " .\n"
                                except Exception as e:
                                    print("Error writing data value to assertion string:", row[col_headers.index(a_tuple["Column"])+1], ": " + str(e))
                                try :
                                    provenanceString += "\n    " + termURI + "\n        <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime"
                                    if "wasDerivedFrom" in a_tuple : 
                                        v_id = assignVID(implicit_entry_tuples,timeline_tuple,a_tuple,"wasDerivedFrom", npubIdentifier)
                                        if ',' in a_tuple["wasDerivedFrom"] :
                                            derivedFromTerms = parseString(a_tuple["wasDerivedFrom"],',')
                                            for derivedFromTerm in derivedFromTerms :
                                                if checkImplicit(derivedFromTerm) :
                                                    provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(derivedFromTerm, v_id)
                                                    if derivedFromTerm not in vref_list :
                                                        vref_list.append(derivedFromTerm)
                                                elif checkTemplate(derivedFromTerm):
                                                    provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,derivedFromTerm)) + ">"
                                                else :
                                                    provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(derivedFromTerm, identifierString)
                                        elif checkImplicit(a_tuple["wasDerivedFrom"]) :
                                            vTermURI = assignTerm(col_headers, "wasDerivedFrom", implicit_entry_tuples, a_tuple, row, v_id)
                                            provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + vTermURI
                                            if a_tuple["wasDerivedFrom"] not in vref_list :
                                                vref_list.append(a_tuple["wasDerivedFrom"])
                                        elif checkTemplate(a_tuple["wasDerivedFrom"]):
                                            provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,a_tuple["wasDerivedFrom"])) + ">"
                                        else :
                                            provenanceString += " ;\n        <" + properties_tuple["wasDerivedFrom"] + ">    " + convertImplicitToKGEntry(a_tuple["wasDerivedFrom"], identifierString)
                                    if "wasGeneratedBy" in a_tuple :
                                        v_id = assignVID(implicit_entry_tuples,timeline_tuple,a_tuple,"wasGeneratedBy", npubIdentifier)
                                        if ',' in a_tuple["wasGeneratedBy"] :
                                            generatedByTerms = parseString(a_tuple["wasGeneratedBy"],',')
                                            for generatedByTerm in generatedByTerms :
                                                if checkImplicit(generatedByTerm) :
                                                    provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(generatedByTerm, v_id)
                                                    if generatedByTerm not in vref_list :
                                                        vref_list.append(generatedByTerm)
                                                elif checkTemplate(generatedByTerm):
                                                    provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,generatedByTerm)) + ">"
                                                else:
                                                    provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(generatedByTerm, identifierString)
                                        elif checkImplicit(a_tuple["wasGeneratedBy"]) :
                                            vTermURI = assignTerm(col_headers, "wasGeneratedBy", implicit_entry_tuples, a_tuple, row, v_id)
                                            provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + vTermURI
                                            if a_tuple["wasGeneratedBy"] not in vref_list :
                                                vref_list.append(a_tuple["wasGeneratedBy"])
                                        elif checkTemplate(a_tuple["wasGeneratedBy"]):
                                            provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    <" + prefixes[kb] + str(extractExplicitTerm(col_headers,row,a_tuple["wasGeneratedBy"])) + ">"
                                        else :
                                            provenanceString += " ;\n        <" + properties_tuple["wasGeneratedBy"] + ">    " + convertImplicitToKGEntry(a_tuple["wasGeneratedBy"], identifierString)
                                        
                                    provenanceString += " .\n"
                                    if "hasPosition" in a_tuple :
                                        publicationInfoString += "\n    " + termURI + "\n        hasco:hasPosition    \"" + str(a_tuple["hasPosition"]) + "\"^^xsd:integer ."
                                except Exception as e:
                                    print("Error writing provenance or publication info: " + str(e))
                            except Exception as e:
                                print("Unable to process tuple" + a_tuple.__str__() + ": " + str(e))
                    try: 
                        for vref in vref_list :
                            [assertionString,provenanceString,publicationInfoString,vref_list] = writeImplicitEntry(assertionString,provenanceString,publicationInfoString,explicit_entry_tuples, implicit_entry_tuples, timeline_tuple, vref_list, vref, npubIdentifier, row, col_headers)
                    except Exception as e:
                        print("Warning: Something went wrong writing implicit entries: " + str(e))
                except Exception as e:
                    print("Error: Something went wrong when processing explicit tuples: " + str(e))
                    sys.exit(1)
                if nanopublication_option == "enabled" :
                    output_file.write("<" +  prefixes[kb] + "assertion-" + npubIdentifier + "> {" + assertionString + "\n}\n\n")
                    output_file.write("<" +  prefixes[kb] + "provenance-" + npubIdentifier + "> {")
                    provenanceString = "\n    <" +  prefixes[kb] + "assertion-" + npubIdentifier + ">    <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .\n" + provenanceString
                    output_file.write(provenanceString + "\n}\n\n")
                    output_file.write("<" +  prefixes[kb] + "pubInfo-" + npubIdentifier + "> {")
                    publicationInfoString = "\n    <" +  prefixes[kb] + "nanoPub-" + npubIdentifier + ">    <" +  prov.generatedAtTime + ">    \"" + "{:4d}-{:02d}-{:02d}".format(datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day) + "T" + "{:02d}:{:02d}:{:02d}".format(datetime.utcnow().hour,datetime.utcnow().minute,datetime.utcnow().second) + "Z\"^^xsd:dateTime .\n" + publicationInfoString
                    output_file.write(publicationInfoString + "\n}\n\n")
                else :
                    output_file.write(assertionString + "\n")
                    output_file.write(provenanceString + "\n")
        except Exception as e :
            print("Warning: Unable to process Data file: " + str(e))

def main():
    if 'dictionary' in config['Source Files'] :
        dm_fn = config['Source Files']['dictionary']
    else :
        print("Error: Dictionary Mapping file is not specified:" + str(e))
        sys.exit(1)

    if 'codebook' in config['Source Files'] :
        cb_fn = config['Source Files']['codebook']
    else :
        cb_fn = None

    if 'timeline' in config['Source Files'] :
        timeline_fn = config['Source Files']['timeline']
    else :
        timeline_fn = None

    if 'data_file' in config['Source Files'] :
        data_fn = config['Source Files']['data_file']
    else :
        data_fn = None

    global nanopublication_option
    if 'nanopublication' in config['Prefixes'] :
        nanopublication_option = config['Prefixes']['nanopublication']
    else :
        nanopublication_option = "enabled"

    if 'out_file' in config['Output Files']:
        out_fn = config['Output Files']['out_file']
    else: 
        if nanopublication_option == "enabled" :
            out_fn = "out.trig"
        else :
            out_fn = "out.ttl"

    if 'query_file' in config['Output Files'] :
        query_fn = config['Output Files']['query_file']
    else :    
        query_fn = "queryQ"

    if 'swrl_file' in config['Output Files'] :
        swrl_fn = config['Output Files']['swrl_file']
    else :    
        swrl_fn = "swrlModel"

    output_file = open(out_fn,"w")
    query_file = open(query_fn,"w")
    swrl_file = open(swrl_fn,"w")
    global prefixes
    prefixes = processPrefixes(output_file,query_file)

    global properties_tuple
    properties_tuple = processProperties()
    global cmap_fn
    [dm_fn, cb_fn, cmap_fn, timeline_fn] = processInfosheet(output_file, dm_fn, cb_fn, cmap_fn, timeline_fn)
    
    global explicit_entry_list
    global implicit_entry_list
    [explicit_entry_list,implicit_entry_list] = processDictionaryMapping(dm_fn)

    cb_tuple = processCodebook(cb_fn)
    timeline_tuple = processTimeline(timeline_fn)

    explicit_entry_tuples = writeExplicitEntryTuples(explicit_entry_list, output_file, query_file, swrl_file, dm_fn)
    implicit_entry_tuples = writeImplicitEntryTuples(implicit_entry_list, timeline_tuple, output_file, query_file, swrl_file, dm_fn)

    processData(data_fn, output_file, query_file, swrl_file, cb_tuple, timeline_tuple, explicit_entry_tuples, implicit_entry_tuples)

    output_file.close()
    query_file.close()
    swrl_file.close()

# Global Scope
# Used to prevent the creation of multiple URIs for hasco:Study, will need to address this in the future
studyRef = None
properties_tuple = {}
prefixes = {}

# Need to implement input flags rather than ordering
if (len(sys.argv) < 2) :
    print("Usage: python sdd2rdf.py <configuration_file>")
    sys.exit(1)

#file setup and configuration
config = configparser.ConfigParser()
try:
    config.read(sys.argv[1])
except Exception as e :
    print("Error: Unable to open configuration file:" + str(e))
    sys.exit(1)

#unspecified parameters in the config file should set the corresponding read string to ""

if 'base_uri' in config['Prefixes']:
    kb = config['Prefixes']['base_uri'] #+ ":" # may want to check if colon already exists in the specified base uri
else:
    kb=":"

if 'code_mappings' in config['Source Files'] :
    cmap_fn = config['Source Files']['code_mappings']
else :
    cmap_fn = None

[unit_code_list,unit_uri_list,unit_label_list] = processCodeMappings(cmap_fn) #must be global at the moment for code mapper to work..

explicit_entry_list = []
implicit_entry_list = []

if __name__ == "__main__":
    main()

