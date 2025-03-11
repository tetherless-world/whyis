.. _sdds:

Uploading and Processing SDDs
=============================

This guide explains how to upload and process SDDs using the SDDAgent.

1. **Prepare your files**: 

Your data file will need to conform to some basic requirements:

    - The data file should be in a tabular format using CSV or Excel.
    - The data file should have a single header row with no extra rows before the header.

The SDD file should be in XLSX format and should conform to the SDD standard as detailed at `SDD website <https://tetherless-world.github.io/sdd>`.

2. **Upload the SDD and Data**:
Note that there can be multiple data files for a single SDD, and multiple SDDs per data file, interpreting different parts of the file. 
The simple case is of one SDD and one data file.
Data files need to be uploaded as part of a DCat dataset, so the easiest way to start is to visit a url in Whyis like "http://localhost:5000/dataset/example_1".

    - When you're logged in, each page has an "Upload" button that will let you select multiple files to upload.
    - Select the "Dataset" file type and upload.

3. **Give the SDD the correct type**:
    - From the dataset page, select the menu for the SDD file and click "Add Type".
    - Add the type "http://purl.org/twc/sdd/SemanticDataDictionary". If the `SDD Ontology<https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/refs/heads/master/sdd-ontology.ttl>` has been loaded, you can just search for "Semantic Data Dictionary".

4. **Add a delimiter to the data file**:
    - From the dataset page, select the menu for the data file and clicke "Add Attribute".
    - Add an attribute with the predicate "http://www.w3.org/ns/csvw#delimiter" (if the `SDD Ontology<https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/refs/heads/master/sdd-ontology.ttl>` has been loaded, you can just search for "delimiter") and the value of the delimiter character, which is usually ','.

5. **Add a URI prefix to the dataset**:
    - From the dataset page, select the menu for the dataset and click "Add Attribute".
    - Add an attribute with the predicate "http://rdfs.org/ns/void#uriSpace" and the value of the URI prefix for the data file. If the `SDD Ontology<https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/refs/heads/master/sdd-ontology.ttl>` has been loaded, you can just search for "uri space".

6. **Link the data file to the SDD**:
    - From the dataset page, select the menu for the data file and click "Add Link".
    - Add a link with the predicate "http://purl.org/dc/terms/conformsTo". Select the SDD file to link to the data file. If the `SDD Ontology<https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/refs/heads/master/sdd-ontology.ttl>` has been loaded, you can just search for "conforms to".

At this point, the SDDAgent will process the SDD and data file to compile the SDD as a SETL script.
The SETLr agent will in turn generate the RDF triples from the SETL script in a new nanopublication.

For more information on SDDs, visit the `SDD website <https://tetherless-world.github.io/sdd>`_.
