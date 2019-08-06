import rdflib
from flask import g, current_app, render_template
from flask_login import current_user

from whyis.blueprint.sparql import sparql_blueprint
from whyis.decorator import conditional_login_required
from whyis.namespace import NS


@sparql_blueprint.route('/sparql.html')
@conditional_login_required
def sparql_form():
    template_args = dict(ns=NS,
                         g=g,
                         config=current_app.config,
                         current_user=current_user,
                         isinstance=isinstance,
                         rdflib=rdflib,
                         hasattr=hasattr,
                         set=set)

    return render_template('sparql.html',endpoint="/sparql", **template_args)
