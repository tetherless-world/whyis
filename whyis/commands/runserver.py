# -*- coding:utf-8 -*-

import subprocess
import sys
from multiprocessing import Process
from threading import Thread, get_ident, main_thread
from werkzeug.serving import is_running_from_reloader
import os
import signal

from flask_script import Option, Server

import os
import socket
from whyis import fuseki

from celery import current_app
from celery.bin import worker

fuseki_server = None

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

    def run_celery(self):
        import sys
        celery_command = os.path.join(os.path.dirname(sys.argv[0]),'celery')
        celery_args = ['-A', 'wsgi.celery']
        worker_args = ['--beat', '-l', 'INFO', '--logfile','run/logs/celery.log']
        command = [celery_command] + celery_args + ['worker'] + worker_args
        p = None
        p = subprocess.Popen(command, stdin=subprocess.DEVNULL)
        return p

    def __call__(self, app, watch, *args, **kwds):
        global fuseki_server
        self.app = app
        self.options={
            "threaded": True,
        }

        if not is_running_from_reloader():
            if self.app.config.get('EMBEDDED_CELERY', False):
                print("Starting embeddded Celery")
                self.celery_worker_process = self.run_celery()
                # app.celery_worker_process = Thread(target=self.run_celery, daemon=True)
                # app.celery_worker_process.start()

        kwds['use_reloader'] = False

        if not watch:
            return Server.__call__(self, app=app, *args, **kwds)

        if sys.platform != "win32":
            # Start webpack in the static/ directories if it's configured
            static_dir_paths = []
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

        for static_dir_path in webpack_static_dir_paths:
            subprocess.Popen(["npm", "start"], cwd=static_dir_path)

        return Server.__call__(self, app=app, *args, **kwds)
