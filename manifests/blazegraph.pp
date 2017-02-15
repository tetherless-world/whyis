Exec { path => ["/usr/local/sbin","/usr/local/bin","/usr/sbin","/usr/bin","/bin"]}


package { ["unzip", "zip", "openjdk-7-jdk", "build-essential","automake", "jetty8", "subversion"]:
  ensure => "installed"
} ->
file_line { "configure_jetty_start":
  path  => '/etc/default/jetty8',
  line  => 'NO_START=0',
  match => 'NO_START=1',
} ->
file_line { "configure_jetty_java_options":
  path  => '/etc/default/jetty8',
  line  => 'JAVA_OPTIONS="-ea -Xmx4g -server -XX:+UseParallelOldGC -Djava.awt.headless=true -Dorg.eclipse.jetty.server.Request.maxFormContentSize=200000000"',
  match => 'JAVA_OPTIONS=',
} ->
file_line { "configure_jetty_host_options":
  path  => '/etc/default/jetty8',
  line  => 'JETTY_HOST=0.0.0.0',
  match => 'JETTY_HOST=',
} ->
file_line { "configure_java_home":
  path  => '/etc/default/jetty8',
  line  => 'JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64',
  match => 'JAVA_HOME=',
} -> wget::fetch { "http://downloads.sourceforge.net/project/bigdata/bigdata/2.1.4/bigdata.war":
  destination => "/tmp/bigdata.war",
  timeout => 0
} ->
file { "/usr/share/jetty8/webapps/bigdata":
  ensure => "directory",
} ->
exec { "unzip_bigdata":
  command => "unzip -u /tmp/bigdata.war",
  cwd => "/usr/share/jetty8/webapps/bigdata",
} -> 
file { "/data":
  ensure => directory,
  owner => "jetty"
} ->
file_line { "configure_bigdata_rule_logging":
  path  => '/usr/share/jetty8/webapps/bigdata/WEB-INF/classes/log4j.properties',
  line  => 'log4j.appender.ruleLog.File=/data/rules.log',
  match => 'rules\.log',
} ->
file_line { "configure_bigdata_config_location":
  path => '/usr/share/jetty8/webapps/bigdata/WEB-INF/web.xml',
  match => 'RWStore.properties</param-value>',
  line => '   <param-value>/usr/share/jetty8/webapps/bigdata/WEB-INF/RWStore.properties</param-value>',
} ->
file { "/usr/share/jetty8/webapps/bigdata/WEB-INF/RWStore.properties":
  content => '
com.bigdata.journal.AbstractJournal.file=/data/bigdata.jnl
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
file { "/usr/share/jetty8/webapps/bigdata/WEB-INF/GraphStore.properties":
  content => '
com.bigdata.journal.AbstractJournal.file=/data/bigdata.jnl
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

service { jetty8:
    ensure => running,
    subscribe => [File["/usr/share/jetty8/webapps/bigdata/WEB-INF/GraphStore.properties"]],
}

