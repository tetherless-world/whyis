# -*- coding:utf-8 -*-

import flask_script as script

from whyis import commands

from whyis.app_factory import app_factory

import sys
import os

# Add current directory to python path to enable imports for app.
try:
    sys.path.index(os.getcwd())
except:
    sys.path.append(os.getcwd())


class Manager(script.Manager):
    def __init__(self):
        script.Manager.__init__(self, app_factory)

        self.add_command("configure", commands.Configure())
        self.add_command("createuser", commands.CreateUser())
        self.add_command("listroutes", commands.ListRoutes())
        self.add_command("load", commands.LoadNanopub())
        self.add_command("retire", commands.RetireNanopub())
        self.add_command("runserver", commands.WhyisServer())
        self.add_command("test", commands.Test())
        self.add_command("testagent", commands.TestAgent())
        self.add_command("updateuser", commands.UpdateUser())
        self.add_command("uninstallapp", commands.UninstallApp())

def main():
    Manager().run()

if __name__ == "__main__":
    Manager().run()
