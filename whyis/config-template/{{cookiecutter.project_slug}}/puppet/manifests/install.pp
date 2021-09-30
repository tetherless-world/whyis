Exec { path => ["/usr/local/sbin","/usr/local/bin","/usr/sbin","/usr/bin","/bin"]}

include wget

# Install and uninstall packages
package { ["apache2-dev", "unzip", "zip", "default-jdk", "build-essential","automake",  "subversion", "git", "libblas3", "libblas-dev", "celeryd", "redis-server", "apache2", "libffi-dev", "libssl-dev", "maven", "libdb5.3-dev", "python3.7-dev"]:
  ensure => "installed"
} ->


# Flesh out the /data directory
file { "/data":
  ensure => directory,
  owner => "jetty"
} ->
file { "/data/nanopublications":
  ensure => directory,
  owner => "whyis",
  group      => 'whyis'
} ->
file { "/data/files":
  ensure => directory,
  owner => "whyis",
  group      => 'whyis'
} ->

# Set up the whyis Python virtual environment
python::pyvenv { '/apps/whyis/venv' :
  ensure       => present,
  version      => '3.7',
  systempkgs   => false,
  venv_dir     => '/apps/whyis/venv',
  owner        => 'whyis',
  group        => 'whyis',
} ->
python::pip { 'pip-upgrade' :
  pkgname       => 'pip',
  ensure        => 'latest',
  virtualenv    => '/apps/whyis/venv',
  owner         => 'whyis',
  group         => 'whyis',
  timeout       => 18000,
} ->
python::pip { 'pip-wheel' :
  pkgname       => 'wheel',
  ensure        => 'latest',
  virtualenv    => '/apps/whyis/venv',
  owner         => 'whyis',
  group         => 'whyis',
  timeout       => 18000,
} ->
python::requirements { '/apps/whyis/requirements/dev.txt' :
  virtualenv => '/apps/whyis/venv',
  owner      => 'whyis',
  group      => 'whyis',
  forceupdate => true,
  timeout       => 18000,
} ->
file { "/apps/.bash_profile" :
  owner => 'whyis',
  group => 'whyis',
  content => '
  source /apps/whyis/venv/bin/activate
  ',
} ->

# Set up celery
file { "/var/log/celery":
    owner => "whyis",
    ensure => directory,
    recurse => true,
    group => "whyis"
} ->
file { "/etc/default/celeryd":
  source => "/apps/whyis/puppet/files/etc/default/celeryd",
  owner => "root",
  group => "root",
  ensure => present
} ->

# Whyis log directory
file { "/var/log/whyis":
  ensure => directory,
  owner => "whyis",
  group => "whyis"
} ->

# Configure Apache
exec { "enable wsgi":
  command => "/apps/whyis/venv/bin/mod_wsgi-express module-config > /etc/apache2/mods-available/wsgi.load",
} ->
exec { "a2enmod wsgi":
  command => "a2enmod wsgi",
} ->
exec { "a2enmod headers":
  command => "a2enmod headers",
} ->
file { "/etc/apache2/sites-available/000-default.conf":
  ensure => present,
  source => "/apps/whyis/puppet/files/etc/apache2/sites-available/000-default.conf",
  owner => "root"
}


service { apache2:
    ensure => running,
    subscribe => [File["/etc/apache2/sites-available/000-default.conf"]],
}

service { redis-server:
    ensure => running,
    subscribe => [File["/etc/apache2/sites-available/000-default.conf"]],
}


service { jetty9:
    ensure => running,
    subscribe => [File["/usr/share/jetty9/webapps/blazegraph/WEB-INF/GraphStore.properties"]],
} ->
exec { "wait_for_blazegraph":
  command => "bash -c 'for i in 1 2 3 4 5; do curl -s http://localhost:8080 &>/dev/null && break || sleep 1; done'",
  user => "whyis",
  cwd => "/apps/whyis",
} ->
exec { "create_admin_namespace":
  command => "curl -X POST --data-binary @admin.properties -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /apps/whyis/admin_namespace.log",
  creates => "/apps/whyis/admin_namespace.log",
  user => "whyis",
  cwd => "/apps/whyis",
} ->
exec { "create_knowledge_namespace":
  command => "curl -X POST --data-binary @knowledge.properties -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /apps/whyis/knowledge_namespace.log",
  creates => "/apps/whyis/knowledge_namespace.log",
  user => "whyis",
  cwd => "/apps/whyis",
}

exec { "compile_java":
  command => "mvn -q clean compile assembly:single -PwhyisProfile",
  creates => "/apps/whyis/java_compile.log",
  user    => "whyis",
  cwd     => "/apps/whyis/whyis-java",
}

class { "nodejs":
  repo_url_suffix => "12.x",
} ->
exec { "install_js_dependencies":
  command => "npm install",
  creates => "/apps/whyis/js_install.log",
  user => "whyis",
  cwd => "/apps/whyis/static",
}  ->
exec { "compile_js":
  command => "npm run build",
  creates => "/apps/whyis/js_compile.log",
  user => "whyis",
  cwd => "/apps/whyis/static",
}


include java
