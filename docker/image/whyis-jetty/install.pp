Exec { path => ["/usr/local/sbin","/usr/local/bin","/usr/sbin","/usr/bin","/bin"]}

package { ["unzip",
           "jetty9"]:
  ensure => "installed",
} ->
file_line { "configure_jetty_java_options":
  path  => '/etc/default/jetty9',
  line  => 'JAVA_OPTIONS="-ea -Xmx4g -server -XX:+UseParallelOldGC -Djava.awt.headless=true -Dorg.eclipse.jetty.server.Request.maxFormContentSize=200000000"',
  match => 'JAVA_OPTIONS=',
} ->
file_line { "configure_jetty_host_options":
  path  => '/etc/default/jetty9',
  line  => 'JETTY_HOST=0.0.0.0',
  match => 'JETTY_HOST=',
} ->
file_line { "configure_java_home":
  path  => '/etc/default/jetty9',
  line  => 'JAVA_HOME=/usr/lib/jvm/default-java',
  match => 'JAVA_HOME=',
} ->
file { "/usr/share/jetty9/webapps/blazegraph":
  ensure => "directory",
} ->
exec { "unzip_blazegraph":
  command => "unzip -u /tmp/blazegraph.war",
  cwd => "/usr/share/jetty9/webapps/blazegraph",
  creates => "/usr/share/jetty9/webapps/blazegraph/WEB-INF/web.xml",
} -> 
file { "/data":
  ensure => directory,
  owner => "jetty"
} ->
file_line { "configure_blazegraph_rule_logging":
  path  => '/usr/share/jetty9/webapps/blazegraph/WEB-INF/classes/log4j.properties',
  line  => 'log4j.appender.ruleLog.File=/data/rules.log',
  match => 'rules\.log',
} ->
file_line { "configure_blazegraph_config_location":
  path => '/usr/share/jetty9/webapps/blazegraph/WEB-INF/web.xml',
  match => 'RWStore.properties</param-value>',
  line => '   <param-value>/usr/share/jetty9/webapps/blazegraph/WEB-INF/RWStore.properties</param-value>',
} ->
file { "/usr/share/jetty9/webapps/blazegraph/WEB-INF/RWStore.properties":
  content => '
  com.bigdata.journal.AbstractJournal.file=/data/blazegraph.jnl
  com.bigdata.journal.AbstractJournal.bufferMode=DiskRW
  com.bigdata.service.AbstractTransactionService.minReleaseAge=1
  com.bigdata.journal.Journal.groupCommit=true
  com.bigdata.btree.writeRetentionQueue.capacity=4000
  com.bigdata.btree.BTree.branchingFactor=128
  com.bigdata.journal.AbstractJournal.initialExtent=209715200
  com.bigdata.journal.AbstractJournal.maximumExtent=209715200
  com.bigdata.rdf.sail.truthMaintenance=false
  com.bigdata.rdf.store.AbstractTripleStore.quads=true
  com.bigdata.rdf.store.AbstractTripleStore.statementIdentifiers=false
  com.bigdata.rdf.store.AbstractTripleStore.textIndex=true
  com.bigdata.rdf.store.AbstractTripleStore.axiomsClass=com.bigdata.rdf.axioms.NoAxioms
  com.bigdata.namespace.kb.lex.com.bigdata.btree.BTree.branchingFactor=400
  com.bigdata.namespace.kb.spo.com.bigdata.btree.BTree.branchingFactor=1024',
} -> 
file { "/usr/share/jetty9/webapps/blazegraph/WEB-INF/GraphStore.properties":
  content => '
  com.bigdata.journal.AbstractJournal.file=/data/blazegraph.jnl
  com.bigdata.journal.AbstractJournal.bufferMode=DiskRW
  com.bigdata.service.AbstractTransactionService.minReleaseAge=1
  com.bigdata.journal.Journal.groupCommit=true
  com.bigdata.btree.writeRetentionQueue.capacity=4000
  com.bigdata.btree.BTree.branchingFactor=128
  com.bigdata.journal.AbstractJournal.initialExtent=209715200
  com.bigdata.journal.AbstractJournal.maximumExtent=209715200
  com.bigdata.rdf.sail.truthMaintenance=false
  com.bigdata.rdf.store.AbstractTripleStore.quads=true
  com.bigdata.rdf.store.AbstractTripleStore.statementIdentifiers=false
  com.bigdata.rdf.store.AbstractTripleStore.textIndex=true
  com.bigdata.rdf.store.AbstractTripleStore.axiomsClass=com.bigdata.rdf.axioms.NoAxioms
  com.bigdata.namespace.kb.lex.com.bigdata.btree.BTree.branchingFactor=400
  com.bigdata.namespace.kb.spo.com.bigdata.btree.BTree.branchingFactor=1024',
}

