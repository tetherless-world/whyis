# This file is part of Flask-PluginEngine.
# Copyright (C) 2014-2021 CERN
#
# Flask-PluginEngine is free software; you can redistribute it
# and/or modify it under the terms of the Revised BSD License.

from blinker import Namespace


_signals = Namespace()
plugins_loaded = _signals.signal('plugins-loaded', """
Called after :meth:`~PluginEngine.load_plugins` has loaded the
plugins successfully. This triggers even if there are no enabled
plugins. *sender* is the Flask app.
""")
