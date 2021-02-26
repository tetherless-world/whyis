from pkg_resources import resource_filename, resource_listdir
import subprocess
import os
import sys
import signal

# exec $JAVA $JVM_ARGS -cp "$CP" org.apache.jena.fuseki.cmd.FusekiCmd "$@"

def run_fuseki(args, stdin=None, stdout=None, stderr=None):
    jvm_args = os.environ.get('JVM_ARGS', '-Xmx4G')
    classpath = os.environ.get('CLASSPATH','')
    jars = resource_listdir(__name__, 'jars')
    jar_path = resource_filename(__name__, 'jars')
    jars = ['/'.join([jar_path, jar]) for jar in jars]
    cp = ':'.join([classpath]+jars)
    java = os.environ.get('JAVA','java')
    env = {}
    env.update(os.environ)
    if 'FUSEKI_HOME' not in env:
        env['FUSEKI_HOME'] = resource_filename('whyis', 'fuseki')
    command = [java, jvm_args, '-cp', cp, 'org.apache.jena.fuseki.cmd.FusekiCmd'] + args
    try:
        p = None

        # Register handler to pass keyboard interrupt to the subprocess
        def handler(sig, frame):
            if p:
                p.send_signal(signal.SIGINT)
            else:
                raise KeyboardInterrupt
        signal.signal(signal.SIGINT, handler)

        p = subprocess.Popen(command, stdin=stdin, stdout=stdout, stderr=stderr, env=env)
        return p
    finally:
        # Reset handler
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    #return subprocess.run(command, stdin=stdin, stdout=stdout, stderr=stderr, env=env)

def main():
    run_fuseki(sys.argv[1:]).wait()

if __name__ == "__main__":
    main()
