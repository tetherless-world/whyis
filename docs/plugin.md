# Creating Whyis Plugins

## Approach for creating a package for Whyis

### Initial Setup
Start by creating a folder that will contain the contents of the package. In this example, we are creating a plugin related to Activity Streams.

### Creating a project configuration
To configure the project for publishing to PyPi, create a `pyproject.toml` file. The file should have `setup-tools` required by the build system.
```
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
```

The project itself should be given a name and other descriptive metadata. Additionally, `whyis` should be added as a dependency.
```
[project]
name='whyis-activitystreams'
version='0.0.4'
description = "A whyis plugin to support the interpretation of activity streams."
dependencies=[
  'whyis',
]
```

The packages to be exported should be specified as tools.
```
[tool.setuptools]
packages=['whyis_activitystreams', 'whyis_activitystreams.activity_agent']
```

The entry points for these packages should also be specified.
```
[project.entry-points.whyis]
whyis_activitystreams = "whyis_activitystreams:ActivityStreamsPlugin"
whyis_activity_agent = "whyis_activitystreams.activity_agent:ActivityAgent"
```

### Initialization
When creating a plugin, a directory should be created with the same name as the package specified in `tool.setuptools`, where names seperated by a period correspond to subdirectories. Within the plugin direction, a python file should be created that contains the main class of the plugin. This class should inherit from the Whyis Plugin class.
```{python}
# plugin.py
from whyis.plugin import Plugin

class ActivityStreamsPlugin(Plugin) :
```

The directory should also contain an initialization file `__init__.py` that specified what content will be imported.
```
from .plugin import *
from .activity_agent import *
```
Note that package subdirectories should also contain their own `__init__.py` file.

### Creating an agent
When creating an agent as an importable package, a python file with the class of that agent and its functionality should be created. That file should import the required packages from Whyis. `rdflib` is typically imported as well to work when working with RDF resources.
```
from whyis.autonomic import UpdateChangeService
from whyis.namespace import NS

from whyis.plugin import Plugin
from flask import current_app

import rdflib
```

The class for the agent is typically defined as either an `UpdateChangeService` or a `GlobalChangeService`. An `UpdateChangeService` runs when a Nanopublication is updated. A `GlobalChangeService` runs when the knowledge graph is updated.  An activity class should be specified as well as a query that triggers the agent.
```
class ActivityAgent(UpdateChangeService):
    activity_class = NS.whyis.ActivityResolving # resolving activities
    
    def get_query(self):
        return '''select distinct ?resource where {
            ?resource rdf:type [ rdfs:subClassOf*  <https://www.w3.org/ns/activitystreams#Object> ] .
        }'''
```

### Building and publishing
In order to publish to PyPi, you must have an account on PyPi set up. Once you do, you can publish the package through twine.
```
python -m pip install build twine
python -m build
twine upload dist/*
```

### Importing and using the package

In order to use a Whyis plugin or agent created as a python package, the associated package should be installed.
```
pip install whyis_activitystreams
```

Within the whyis configuration file, the package contents should be imported.
```
from whyis_activitystreams import *
from whyis_activitystreams.activity_agent import ActivityAgent
```

Plugins should be included in the Plugin engine list.
```
PLUGINENGINE_PLUGINS = ["whyis_activitystreams"]
```

Agents should be included in the agent configuration.
```
INFERENCERS = {
    "SETLr": autonomic.SETLr(),
    "SETLMaker": autonomic.SETLMaker(),
    "SDDAgent": autonomic.SDDAgent(),
    "ActivityAgent": ActivityAgent()
}
```
