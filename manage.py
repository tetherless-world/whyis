# -*- coding:utf-8 -*-

import flask_script as script

import commands

from main import app_factory
try:
    import config
except ImportError as e:
    print("WARNING: %s, using defaults file" % str(e))
    import config_defaults as config

manager = script.Manager(app_factory)

if __name__ == "__main__":

    manager.add_option("-n", "--name", dest="app_name", required=False, default=config.project_name)
    manager.add_option("-c", "--config", dest="config", required=False, default=config.Dev)
    manager.add_command("configure", commands.Configure())
    manager.add_command("createuser", commands.CreateUser())
    manager.add_command("interpret", commands.ListRoutes())
    manager.add_command("list_routes", commands.ListRoutes())
    manager.add_command("load", commands.LoadNanopub())
    manager.add_command("retire", commands.RetireNanopub())
    manager.add_command("runserver", commands.WhyisServer())
    manager.add_command("test", commands.Test())
    manager.add_command("test_agent", commands.TestAgent())
    manager.add_command("updateuser", commands.UpdateUser())

    manager.run()
