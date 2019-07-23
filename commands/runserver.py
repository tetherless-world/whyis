# -*- coding:utf-8 -*-

import subprocess
import sys

from flask_script import Option, Server

import os


class WhyisServer(Server):
    """
    Customized runserver command.
    """

    def get_options(self):
        return \
            list(Server.get_options(self)) + \
            [
                Option("--watch", action="store_true"),
            ]

    def __call__(self, app, watch, *args, **kwds):
        if not watch:
            return Server.__call__(self, app=app, *args, **kwds)

        if sys.platform != "win32":
            # Start webpack in the static/ directories if it's configured
            static_dir_paths = [app.static_folder]
            if 'WHYIS_CDN_DIR' in app.config and app.config['WHYIS_CDN_DIR'] is not None:
                static_dir_paths.append(app.config["WHYIS_CDN_DIR"])
            webpack_static_dir_paths = []
            for static_dir_path in static_dir_paths:
                if not os.path.isfile(os.path.join(static_dir_path, "package.json")):
                    continue
                if not os.path.isfile(os.path.join(static_dir_path, "webpack.config.js")):
                    continue
                if not os.path.isdir(os.path.join(static_dir_path, "node_modules")):
                    print("%s has a package.json but no node_modules; need to run 'npm install' to get webpack?",
                          file=sys.stderr)
                    continue
                webpack_static_dir_paths.append(static_dir_path)
        else:
            webpack_static_dir_paths = []

        for static_dir_path in webpack_static_dir_paths:
            subprocess.call(["npm", "install"], cwd=static_dir_path)

        class CleanChildProcesses:
            def __enter__(self):
                os.setpgrp()  # create new process group, become its leader

            def __exit__(self, type, value, traceback):
                try:
                    import signal
                    os.killpg(0, signal.SIGINT)  # kill all processes in my group
                except KeyboardInterrupt:
                    # SIGINT is delievered to this process as well as the child processes.
                    # Ignore it so that the existing exception, if any, is returned. This
                    # leaves us with a clean exit code if there was no exception.
                    pass

        with CleanChildProcesses():
            for static_dir_path in webpack_static_dir_paths:
                subprocess.Popen(["npm", "start"], cwd=static_dir_path)

            Server.__call__(self, app=app, *args, **kwds)
