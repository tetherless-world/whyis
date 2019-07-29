# -*- coding:utf-8 -*-

import flask_script as script

from whyis import commands

from main import app_factory

from whyis.config_utils import import_config_module


if __name__ == "__main__":
    config = import_config_module()
    manager = script.Manager(app_factory)

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
    manager.add_command("uninstall_app", commands.UninstallApp())

    manager.run()
