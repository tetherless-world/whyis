Exec { path => ["/usr/local/sbin","/usr/local/bin","/usr/sbin","/usr/bin","/bin"]}

$whyis_branch_ = $whyis_branch ? { "" => "release", default => $whyis_branch }
notice("Whyis branch: ${whyis_branch_}")

class { 'python' :
  version    => 'system',
  pip        => 'present',
  dev        => 'present',
  virtualenv => 'present',
  gunicorn   => 'absent',
}

service { jetty8:
    ensure => stopped,
    subscribe => [Package["jetty8"]],

}

package { ["unzip", "zip", "default-jdk", "build-essential","automake", "jetty9", "subversion", "git", "libapache2-mod-wsgi-py3", "libblas3", "libblas-dev", "celeryd", "redis-server", "apache2", "libffi-dev", "libssl-dev", "maven", "python3-dev", "libdb5.3-dev"]:
  ensure => "installed"
} ->
package { "jetty8":
  ensure => "absent",
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
  content => '
#!/bin/sh -e
#
# /etc/init.d/jetty9 -- startup script for Jetty 9
#
# Written by Philipp Meier <meier@meisterbohne.de>
# Modified for Jetty 6 by Ludovic Claude <ludovic.claude@laposte.net>
# Modified for Jetty 8 by Jakub Adam <jakub.adam@ktknet.cz>
# Modified for Jetty 9 by Emmanuel Bourg <ebourg@apache.org>
#
### BEGIN INIT INFO
# Provides:          jetty9
# Required-Start:    $local_fs $remote_fs $network
# Required-Stop:     $local_fs $remote_fs $network
# Should-Start:      $named
# Should-Stop:       $named
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start Jetty
# Description:       Start Jetty HTTP server and servlet container.
### END INIT INFO

# Configuration files
#
# /etc/default/jetty9
#   If it exists, this is read at the start of script. It may perform any
#   sequence of shell commands, like setting relevant environment variables.
#
# /etc/jetty9/jetty.conf
#   If found, the file will be used as this script's configuration.
#   Each line in the file may contain:
#     - A comment denoted by the pound (#) sign as first non-blank character.
#     - The path to a regular file, which will be passed to jetty as a
#       config.xml file.
#     - The path to a directory. Each *.xml file in the directory will be
#       passed to jetty as a config.xml file.
#
#   The files will be checked for existence before being passed to jetty.
#
# /etc/jetty9/jetty.xml
#   If found, used as this script's configuration file, but only if
#   /etc/jetty9/jetty.conf was not present. See above.
#
# Configuration variables (to define in /etc/default/jetty9)
#
# JAVA_HOME
#   Home of Java installation.
#
# JAVA_OPTIONS
#   Extra options to pass to the JVM
#
# JETTY_ARGS
#   The default arguments to pass to jetty.
#
# JETTY_USER
#   if set, then used as a username to run the server as

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
VERSION=9
NAME=jetty$VERSION
DESC="Jetty $VERSION Servlet Engine"
JETTY_HOME=/usr/share/$NAME
LOGDIR="/var/log/$NAME"
START_JAR="$JETTY_HOME/start.jar"
DEFAULT=/etc/default/$NAME
JVM_TMP=/var/cache/$NAME/tmp

if [ `id -u` -ne 0 ]; then
	echo "You need root privileges to run this script"
	exit 1
fi

# Make sure jetty is started with system locale
if [ -r /etc/default/locale ]; then
	. /etc/default/locale
	export LANG
fi

. /lib/lsb/init-functions

if [ -r /etc/default/rcS ]; then
	. /etc/default/rcS
fi


# The following variables can be overwritten in /etc/default/jetty

# Whether to start jetty (as a daemon) or not
NO_START=0

# Run Jetty as this user ID (default: jetty)
# Set this to an empty string to prevent Jetty from starting automatically
JETTY_USER=jetty

# Additional arguments to pass to Jetty
JETTY_ARGS=

JETTY_STATE=/var/lib/jetty$VERSION/jetty.state

# Extra options to pass to the JVM
# Set java.awt.headless=true if JAVA_OPTIONS is not set so the
# Xalan XSL transformer can work without X11 display on JDK 1.4+
# It also sets the maximum heap size to 256M to deal with most cases.
JAVA_OPTIONS="-Xmx256m -Djava.awt.headless=true"

# This function sets the variable JDK_DIRS
find_jdks()
{
    for java_version in 9 8 7
    do
        for jvmdir in /usr/lib/jvm/java-${java_version}-openjdk-* \
                      /usr/lib/jvm/jdk-${java_version}-oracle-* \
                      /usr/lib/jvm/jre-${java_version}-oracle-* \
                      /usr/lib/jvm/java-${java_version}-oracle
        do
            if [ -d "${jvmdir}" ]
            then
                JDK_DIRS="${JDK_DIRS} ${jvmdir}"
            fi
        done
    done

    # Add the paths for the JVMs packaged by the older versions of java-package (<< 0.52 as in Wheezy and Trusty)
    JDK_DIRS="${JDK_DIRS} /usr/lib/jvm/j2re1.7-oracle /usr/lib/jvm/j2sdk1.7-oracle"
}

# The first existing directory is used for JAVA_HOME (if JAVA_HOME is not
# defined in $DEFAULT)
JDK_DIRS="/usr/lib/jvm/default-java"
find_jdks

# Timeout in seconds for the shutdown of all webapps
JETTY_SHUTDOWN=30

# Jetty uses a directory to store temporary files like unpacked webapps
JETTY_TMP=/var/cache/jetty$VERSION/data

# End of variables that can be overwritten in /etc/default/jetty

# overwrite settings from default file
if [ -f "$DEFAULT" ]; then
	. "$DEFAULT"
fi

# Check whether jetty is still installed (it might not be if this package was
# removed and not purged)
if [ ! -r "$START_JAR" ]; then
	log_failure_msg "$NAME is not installed"
	exit 1
fi

# Check whether startup has been disabled
if [ "$NO_START" != "0" -a "$1" != "stop" ]; then
	[ "$VERBOSE" != "no" ] && log_failure_msg "Not starting jetty - edit /etc/default/jetty$VERSION and change NO_START to be 0 (or comment it out)."
	exit 0
fi

if [ -z "$JETTY_USER" ]; then
	log_failure_msg "Not starting/stopping $DESC as configured"
	log_failure_msg "(JETTY_USER is empty in /etc/default/jetty$VERSION)."
	exit 0
fi

# Look for the right JVM to use
for jdir in $JDK_DIRS; do
	if [ -d "$jdir" -a -z "${JAVA_HOME}" ]; then
		JAVA_HOME="$jdir"
	fi
done
export JAVA_HOME

export JAVA="$JAVA_HOME/bin/java"

JAVA_OPTIONS="$JAVA_OPTIONS \
	-Djava.io.tmpdir=$JETTY_TMP \
	-Djava.library.path=/usr/lib \
	-Djetty.home=$JETTY_HOME \
	-Djetty.logs=$LOGDIR \
	-Djetty.state=$JETTY_STATE"

export JAVA_OPTIONS

# Define other required variables
PIDFILE="/var/run/$NAME.pid"
WEBAPPDIR="$JETTY_HOME/webapps"
ROTATELOGS=/usr/sbin/rotatelogs

##################################################
# Check for JAVA_HOME
##################################################
if [ -z "$JAVA_HOME" ]; then
	log_failure_msg "Could not start $DESC because no Java Runtime Environment (JRE)"
	log_failure_msg "was found. Please download and install Java 7 or higher and set"
	log_failure_msg "JAVA_HOME in /etc/default/jetty$VERSION to the JDK's installation directory."
	exit 0
fi

JETTY_CONF=/etc/jetty$VERSION/jetty.conf
CONFIG_LINES=$(cat $JETTY_CONF | grep -v "^[[:space:]]*#" | tr "\n" " ")

##################################################
# Get the list of config.xml files from jetty.conf
##################################################
if [ ! -z "${CONFIG_LINES}" ]
then
  for CONF in ${CONFIG_LINES}
  do
    if [ ! -r "$CONF" ] && [ ! -r "$JETTY_HOME/etc/$CONF" ]
    then
      log_warning_msg "WARNING: Cannot read '$CONF' specified in '$JETTY_CONF'"
    elif [ -f "$CONF" ] || [ -f "$JETTY_HOME/etc/$CONF" ]
    then
      # assume it's a configure.xml file
      CONFIGS="$CONFIGS $CONF"
    elif [ -d "$CONF" ]
    then
      # assume it's a directory with configure.xml files
      # for example: /etc/jetty.d/
      # sort the files before adding them to the list of CONFIGS
      XML_FILES=`ls ${CONF}/*.xml | sort | tr "\n" " "`
      for FILE in ${XML_FILES}
      do
         if [ -r "$FILE" ] && [ -f "$FILE" ]
         then
            CONFIGS="$CONFIGS $FILE"
         else
           log_warning_msg "WARNING: Cannot read '$FILE' specified in '$JETTY_CONF'"
         fi
      done
    else
      log_warning_msg "WARNING: Don''t know what to do with '$CONF' specified in '$JETTY_CONF'"
    fi
  done
fi

#####################################################
# Run the standard server if there's nothing else to run
#####################################################
if [ -z "$CONFIGS" ]
then
	CONFIGS="/etc/jetty$VERSION/jetty-logging.xml /etc/jetty$VERSION/jetty-started.xml"
fi

##################################################
# Do the action
##################################################
case "$1" in
  start)
	log_daemon_msg "Starting $DESC" "$NAME"
	if start-stop-daemon --quiet --test --start --pidfile "$PIDFILE" \
	                --user "$JETTY_USER" --startas "$JAVA" > /dev/null; then

		if [ -f $PIDFILE ] ; then
			log_warning_msg "$PIDFILE exists, but jetty was not running. Ignoring $PIDFILE"
		fi

		if [ -s "$LOGDIR/out.log" ]; then
			log_progress_msg "Rotate logs"
			$ROTATELOGS "$LOGDIR/out.log" 86400 \
				< "$LOGDIR/out.log" || true
		fi
		> "$LOGDIR/out.log"
		chown -R $JETTY_USER:adm "$LOGDIR"

		# Remove / recreate JETTY_TMP directory
		rm -rf "$JETTY_TMP"
		mkdir "$JETTY_TMP" || {
			log_failure_msg "could not create $DESC temporary directory at $JETTY_TMP"
			exit 1
		}
		chown $JETTY_USER "$JETTY_TMP"

		# Remove / recreate JVM_TMP directory
		rm -rf "$JVM_TMP"
		mkdir "$JVM_TMP" || {
			log_failure_msg "could not create JVM temporary directory at $JVM_TMP"
			exit 1
		}
		chown $JETTY_USER "$JVM_TMP"
		cd "$JVM_TMP"

		JETTY_CMD="$JAVA $JAVA_OPTIONS -jar $START_JAR $JETTY_ARGS --daemon $CONFIGS"

		AUTHBIND_COMMAND=""
		if [ "$AUTHBIND" = "yes" ]; then
			if [ ! -f "/usr/bin/authbind" ]; then
				log_failure_msg "Authbind is not installed, please run 'apt-get install authbind' and retry"
				exit 1
			fi

			AUTHBIND_COMMAND="/usr/bin/authbind --deep /bin/bash -c "
			JETTY_CMD="'$JETTY_CMD'"
		fi

		start-stop-daemon --start --pidfile "$PIDFILE" --chuid "$JETTY_USER" \
		    --chdir "$JETTY_HOME" --background --make-pidfile -x /bin/bash -- -c \
		    "$AUTHBIND_COMMAND $JETTY_CMD"

		sleep 5
		if start-stop-daemon --test --start --pidfile "$PIDFILE" \
			--user $JETTY_USER --exec "$JAVA" >/dev/null; then
			log_end_msg 0
		else
			log_end_msg 1
		fi

	else
		log_warning_msg "(already running)."
		log_end_msg 0
		exit 1
	fi
	;;

  stop)
	log_daemon_msg "Stopping $DESC" "$NAME"

	if start-stop-daemon --quiet --test --start --pidfile "$PIDFILE" \
		--user "$JETTY_USER" --startas "$JAVA" > /dev/null; then
		if [ -x "$PIDFILE" ]; then
			log_warning_msg "(not running but $PIDFILE exists)."
		else
			log_warning_msg "(not running)."
		fi
	else
		start-stop-daemon --quiet --stop \
			--pidfile "$PIDFILE" --user "$JETTY_USER" \
			--startas "$JAVA" > /dev/null
		while ! start-stop-daemon --quiet --test --start \
			  --pidfile "$PIDFILE" --user "$JETTY_USER" \
			  --startas "$JAVA" > /dev/null; do
			sleep 1
			log_progress_msg "."
			JETTY_SHUTDOWN=`expr $JETTY_SHUTDOWN - 1` || true
			if [ $JETTY_SHUTDOWN -ge 0 ]; then
				start-stop-daemon --oknodo --quiet --stop \
					--pidfile "$PIDFILE" --user "$JETTY_USER" \
					--startas "$JAVA"
			else
				log_progress_msg " (killing) "
				start-stop-daemon --stop --signal 9 --oknodo \
					--quiet --pidfile "$PIDFILE" \
					--user "$JETTY_USER"
			fi
		done
		rm -f "$PIDFILE"
		rm -rf "$JVM_TMP"
		rm -rf "$JETTY_TMP/*"
		log_end_msg 0
	fi
	;;

  status)
	if start-stop-daemon --quiet --test --start --pidfile "$PIDFILE" \
		--user "$JETTY_USER" --startas "$JAVA" > /dev/null; then

		if [ -f "$PIDFILE" ]; then
		    log_success_msg "$DESC is not running, but pid file exists."
			exit 1
		else
		    log_success_msg "$DESC is not running."
			exit 3
		fi
	else
		log_success_msg "$DESC is running with pid `cat $PIDFILE`"
	fi
	;;

  restart|force-reload)
	if ! start-stop-daemon --quiet --test --start --pidfile "$PIDFILE" \
		--user "$JETTY_USER" --startas "$JAVA" > /dev/null; then
		$0 stop $*
		sleep 1
	fi
	$0 start $*
	;;

  try-restart)
	if start-stop-daemon --quiet --test --start --pidfile "$PIDFILE" \
		--user "$JETTY_USER" --startas "$JAVA" > /dev/null; then
		$0 start $*
	fi
	;;

  check)
	log_success_msg "Checking arguments for Jetty: "
	log_success_msg ""
	log_success_msg "PIDFILE        =  $PIDFILE"
	log_success_msg "JAVA_OPTIONS   =  $JAVA_OPTIONS"
	log_success_msg "JAVA           =  $JAVA"
	log_success_msg "JETTY_USER     =  $JETTY_USER"
	log_success_msg "ARGUMENTS      =  $ARGUMENTS"

	if [ -f $PIDFILE ]
	then
		log_success_msg "$DESC is running with pid `cat $PIDFILE`"
		exit 0
	fi
	exit 1
	;;

  *)
	log_success_msg "Usage: $0 {start|stop|restart|force-reload|try-restart|status|check}"
	exit 1
	;;
esac

exit 0',
} ->
file_line { "configure_java_home":
  path  => '/etc/default/jetty9',
  line  => 'JAVA_HOME=/usr/lib/jvm/default-java',
  match => 'JAVA_HOME=',
} -> wget::fetch { "https://github.com/tetherless-world/whyis/raw/release/resources/blazegraph.war":
  destination => "/tmp/blazegraph.war",
  timeout => 0
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
vcsrepo { '/apps/whyis':
  ensure   => present,
  provider => git,
  source   => 'https://github.com/tetherless-world/whyis.git',
  revision => $whyis_branch_,
  user     => 'whyis'
} ->
python::virtualenv { '/apps/whyis/venv' :
  ensure       => present,
  version      => '3',
  systempkgs   => false,
  distribute   => false,
  venv_dir     => '/apps/whyis/venv',
  owner        => 'whyis',
  cwd          => '/apps/whyis',
  timeout      => 18000,
} ->
python::pip { 'pip-upgrade' :
  pkgname       => 'pip',
  ensure        => 'latest',
  virtualenv    => '/apps/whyis/venv',
  owner         => 'whyis',
  timeout       => 18000,
} ->
python::requirements { '/apps/whyis/requirements/dev.txt' :
  virtualenv => '/apps/whyis/venv',
  owner      => 'whyis',
  forceupdate => true,
  timeout       => 18000,
} ->
file { "/apps/.bash_profile" :
  owner => 'whyis',
  content => '
  source /apps/whyis/venv/bin/activate
  ',
} ->
file { "/var/log/celery":
    owner => "whyis",
    ensure => directory,
    recurse => true,
    group => "whyis",
} ->
file { "/etc/default/celeryd":
  source => "/apps/whyis/resources/celeryd",
  owner => "root",
  group => "root",
  ensure => present
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
} ->
file { "/etc/apache2/sites-available/000-default.conf":
  ensure => present,
  source => "/apps/whyis/apache.conf",
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
