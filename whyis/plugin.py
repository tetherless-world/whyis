from flask import render_template
from flask_pluginengine import Plugin as PluginBase
from flask_pluginengine import PluginBlueprint, current_plugin
from pkg_resources import resource_exists, resource_stream, resource_filename
import rdflib

class Listener:
    '''Listen for changes in the system based on the signals listed in self.signal.'''
    signals = []

class NanopublicationListener(Listener):
    '''
Listen for nanopublication changes. Right now, only databases can do that
when theyre configured. '''

    signals = ['on_retire','on_publish']

    def on_retire(self, nanopub):
        pass

    def on_publish(self, nanopub):
        pass

    def on_prepare(self, nanopub):
        pass

class EntityResolverListener(Listener):

    signals = ['on_resolve']

    def on_resolve(self, term, type, context, label=True):
        return []

class Plugin(PluginBase):

    filters = {}

    _vocab = None

    _blueprint = None

    def vocab(self, store):
        import inspect
        module = inspect.getmodule(type(self))
        print(resource_filename(module.__name__, 'vocab.ttl'))
        if resource_exists(module.__name__, "vocab.ttl"):
            vocab = rdflib.Graph(store=store)
            vocab.parse(
                resource_stream(module.__name__, "vocab.ttl"),
                format="turtle",
                publicID=str(self.app.NS.local)
            )

    def create_blueprint(self):
        return None
#        plugin_blueprint = PluginBlueprint('example', __name__)
#        return plugin_blueprint

    @property
    def blueprint(self):
        if self._blueprint is None:
            self._blueprint = self.create_blueprint()
        return self._blueprint
