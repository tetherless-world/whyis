#!/bin/sh

echo '<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
  <entry key="com.bigdata.rdf.sail.namespace">knowledge</entry>
  <entry key="com.bigdata.rdf.store.AbstractTripleStore.quads">true</entry>
  <entry key="com.bigdata.rdf.sail.truthMaintenance">false</entry>
  <entry key="com.bigdata.rdf.store.AbstractTripleStore.textIndex">true</entry>
</properties>
' | curl -v -X POST --data-binary @- --header 'Content-Type:application/xml' http://localhost:9999/blazegraph/namespace
