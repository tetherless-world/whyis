# This file is part of Flask-PluginEngine.
# Copyright (C) 2014-2021 CERN
#
# Flask-PluginEngine is free software; you can redistribute it
# and/or modify it under the terms of the Revised BSD License.

from werkzeug.local import LocalProxy, LocalStack


_plugin_ctx_stack = LocalStack()

#: Proxy to the currently active plugin
current_plugin = LocalProxy(lambda: _plugin_ctx_stack.top)
