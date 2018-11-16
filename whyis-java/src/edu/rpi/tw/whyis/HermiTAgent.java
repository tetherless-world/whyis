package edu.rpi.tw.whyis;

//import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.Instant;

import org.semanticweb.HermiT.Reasoner;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;

public class HermiTAgent {

    public static void main(String[] args) throws Exception {
        HermiTAgent.reason();
    }

    public static String reason() throws Exception {
        // First, we create an OWLOntologyManager object. The manager will load and save ontologies.
        OWLOntologyManager m=OWLManager.createOWLOntologyManager();
        // We use the OWL API to load the Pizza ontology.
        OWLOntology o=m.loadOntologyFromOntologyDocument(IRI.create("https://protege.stanford.edu/ontologies/pizza/pizza.owl"));
        //OWLOntology o=m.loadOntologyFromOntologyDocument(new File("/apps/hermit/xacml-core2.rdf"));
        // Now, we instantiate HermiT by creating an instance of the Reasoner class in the package org.semanticweb.He$
        Reasoner hermit=new Reasoner(o);
        // Finally, we output whether the ontology is consistent.
        String msg = String.valueOf(hermit.isConsistent());
        msg = Instant.now().toString() + "::: " + msg + "\n";
        System.out.print(msg);
        Files.write(Paths.get("/apps/hermit.log"), msg.getBytes());
        return String.valueOf(hermit.isConsistent());
    }
}
