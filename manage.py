# -*- coding:utf-8 -*-

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
import flask_script as script

import subprocess

from main import app_factory
try:
    import config
except ImportError as e:
    print("WARNING: %s, using defaults file" % str(e))
    import config_defaults as config

manager = script.Manager(app_factory)

@manager.command
def list_routes():
    import urllib.request, urllib.parse, urllib.error
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)
    
    for line in sorted(output):
        print(line)

if __name__ == "__main__":

    manager.add_option("-n", "--name", dest="app_name", required=False, default=config.project_name)
    manager.add_option("-c", "--config", dest="config", required=False, default=config.Dev)
    manager.add_command("createuser", subprocess.CreateUser())
    manager.add_command("updateuser", subprocess.UpdateUser())
    manager.add_command("test", subprocess.Test())
    manager.add_command("configure", subprocess.Configure())
    manager.add_command("test_agent", subprocess.TestAgent())
    manager.add_command("load", subprocess.LoadNanopub())
    manager.add_command("retire", subprocess.RetireNanopub())
    manager.add_command("interpret", subprocess.RunInterpreter())

    manager.run()
