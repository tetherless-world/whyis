
file_line { "reconfigure_mod_wsgi":
  path  => "/apps/whyis/puppet/files/etc/apache2/sites-available/000-default.conf",
  line  => 'WSGIPythonHome /usr/bin/python3',
  match => 'WSGIPythonHome',
} ->
file { "/etc/apache2/sites-available/000-default.conf":
  ensure => present,
  source => "/apps/whyis/puppet/files/etc/apache2/sites-available/000-default.conf",
  owner => "root"
}

file { "/etc/default/celeryd":
  source => "/apps/whyis/docker/image/whyis/celeryd",
  owner => "root",
  group => "root",
  ensure => present,
}
