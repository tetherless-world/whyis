import rdflib
from flask import g, current_app, render_template
from flask_login import current_user

from .cql_blueprint import cql_blueprint
from whyis.decorator import conditional_login_required
from whyis.namespace import NS


@cql_blueprint.route('/cql.html')
@conditional_login_required
def cql_form():
    template_args = dict(ns=NS,
                         g=g,
                         config=current_app.config,
                         current_user=current_user,
                         isinstance=isinstance,
                         rdflib=rdflib,
                         hasattr=hasattr,
                         set=set)

    return render_template('cql.html', endpoint="/cql", **template_args)