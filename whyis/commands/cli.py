# -*- coding:utf-8 -*-
"""
Click-based CLI commands for Whyis.

This module provides Flask CLI commands using Click, replacing Flask-Script commands.
"""

import click
from flask.cli import with_appcontext
import datetime
import flask
import sys
import os
import uuid

# Flask-Security-Too renamed encrypt_password to hash_password
try:
    from flask_security.utils import hash_password
except ImportError:
    # Fallback for older versions
    from flask_security.utils import encrypt_password as hash_password


@click.command('createuser')
@click.option('-e', '--email', help='Email address for this user', type=str)
@click.option('-p', '--password', required=True, help='Password for this user', type=str)
@click.option('-f', '--fn', help='First name of this user', type=str)
@click.option('-l', '--ln', help='Last name of this user', type=str)
@click.option('-u', '--username', required=True, help='Username for this user', type=str)
@click.option('--roles', help='Comma-delimited list of role names', type=str)
@with_appcontext
def createuser_command(email, password, fn, ln, username, roles):
    """Add a user to Whyis."""
    role_objects = []
    if roles is not None:
        role_objects = [flask.current_app.datastore.find_or_create_role(name=r) for r in roles.split(',')]
    
    user = dict(
        id=username, 
        email=email,
        password=hash_password(password),
        givenName=fn, 
        familyName=ln,
        confirmed_at=datetime.datetime.utcnow(), 
        roles=role_objects,
        fs_uniquifier=str(uuid.uuid4())  # Required by Flask-Security-Too 4.0+
    )
    user_obj = flask.current_app.datastore.create_user(**user)
    click.echo(f"Created user: {username}")


@click.command('init')
@with_appcontext
def init_command():
    """Initialize Whyis application."""
    from whyis.commands.init import Initialize
    cmd = Initialize()
    cmd.run()
    click.echo("Initialization complete.")


@click.command('sanitize')
@with_appcontext
def sanitize_command():
    """Sanitize the knowledge graph."""
    from whyis.commands.sanitize import Sanitize
    cmd = Sanitize()
    cmd.run()
    click.echo("Sanitization complete.")


@click.command('backup')
@with_appcontext
def backup_command():
    """Backup the Whyis application."""
    from whyis.commands.backup import Backup
    cmd = Backup()
    cmd.run()
    click.echo("Backup complete.")


@click.command('restore')
@with_appcontext  
def restore_command():
    """Restore the Whyis application from backup."""
    from whyis.commands.restore import Restore
    cmd = Restore()
    cmd.run()
    click.echo("Restore complete.")


@click.command('load')
@click.argument('filename')
@with_appcontext
def load_command(filename):
    """Load a nanopublication from file."""
    from whyis.commands.load_nanopub import LoadNanopub
    cmd = LoadNanopub()
    cmd.run(filename)
    click.echo(f"Loaded nanopublication from {filename}")


@click.command('retire')
@click.argument('nanopub_uri')
@with_appcontext
def retire_command(nanopub_uri):
    """Retire a nanopublication."""
    from whyis.commands.retire_nanopub import RetireNanopub
    cmd = RetireNanopub()
    cmd.run(nanopub_uri)
    click.echo(f"Retired nanopublication: {nanopub_uri}")


@click.command('updateuser')
@click.option('-e', '--email', help='Email address', type=str)
@click.option('-p', '--password', help='New password', type=str)
@click.option('-f', '--fn', help='First name', type=str)
@click.option('-l', '--ln', help='Last name', type=str)
@click.option('-u', '--username', required=True, help='Username', type=str)
@click.option('--roles', help='Comma-delimited list of role names', type=str)
@with_appcontext
def updateuser_command(email, password, fn, ln, username, roles):
    """Update a user in Whyis."""
    from whyis.commands.update_user import UpdateUser
    cmd = UpdateUser()
    cmd.run(email=email, password=password, fn=fn, ln=ln, identifier=username, roles=roles)
    click.echo(f"Updated user: {username}")


@click.command('test')
@click.option('-v', '--verbosity', type=int, default=2, help='Verbosity level (0-2)')
@click.option('--failfast', is_flag=True, help='Stop after first failure')
@click.option('--test', 'tests', default='test*', help='Test pattern or file')
@click.option('--ci', is_flag=True, help='Run with coverage for CI')
@click.option('--apponly', is_flag=True, help='Run app tests only')
@with_appcontext
def test_command(verbosity, failfast, tests, ci, apponly):
    """Run tests."""
    from whyis.commands.test import Test
    cmd = Test()
    cmd.run(verbosity=verbosity, failfast=failfast, tests=tests, ci=ci, apponly=apponly)


@click.command('runagent')
@click.argument('agent_name')
@with_appcontext
def runagent_command(agent_name):
    """Run a specific agent."""
    from whyis.commands.test_agent import TestAgent
    cmd = TestAgent()
    cmd.run(agent_name)
    click.echo(f"Ran agent: {agent_name}")


@click.command('run')
@click.option('-h', '--host', default='127.0.0.1', help='Host to bind to')
@click.option('-p', '--port', default=5000, type=int, help='Port to bind to')
@click.option('--threaded/--no-threaded', default=True, help='Enable/disable threading')
@click.option('--watch', is_flag=True, help='Watch for changes and reload')
@with_appcontext
def run_command(host, port, threaded, watch):
    """Run the Whyis development server with embedded services."""
    import subprocess
    from werkzeug.serving import is_running_from_reloader
    from flask import current_app
    
    celery_process = None
    webpack_processes = []
    
    # Start embedded Celery if configured
    if not is_running_from_reloader():
        if current_app.config.get('EMBEDDED_CELERY', False):
            click.echo("Starting embedded Celery...")
            import shutil
            celery_command = shutil.which('celery')
            if not celery_command:
                # Fallback to sys.argv[0] path
                celery_command = os.path.join(os.path.dirname(sys.argv[0]), 'celery')
            # Use full module path for Celery 5.x: 'whyis.wsgi:celery'
            # This tells Celery to import whyis.wsgi module and use the 'celery' attribute
            celery_args = ['-A', 'whyis.wsgi:celery']
            worker_args = ['worker', '--beat', '-l', 'INFO', '--logfile', 'run/logs/celery.log']
            command = [celery_command] + celery_args + worker_args
            celery_process = subprocess.Popen(command, stdin=subprocess.DEVNULL)
    
    # Start webpack watch if requested
    if watch and sys.platform != "win32":
        static_dir_paths = []
        if 'WHYIS_CDN_DIR' in current_app.config and current_app.config['WHYIS_CDN_DIR'] is not None:
            static_dir_paths.append(current_app.config["WHYIS_CDN_DIR"])
        
        webpack_static_dir_paths = []
        for static_dir_path in static_dir_paths:
            if not os.path.isfile(os.path.join(static_dir_path, "package.json")):
                continue
            if not os.path.isfile(os.path.join(static_dir_path, "webpack.config.js")):
                continue
            if not os.path.isdir(os.path.join(static_dir_path, "node_modules")):
                click.echo(f"{static_dir_path} has package.json but no node_modules; run 'npm install'")
                continue
            webpack_static_dir_paths.append(static_dir_path)
        
        for static_dir_path in webpack_static_dir_paths:
            subprocess.call(["npm", "install"], cwd=static_dir_path)
        
        for static_dir_path in webpack_static_dir_paths:
            proc = subprocess.Popen(["npm", "start"], cwd=static_dir_path)
            webpack_processes.append(proc)
    
    # Run the Flask development server
    try:
        current_app.run(host=host, port=port, threaded=threaded, use_reloader=False)
    finally:
        # Clean up subprocesses
        if celery_process:
            celery_process.terminate()
        for proc in webpack_processes:
            proc.terminate()


# Export all commands for registration
__all__ = [
    'createuser_command',
    'init_command',
    'sanitize_command',
    'backup_command',
    'restore_command',
    'load_command',
    'retire_command',
    'updateuser_command',
    'test_command',
    'runagent_command',
    'run_command',
]
