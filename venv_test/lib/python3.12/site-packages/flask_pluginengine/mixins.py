# This file is part of Flask-PluginEngine.
# Copyright (C) 2014-2021 CERN
#
# Flask-PluginEngine is free software; you can redistribute it
# and/or modify it under the terms of the Revised BSD License.

from flask import Blueprint, Flask
from flask.blueprints import BlueprintSetupState
from jinja2 import ChoiceLoader
from werkzeug.utils import cached_property

from .globals import current_plugin
from .templating import PluginEnvironment, PluginPrefixLoader
from .util import wrap_in_plugin_context


class PluginBlueprintSetupStateMixin:
    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        func = view_func
        if view_func is not None:
            plugin = current_plugin._get_current_object()
            func = wrap_in_plugin_context(plugin, view_func)

        super().add_url_rule(rule, endpoint, func, **options)


class PluginBlueprintMixin:
    def __init__(self, name, *args, **kwargs):
        if 'template_folder' in kwargs:
            raise ValueError('Template folder cannot be specified')
        kwargs.setdefault('static_folder', 'static')
        kwargs.setdefault('static_url_path', f'/static/plugins/{name}')
        name = f'plugin_{name}'
        super().__init__(name, *args, **kwargs)

    def make_setup_state(self, app, options, first_registration=False):
        return PluginBlueprintSetupState(self, app, options, first_registration)

    @cached_property
    def jinja_loader(self):
        return None


class PluginFlaskMixin:
    plugin_jinja_loader = PluginPrefixLoader
    jinja_environment = PluginEnvironment

    def create_global_jinja_loader(self):
        default_loader = super().create_global_jinja_loader()
        return ChoiceLoader([self.plugin_jinja_loader(self), default_loader])


class PluginBlueprintSetupState(PluginBlueprintSetupStateMixin, BlueprintSetupState):
    pass


class PluginBlueprint(PluginBlueprintMixin, Blueprint):
    pass


class PluginFlask(PluginFlaskMixin, Flask):
    pass
