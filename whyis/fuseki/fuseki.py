from pkg_resources import resource_filename, resource_listdir, resource_string
import subprocess
import os
import sys
import signal
import requests
import time
import socket

# exec $JAVA $JVM_ARGS -cp "$CP" org.apache.jena.fuseki.cmd.FusekiCmd "$@"

def find_free_port():
    with socket.socket() as s:
        s.bind(('', 0))            # Bind to a free port provided by the host.
        return s.getsockname()[1]  # Return the port number assigned.

def _wait_for_port(port, host='localhost', timeout=10.0):
    """Wait until a port starts accepting TCP connections.
    Args:
        port (int): Port number.
        host (str): Host address on which the port should exist.
        timeout (float): In seconds. How long to wait before raising errors.
    Raises:
        TimeoutError: The port isn't accepting connection after time specified in `timeout`.
    """
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Waited too long for the port {} on host {} to start accepting '
                                   'connections.'.format(port, host)) from ex
            time.sleep(0.1)

class FusekiServer:
    _datasets = None
    _template = resource_string(__name__, "default_assembler.ttl").decode('utf8')
    _fuseki_base = os.sep.join([os.getcwd(),'run'])

    def __init__(self, args=[], port=3030, stdin=subprocess.PIPE, stdout=None, stderr=None):
        self.args = args
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.port = port
        self.url = 'http://localhost:'+str(self.port)
        self.process = run_fuseki(args+['--port',str(port),'-q', '--localhost', '--mem','/ds'],
                                  stdin, stdout, stderr)
        _wait_for_port(port)

    @property
    def datasets(self):
        if self._datasets is None:
            datasets = requests.get(self.url+'/$/datasets').json()
            self._datasets = dict([(d['ds.name'],d) for d in datasets['datasets']])
        return self._datasets

    def get_dataset(self, name):
        if name not in self.datasets:
            assembler = self._template.format(NAME=name, FUSEKI_BASE=self._fuseki_base)
            response = requests.post(self.url+'/$/datasets',
                                     data=assembler,
                                     headers={'Content-Type':"text/turtle"})
        return self.url+name

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
    #try:
    p = None

    # Register handler to pass keyboard interrupt to the subprocess
    # def handler(sig, frame):
    #     if p:
    #         p.send_signal(signal.SIGINT)
    #     else:
    #         raise KeyboardInterrupt
    # signal.signal(signal.SIGINT, handler)

    p = subprocess.Popen(command, stdin=stdin, stdout=stdout, stderr=stderr, env=env)
    return p
    #finally:
        # Reset handler
        #signal.signal(signal.SIGINT, signal.SIG_DFL)
    #return subprocess.run(command, stdin=stdin, stdout=stdout, stderr=stderr, env=env)

def main():
    run_fuseki(sys.argv[1:]).wait()

if __name__ == "__main__":
    main()
