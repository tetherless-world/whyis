# -*- coding:utf-8 -*-

import flask_script as script

from whyis import commands

from whyis.app_factory import app_factory
from re import finditer

import sys
import os
from cookiecutter.main import cookiecutter
from pkg_resources import resource_filename, resource_listdir

from whyis.config.utils import import_config_module, UnconfiguredAppException
import json
import signal

# Add current directory to python path to enable imports for app.
try:
    sys.path.index(os.getcwd())
except:
    sys.path.append(os.getcwd())

fuseki_celery_local = False

class CleanChildProcesses:

    def __enter__(self):
        try:
            os.setpgrp()  # create new process group, become its leader
        except PermissionError:
            print('Running in a container, probably.')

    def __exit__(self, type, value, traceback):
        global fuseki_celery_local
        print(fuseki_celery_local)
        if fuseki_celery_local:
            print("Cleaning up local config.")
            os.remove('embedded.conf')
        try:
            import signal

            os.killpg(0, signal.SIGINT)  # kill all processes in my group
        except KeyboardInterrupt:
            # SIGINT is delievered to this process as well as the child processes.
            # Ignore it so that the existing exception, if any, is returned. This
            # leaves us with a clean exit code if there was no exception.
            pass


def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def configure_knowledge_graph():
    try:
        from pip._internal.operations import freeze
    except ImportError:  # pip < 10.0
        from pip.operations import freeze

    # Create project from the cookiecutter-pypackage/ template
    app_dir = os.getcwd()
    dirname = app_dir.split(os.path.sep)[-1]
    project_name = ' '.join(camel_case_split(dirname.replace('_'," ").replace('-',' '))).title()
    extra_context = {
        'project_name' : project_name,
        'project_slug' : dirname,
        '__freeze' : list(freeze.freeze())
    }
    template_path = resource_filename('whyis', 'config-template')
    os.chdir('..')
    cookiecutter(template_path, extra_context=extra_context,
                 no_input=True,overwrite_if_exists=True)
    os.chdir(app_dir)

unconfigurable_commands = set([
    "backup",
    "createuser",
    "load",
    "restore",
    "retire",
    "test",
    "runagent",
    "updateuser",
    "init",
    "sanitize"
])

class Manager(script.Manager):
    def __init__(self):
        script.Manager.__init__(self, app_factory, with_default_commands=False)

        self.add_command("backup", commands.Backup())
        #self.add_command("configure", commands.Configure())
        self.add_command("createuser", commands.CreateUser())
        #self.add_command("listroutes", commands.ListRoutes())
        self.add_command("load", commands.LoadNanopub())
        self.add_command("init", commands.Initialize())
        self.add_command("sanitize", commands.Sanitize())
        self.add_command("restore", commands.Restore())
        self.add_command("retire", commands.RetireNanopub())
        self.add_command("run", commands.WhyisServer())
        self.add_command("test", commands.Test())
        self.add_command("runagent", commands.TestAgent())
        self.add_command("updateuser", commands.UpdateUser())

    _app = None

    def app(self):
        if self._app is None:
            self._app =  script.Manager.app(self)
        return self._app

def main():
    global fuseki_celery_local
    os.environ['FLASK_ENV'] = 'development'
    #os.setpgrp()  # create new process group, become its leader
    with CleanChildProcesses():
        m = Manager()
        if '-q' not in sys.argv and '--help' not in sys.argv:
            if not os.path.exists('whyis.conf'):
                configure_knowledge_graph()
            app = m.app()
            if app.config.get('EMBEDDED_CELERY',False) or app.config.get('EMBEDDED_FUSEKI', False):
                fuseki_celery_local = True
                embedded_config = {
                    'EMBEDDED_FUSEKI' : False,
                    'FUSEKI_PORT' : app.config['FUSEKI_PORT'],
                    'KNOWLEDGE_ENDPOINT' : app.config['KNOWLEDGE_ENDPOINT'],
                    'ADMIN_ENDPOINT' : app.config['ADMIN_ENDPOINT'],
                    'EMBEDDED_CELERY' : False,
                    'CELERY_BROKER_URL' : app.config['CELERY_BROKER_URL'],
                    'CELERY_RESULT_BACKEND' : app.config['CELERY_RESULT_BACKEND']
                }
                with open('embedded.conf', 'w') as embedded_config_file:
                    json.dump(embedded_config, embedded_config_file)
                    #def sigint_handler(signal, frame):
                    #    print('Cleaning up...')
                    #    os.remove('embedded.conf')
                    #signal.signal(signal.SIGINT, sigint_handler)

        m.run(default_command='run')
#    except KeyboardInterrupt:
    #    pass
        # print('hi!',flush=True)
        # if fuseki_celery_local:
        #    os.remove('embedded.conf')
        #try:
        #    os.killpg(0, signal.SIGINT)  # kill all processes in my group
        #except KeyboardInterrupt:
            # SIGINT is delievered to this process as well as the child processes.
            # Ignore it so that the existing exception, if any, is returned. This
            # leaves us with a clean exit code if there was no exception.
        #    pass
    #print(fuseki_celery_local, flush=True)
    #print("Exiting...",flush=True)

        #import signal

        #os.killpg(0, signal.SIGINT)  # kill all processes in my group
        #except KeyboardInterrupt:
            # SIGINT is delievered to this process as well as the child processes.
            # Ignore it so that the existing exception, if any, is returned. This
            # leaves us with a clean exit code if there was no exception.
        #    pass

if __name__ == "__main__":
    main()
