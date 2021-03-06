Exec { path => ["/usr/local/sbin","/usr/local/bin","/usr/sbin","/usr/bin","/bin"]}

# jdk is required to install javabridge
package { ["unzip", "zip", "default-jdk", "build-essential", "automake", "jetty9", "subversion", "git",
  "libapache2-mod-wsgi-py3", "libblas3", "libblas-dev", "redis-server", "apache2", "libffi-dev", "libssl-dev"
  , "maven", "python3-dev", "python3-pip", "libdb5.3-dev", "sudo"]:
  ensure => "installed"
} ->
file_line { "configure_jetty_start":
  path  => '/etc/default/jetty9',
  line  => 'NO_START=0',
  match => 'NO_START=1',
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
file { "/etc/init.d/jetty9":
  ensure => file,
  source => "/apps/whyis/puppet/files/etc/init.d/jetty9",
  owner => "root",
} ->
file_line { "configure_java_home":
  path  => '/etc/default/jetty9',
  line  => 'JAVA_HOME=/usr/lib/jvm/default-java',
  match => 'JAVA_HOME=',
} ->
file { "/tmp/blazegraph.war":
  ensure => file,
  source => "/apps/whyis/puppet/files/usr/share/jetty9/webapps/blazegraph.war",
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
#com.bigdata.journal.AbstractJournal.initialExtent=209715200
com.bigdata.journal.AbstractJournal.maximumExtent=209715200
com.bigdata.rdf.sail.truthMaintenance=false
com.bigdata.rdf.store.AbstractTripleStore.quads=true
com.bigdata.rdf.store.AbstractTripleStore.statementIdentifiers=false
com.bigdata.rdf.store.AbstractTripleStore.textIndex=true
com.bigdata.rdf.store.AbstractTripleStore.axiomsClass=com.bigdata.rdf.axioms.NoAxioms
com.bigdata.namespace.kb.lex.com.bigdata.btree.BTree.branchingFactor=400
com.bigdata.namespace.kb.spo.com.bigdata.btree.BTree.branchingFactor=1024',
} ->
group { 'whyis':
    ensure => 'present',
}
user { 'whyis':
  ensure => present,
  password => '*',
  home => '/apps',
  shell => '/bin/bash',
  gid => 'whyis'
} ->
file { "/apps":
  ensure => "directory",
  owner => "whyis",
  group => "whyis"
} ->
file { "/data/nanopublications":
  ensure => directory,
  owner => "whyis"
} ->
file { "/data/files":
  ensure => directory,
  owner => "whyis"
} ->
file { "/var/log/celery":
    owner => "whyis",
    ensure => directory,
    recurse => true,
    group => "whyis",
} ->
exec { "a2enmod wsgi":
  command => "a2enmod wsgi",
} -> 
exec { "a2enmod headers":
  command => "a2enmod headers",
} -> 
file { "/var/log/whyis":
  ensure => directory,
  owner => "whyis",
  group => "whyis",
}

# Register the generic celery daemon service
file { "/etc/init.d/celeryd":
  ensure => file,
  source => "/apps/whyis/puppet/files/etc/init.d/celeryd",
  mode => "0744",
  owner => "root"
}

# Docker does not like ::1
file_line { "reconfigure_redis_bind":
  path  => '/etc/redis/redis.conf',
  line => "bind 127.0.0.1",
  match => "^bind 127.0.0.1 ::1",
  subscribe => [Package["redis-server"]]
}
