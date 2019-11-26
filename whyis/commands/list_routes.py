from flask import url_for, current_app
from flask_script import Command
import urllib.request, urllib.parse, urllib.error


class ListRoutes(Command):
    """Display all valid routes in the application"""
    def run(self):
        output = []
        for rule in current_app.url_map.iter_rules():

            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = url_for(rule.endpoint, **options)
            line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
            output.append(line)

        for line in sorted(output):
            print(line)
