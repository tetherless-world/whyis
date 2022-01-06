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

# Add current directory to python path to enable imports for app.
try:
    sys.path.index(os.getcwd())
except:
    sys.path.append(os.getcwd())

class CleanChildProcesses:
    def __enter__(self):
        os.setpgrp()  # create new process group, become its leader

    def __exit__(self, type, value, traceback):
        try:
            import signal
            os.killpg(0, signal.SIGINT)  # kill all processes in my group

            app.celery_worker.stop()
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
    "updateuser"
])

class Manager(script.Manager):
    def __init__(self):
        script.Manager.__init__(self, app_factory, with_default_commands=False)

        self.add_command("backup", commands.Backup())
        #self.add_command("configure", commands.Configure())
        self.add_command("createuser", commands.CreateUser())
        #self.add_command("listroutes", commands.ListRoutes())
        self.add_command("load", commands.LoadNanopub())
        self.add_command("restore", commands.Restore())
        self.add_command("retire", commands.RetireNanopub())
        self.add_command("run", commands.WhyisServer())
        self.add_command("test", commands.Test())
        self.add_command("runagent", commands.TestAgent())
        self.add_command("updateuser", commands.UpdateUser())

def main():
    os.environ['FLASK_ENV'] = 'development'
    with CleanChildProcesses():
        if not os.path.exists('whyis.conf'):
            configure_knowledge_graph()
        m = Manager()
        m.run(default_command='run')

if __name__ == "__main__":
    main()
