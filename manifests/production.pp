Exec { path => ["/usr/local/sbin","/usr/local/bin","/usr/sbin","/usr/bin","/bin"]}


package { ["git", "python-dev", "python-pip", "python-pip-whl", "unzip", "zip", "openjdk-7-jdk", "build-essential","automake", "jetty8", "subversion", "libapache2-mod-wsgi", "npm", "nodejs", "nodejs-legacy", "maven", "libblas3", "libblas-dev"]:
  ensure => "installed"
} ->
exec { "fabric_dependencies":
  cwd => "/home/hbgd/hbgdki_ontology",
  timeout => 0,
  command => "pip install -r requirements.txt"
} ->
file { "/opt":
  ensure => "directory",
  owner => "hbgd"
} ->
vcsrepo { '/opt/csv2rdf4lod':
  ensure   => present,
  user => "hbgd",
  provider => git,
  source   => 'https://github.com/timrdf/csv2rdf4lod-automation.git'
} -> 
file_line { "configure_jetty_start":
  path  => '/etc/default/jetty8',
  line  => 'NO_START=0',
  match => 'NO_START=1',
} ->
file_line { "configure_jetty_java_options":
  path  => '/etc/default/jetty8',
  line  => 'JAVA_OPTIONS="-ea -Xmx4g -server -XX:+UseParallelOldGC -Djava.awt.headless=true -Dlinkipedia.index=/data/hbgd-index/knowledge_index -Dorg.eclipse.jetty.server.Request.maxFormContentSize=200000000"',
  match => 'JAVA_OPTIONS',
} ->
file_line { "configure_jetty_host_options":
  path  => '/etc/default/jetty8',
  line  => 'JETTY_HOST=0.0.0.0',
  match => 'JETTY_HOST',
} ->
file_line { "configure_java_home":
  path  => '/etc/default/jetty8',
  line  => 'JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64',
  match => 'JAVA_HOME',
} ->


vcsrepo { '/opt/linkipedia':
  ensure   => present,
  user => "hbgd",
  provider => git,
  source   => 'https://github.com/tetherless-world/linkipedia.git'
} ->
exec { "linkipedia build":
  cwd => "/opt/linkipedia",
  command => "mvn clean install package",
  user => hbgd,
  timeout => 0
} ->
exec { "deploy linkipedia jar":
  command => "cp /opt/linkipedia/linkipedia-web/target/linkipedia-web.war /usr/share/jetty8/webapps/linkipedia.war"
} ->


wget::fetch { "http://downloads.sourceforge.net/project/bigdata/bigdata/1.5.2/bigdata.war":
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
} ->
file { "/apps":
  ensure => "directory",
  owner => "hbgd"
} ->
file { "/apps/ontology_browser":
  ensure => "directory",
  owner => "hbgd"
} ->
exec { "install grunt":
  command => "npm install -g grunt-cli"
} ->
exec { "install bower":
  command => "npm install -g bower"
} ->
exec { "fabric_setup":
  cwd => "/home/hbgd/hbgdki_ontology",
  command => "fab setup",
  user => "hbgd"
} ->
file { "/etc/apache2/sites-available/000-default.conf":
  ensure => present,
  source => "/home/hbgd/hbgdki_ontology/hbgd/apache.conf",
  owner => "root"
}


service { apache2:
    ensure => running,
    subscribe => [File["/etc/apache2/sites-available/000-default.conf"]],
}


service { jetty8:
    ensure => running,
    subscribe => [File["/usr/share/jetty8/webapps/bigdata/WEB-INF/GraphStore.properties"]],
}

