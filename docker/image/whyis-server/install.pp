file { "/etc/apache2/sites-available/000-default.conf":
  ensure => present,
  source => "/apps/whyis/apache.conf",
  owner => "root",
}

file { "/etc/default/celeryd":
  source => "/apps/whyis/docker/image/whyis/celeryd",
  owner => "root",
  group => "root",
  ensure => present,
}
