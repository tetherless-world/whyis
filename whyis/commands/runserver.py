# -*- coding:utf-8 -*-

import subprocess
import sys
from multiprocessing import Process
from threading import Thread, get_ident, main_thread
from werkzeug.serving import is_running_from_reloader

from flask_script import Option, Server

import os
import socket
from whyis import fuseki

from celery import current_app
from celery.bin import worker

def find_free_port():
    with socket.socket() as s:
        s.bind(('', 0))            # Bind to a free port provided by the host.
        return s.getsockname()[1]  # Return the port number assigned.

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
        with self.app.app_context():
            self.app.celery_worker = self.app.celery.WorkController()
            print("Starting Celery worker...")
            self.app.celery_worker.start()

    def __call__(self, app, watch, *args, **kwds):
        global fuseki_server
        self.app = app
        self.options={
            "threaded": True,
        }

        if not is_running_from_reloader():
            if self.app.config.get('EMBEDDED_CELERY', False):
                app.celery_worker_process = Thread(target=self.run_celery, daemon=True)
                app.celery_worker_process.start()
                #app.celery_worker.start()

            if app.config.get('EMBEDDED_FUSEKI', False) and fuseki_server is None:
                self.port = find_free_port()
                print("Starting Fuseki on port",self.port)
                fuseki_server = fuseki.FusekiServer(port=self.port)

        if app.config.get('EMBEDDED_FUSEKI', False):
            app.config['FUSEKI_PORT'] = self.port
            knowledge_endpoint = fuseki_server.get_dataset('/knowledge')
            print("Knowledge Endpoint:", knowledge_endpoint)
            app.config['KNOWLEDGE_ENDPOINT'] = knowledge_endpoint
            admin_endpoint = fuseki_server.get_dataset('/admin')
            app.config['ADMIN_ENDPOINT'] = admin_endpoint
            print("Admin Endpoint:", admin_endpoint)
            app.configure_database()

        kwds['use_reloader'] = False

        if not watch:
            print ("Starting Whyis Webserver...")
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

        with CleanChildProcesses():
            for static_dir_path in webpack_static_dir_paths:
                subprocess.Popen(["npm", "start"], cwd=static_dir_path)

            return Server.__call__(self, app=app, *args, **kwds)
