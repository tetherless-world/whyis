Exec { path => ["/usr/local/sbin","/usr/local/bin","/usr/sbin","/usr/bin","/bin"]}

class { 'python' :
  version    => 'system',
  pip        => 'present',
  dev        => 'present',
  virtualenv => 'present',
  gunicorn   => 'absent',
}

package { ["unzip", "zip", "default-jdk", "build-essential","automake", "jetty8", "subversion", "git", "libapache2-mod-wsgi", "libblas3", "libblas-dev", "celeryd", "redis-server", "apache2", "libffi-dev", "libssl-dev"]:
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
} -> wget::fetch { "https://github.com/tetherless-world/satoru/raw/master/resources/blazegraph.war":
  destination => "/tmp/blazegraph.war",
  timeout => 0
} ->
file { "/usr/share/jetty8/webapps/blazegraph":
  ensure => "directory",
} ->
exec { "unzip_blazegraph":
  command => "unzip -u /tmp/blazegraph.war",
  cwd => "/usr/share/jetty8/webapps/blazegraph",
  creates => "/usr/share/jetty8/webapps/blazegraph/WEB-INF/web.xml",
} -> 
file { "/data":
  ensure => directory,
  owner => "jetty"
} ->
file_line { "configure_blazegraph_rule_logging":
  path  => '/usr/share/jetty8/webapps/blazegraph/WEB-INF/classes/log4j.properties',
  line  => 'log4j.appender.ruleLog.File=/data/rules.log',
  match => 'rules\.log',
} ->
file_line { "configure_blazegraph_config_location":
  path => '/usr/share/jetty8/webapps/blazegraph/WEB-INF/web.xml',
  match => 'RWStore.properties</param-value>',
  line => '   <param-value>/usr/share/jetty8/webapps/blazegraph/WEB-INF/RWStore.properties</param-value>',
} ->
file { "/usr/share/jetty8/webapps/blazegraph/WEB-INF/RWStore.properties":
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
file { "/usr/share/jetty8/webapps/blazegraph/WEB-INF/GraphStore.properties":
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
group { 'satoru':
    ensure => 'present',
}
user { 'satoru':
  ensure => present,
  password => '*',
  home => '/apps',
  gid => 'satoru'
} ->
file { "/apps":
  ensure => "directory",
  owner => "satoru"
} ->
file { "/data/nanopublications":
  ensure => directory,
  owner => "satoru"
} ->
vcsrepo { '/apps/satoru':
  ensure   => present,
  provider => git,
  source   => 'https://github.com/tetherless-world/satoru.git',
  user     => 'satoru'
} ->
python::virtualenv { '/apps/satoru/venv' :
  ensure       => present,
  version      => 'system',
  systempkgs   => false,
  distribute   => false,
  venv_dir     => '/apps/satoru/venv',
  owner        => 'satoru',
  cwd          => '/apps/satoru',
  timeout      => 0,
} ->
python::pip { 'pip-upgrade' :
  pkgname       => 'pip',
  ensure        => 'latest',
  virtualenv    => '/apps/satoru/venv',
  owner         => 'satoru',
  timeout       => 0,
} ->
python::requirements { '/apps/satoru/requirements/dev.txt' :
  virtualenv => '/apps/satoru/venv',
  owner      => 'satoru',
} ->
file { "/var/log/celery":
    owner => "satoru",
    ensure => directory,
    recurse => true,
    group => "satoru",
} ->
file { "/etc/default/celeryd":
  source => "/apps/satoru/resources/celeryd",
  ensure => present
} ->
exec { "a2enmod wsgi":
  command => "a2enmod wsgi",
} -> 
exec { "a2enmod headers":
  command => "a2enmod headers",
} -> 
file { "/var/log/satoru":
  ensure => directory,
  owner => "satoru",
  group => "satoru",
} ->
file { "/apps/satoru/config.py":
  ensure => present,
  source => "/apps/satoru/config-defaults.py",
  owner => "satoru"
} ->
file { "/etc/apache2/sites-available/000-default.conf":
  ensure => present,
  source => "/apps/satoru/apache.conf",
  owner => "root"
}


service { apache2:
    ensure => running,
    subscribe => [File["/etc/apache2/sites-available/000-default.conf"]],
}

service { redis-server:
    ensure => running,
    subscribe => [File["/apps/satoru/config.py"]],
}

service { celeryd:
    ensure => running,
    subscribe => [File["/apps/satoru/config.py"]],
}

service { celerybeat:
    ensure => running,
    subscribe => [File["/apps/satoru/config.py"]],
}

service { jetty8:
    ensure => running,
    subscribe => [File["/usr/share/jetty8/webapps/blazegraph/WEB-INF/GraphStore.properties"]],
} ->
exec { "create_admin_namespace":
  command => "curl -X POST --data-binary @admin.properties -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > admin_namespace.log",
  creates => "/apps/satoru/admin_namespace.log",
  user => "satoru",
  cwd => "/apps/satoru",
} -> 
exec { "create_knowledge_namespace":
  command => "curl -X POST --data-binary @knowledge.properties -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /apps/satoru/knowledge_namespace.log",
  creates => "/apps/satoru/knowledge_namespace.log",
  user => "satoru",
  cwd => "/apps/satoru",
}

