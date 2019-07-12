Exec { path => ["/usr/local/sbin","/usr/local/bin","/usr/sbin","/usr/bin","/bin"]}

class { 'python' :
  version    => 'python3.7',
  pip        => 'present',
  dev        => 'present',
  virtualenv => 'absent',
  gunicorn   => 'absent',
}

package { ["default-jdk",
           "build-essential",
           "automake",
           "libapache2-mod-wsgi-py3",
           "libblas3",
           "libblas-dev",
           "git",
           "celeryd",
           "apache2",
           "libffi-dev",
           "libssl-dev",
           "libdb5.3-dev"]:
  ensure => "installed",
} ->
group { 'whyis':
  ensure => 'present',
} ->
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
file { "/data":
  ensure => directory,
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
python::pip { 'pip-upgrade' :
  pkgname       => 'pip',
  ensure        => 'latest',
  pip_provider  => 'pip3',
  timeout       => 18000,
} ->
exec { "pip-install":
  command => "pip3 install -r requirements/dev.txt",
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
