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

Finally, set a password salt secret that will prevent hackers from being able to guess passwords if they get access to them.
This can be generated using `os.urandom(24)` as well.

```
SECURITY_PASSWORD_SALT = 'changeme__',
```

## Advanced Configuration

If you are developing a custom knowledge graph, you will probably want to manage your code in a module that you can version control separately from the Satoru installation.
First, create a project directory.
Ideally, it should be owned by the `satoru` user and be in apps. 
You should also create a requirements.txt file, with all of your python dependencies, and install them and the package itself:

```
cd /apps
mkdir myknowledgegraph
cd myknowledgegraph
touch requirements.txt
mkdir templates
mkdir cdn
mv /apps/satoru/config.py .
cp /apps/satoru/vocab.ttl .
pip install -e .
```

That should set up an initial project directory and let you check your configuration in there and create templates and a local vocabulary.
Edit `/apps/satoru/config.py` to set `vocab_file='/apps/myknowledgegraph/vocab.ttl'` (or whatever you're calling your project).
You will also need to set `SATORU_TEMPLATE_DIR` in order to create custom views:

```
    SATORU_TEMPLATE_DIR = "/apps/myknowledgegraph/templates",
    SATORU_CDN_DIR = "/apps/myknowledgegraph/cdn",
```

## Views and Interaction

Nodes in Satoru knowledge graphs can be customized to look like just about anything based on their `rdf:type`.
Nodes can also have multiple views, which can be selected using the `view=` URL parameter. 
The default type in the graph is `rdfs:Resource`, and the default view is `view`.
If you want to create a default view for a class you are defining, add the following to your vocab.ttl file:

```
<http://example.com/my_ontology/MyClass> rdfs:label "My Class";
    graphene:hasView "my_class_view.html".
```

`graphene:hasView` is the top-level property for creating views in Satoru.
If you want to create a new kind of view, create a subproperty of `graphene:hasView` and give it an identifier:

```
<http://example.com/my_ontology/hasScatterPlot> dc:identifier "scatter_plot";
  rdfs:subPropertyOf graphene:hasView.
```

You can now configure `scatter_plot` views for your class too:

```
<http://example.com/my_ontology/MyClass> graphene:hasScatterPlot "my_scatterplot_view.html".
```

Create a file called `/apps/myknowledgegraph/templates/my_scatterplot_view.html` and populate it with your code.
The file `/apps/satoru/templates/resource_view.html` is a good first example.

You will need to restart apache after reconfiguring views in Satoru.

The pre-configured template and views are:

| Class | view | describe | label | nanopublications | related |
| ----- | ---- | -------- | ----- | ---------------- | ------- |
|rdfs:Resource | resource_view.html | describe.json | label_view.html | nanopublications.json | related.json |
|owl:Class | class_view.html |
|owl:Ontology | ontology_view.html |
|bibo:AcademicArticle | article_view.html |

The view selector will choose the template for the view that is most specific to an instance.
Subclasses with custom views will override their transitive superclasses.
Instances do not need to have a type directly asserted, but can use the knowledge graph and vocab files to find relevant superclasses to the asserted types.

## Security
Satoru uses flask-security for authentication and authorization. 
The default configuration is to require an authenticated user for all access.
We are happy to accept pull requests that make this configurable. 
A guide to [configuring flask-security](https://pythonhosted.org/Flask-Security/configuration.html) is available on the flask-security site.

## Email
Satoru uses flask-mail for sending email. Please refer to the [flask-mail configuration guide](https://pythonhosted.org/Flask-Mail/).

