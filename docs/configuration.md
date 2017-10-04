# Configure Satoru

Satoru is built on the Flask web framework, and most of the Flask authentication options are available to configure in Satoru.
The main configuration components are `/apps/satoru/config.py` and the turtle vocabulary file, at `/apps/satoru/vocab.ttl`.
`config.py` is a python-based configuration file, where the main configurations are set in a dict object.

## Basic Configuration

Any knowledge graph needs to have a default URI namespace.
This namespace is the prefix for all users, nanopublications, and is the default prefix for entities in the knowledge graph.
The default prefix is for development. It should be set to the base URL of the Satoru application:

```
LOD_PREFIX='http://localhost:5000'
```

The site name should be configured as well:

```
   site_name = "Satoru Knowledge Graph",
```

You should also configure a WSRF secret key, in the `SECRET_KEY` field.
It should be set from a value generated using a command like:

```
import os; os.urandom(24)
```

### Security
Satoru uses flask-security for authentication and authorization. 
The default configuration is to require an authenticated user for all access.
We are happy to accept pull requests that make this configurable. 
A guide to [configuring flask-security](https://pythonhosted.org/Flask-Security/configuration.html) is available on the flask-security site.

### Email
Satoru uses flask-mail for sending email. Please refer to the [flask-mail configuration guide](https://pythonhosted.org/Flask-Mail/).

## Advanced Configuration

If you are developing a custom knowledge graph, you will probably want to manage your code in a module that you can version control separately from the Satoru installation.
