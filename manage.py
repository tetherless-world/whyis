# -*- coding:utf-8 -*-

from __future__ import print_function
import flask_script as script

import commands

from main import app_factory
try:
    import config
except ImportError as e:
    print("WARNING: %s, using defaults file" % str(e))
    import config_defaults as config

manager = script.Manager(app_factory)

@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)
    
    for line in sorted(output):
        print(line)

if __name__ == "__main__":

    manager.add_option("-n", "--name", dest="app_name", required=False, default=config.project_name)
    manager.add_option("-c", "--config", dest="config", required=False, default=config.Dev)
    manager.add_command("createuser", commands.CreateUser())
    manager.add_command("updateuser", commands.UpdateUser())
    manager.add_command("test", commands.Test())
    manager.add_command("configure", commands.Configure())
    manager.add_command("test_agent", commands.TestAgent())
    manager.add_command("load", commands.LoadNanopub())
    manager.add_command("retire", commands.RetireNanopub())
    manager.add_command("interpret", commands.RunInterpreter())

    manager.run()
