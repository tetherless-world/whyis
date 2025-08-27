from flask import Blueprint
import os

# Get the directory containing this file
_dir = os.path.dirname(os.path.abspath(__file__))
_template_folder = os.path.join(os.path.dirname(_dir), 'templates')

cql_blueprint = Blueprint("cql_blueprint", __name__, template_folder=_template_folder)