FROM jetty:9.2-jre8

USER root
RUN apt-get update && apt-get install -y unzip

# With the blazegraph/ context
COPY ./resources/blazegraph.war /tmp/.

# Creates the directory
WORKDIR /var/lib/jetty/webapps/blazegraph

RUN unzip -u /tmp/blazegraph.war -d /var/lib/jetty/webapps/blazegraph

RUN mkdir -p /data &&\
	chown -R jetty /data
RUN sed -i 's/.*rules\.log.*/log4j.appender.rulelog.File=\/data\/rules.log/' ./WEB-INF/classes/log4j.properties

RUN printf 'com.bigdata.journal.AbstractJournal.file=/data/blazegraph.jnl\n\
com.bigdata.journal.AbstractJournal.bufferMode=DiskRW\n\
com.bigdata.service.AbstractTransactionService.minReleaseAge=1\n\
com.bigdata.journal.Journal.groupCommit=true\n\
com.bigdata.btree.writeRetentionQueue.capacity=4000\n\
com.bigdata.btree.BTree.branchingFactor=128\n\
com.bigdata.journal.AbstractJournal.initialExtent=209715200\n\
com.bigdata.journal.AbstractJournal.maximumExtent=209715200\n\
com.bigdata.rdf.sail.truthMaintenance=false\n\
com.bigdata.rdf.store.AbstractTripleStore.quads=true\n\
com.bigdata.rdf.store.AbstractTripleStore.statementIdentifiers=false\n\
com.bigdata.rdf.store.AbstractTripleStore.textIndex=true\n\
com.bigdata.rdf.store.AbstractTripleStore.axiomsClass=com.bigdata.rdf.axioms.NoAxioms\n\
com.bigdata.namespace.kb.lex.com.bigdata.btree.BTree.branchingFactor=400\n\
com.bigdata.namespace.kb.spo.com.bigdata.btree.BTree.branchingFactor=1024\n' > ./WEB-INF/RWStore.properties

RUN printf 'com.bigdata.journal.AbstractJournal.file=/data/blazegraph.jnl\n\
com.bigdata.journal.AbstractJournal.bufferMode=DiskRW\n\
com.bigdata.service.AbstractTransactionService.minReleaseAge=1\n\
com.bigdata.journal.Journal.groupCommit=true\n\
com.bigdata.btree.writeRetentionQueue.capacity=4000\n\
com.bigdata.btree.BTree.branchingFactor=128\n\
com.bigdata.journal.AbstractJournal.initialExtent=209715200\n\
com.bigdata.journal.AbstractJournal.maximumExtent=209715200\n\
com.bigdata.rdf.sail.truthMaintenance=false\n\
com.bigdata.rdf.store.AbstractTripleStore.quads=true\n\
com.bigdata.rdf.store.AbstractTripleStore.statementIdentifiers=false\n\
com.bigdata.rdf.store.AbstractTripleStore.textIndex=true\n\
com.bigdata.rdf.store.AbstractTripleStore.axiomsClass=com.bigdata.rdf.axioms.NoAxioms\n\
com.bigdata.namespace.kb.lex.com.bigdata.btree.BTree.branchingFactor=400\n\
com.bigdata.namespace.kb.spo.com.bigdata.btree.BTree.branchingFactor=1024\n' > ./WEB-INF/GraphStore.properties

RUN sed -i 's/.*RWStore.properties<\/param-value>.*/   <param-value>\/var\/lib\/jetty\/webapps\/blazegraph\/WEB-INF\/RWStore.properties<\/param-value>/' ./WEB-INF/web.xml

RUN mv /docker-entrypoint.sh /jetty-docker-entrypoint.sh
COPY /docker/image/whyis-blazegraph/docker-entrypoint.sh /docker-entrypoint.sh

USER jetty

ENV JAVA_OPTIONS="-ea -Xmx4g -server -XX:+UseParallelOldGC -Djava.awt.headless=true -Dorg.eclipse.jetty.server.Request.maxFormContentSize=200000000"

WORKDIR /var/lib/jetty
