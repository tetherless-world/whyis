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


class Manager(script.Manager):
    def __init__(self):
        script.Manager.__init__(self, app_factory)

        self.add_command("backup", commands.Backup())
        self.add_command("configure", commands.Configure())
        self.add_command("createuser", commands.CreateUser())
        self.add_command("listroutes", commands.ListRoutes())
        self.add_command("load", commands.LoadNanopub())
        self.add_command("restore", commands.Restore())
        self.add_command("retire", commands.RetireNanopub())
        self.add_command("runserver", commands.WhyisServer())
        self.add_command("test", commands.Test())
        self.add_command("testagent", commands.TestAgent())
        self.add_command("updateuser", commands.UpdateUser())
        self.add_command("uninstallapp", commands.UninstallApp())

def main():
    with CleanChildProcesses():
        Manager().run()

if __name__ == "__main__":
    Manager().run()
