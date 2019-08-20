# Creating Whyis Views

**Before starting this tutorial, please make sure that you have created a Whyis extension using the instructions in [Advanced Configuration](https://tetherless-world.github.io/whyis/configuration).**

Whyis creates knowledge graphs like a wiki - every possible URL in your Whyis knowledge graph is a node waiting to be created.
We will walk through creating custom views in Whyis, and how to use them to display nodes based on their type.

## Every Page is a Node

Every URL in Whyis, except for some special ones like under `/static` (Javascript, CSS, images and such for Whyis), `/cdn` (custom Javascript, CSS, images and such), and `/sparql` are Resources, or nodes in the knowledge graph.
The URL naming scheme for your knowledge graph is up to you.
You can organize nodes by their source, by topic, or just have an infinitely flat space.

We have pre-configured two importer namespaces in Whyis by default, DOI and DBpedia.
These can be removed or added to, but it makes it easy to quickly build example applications by having their knowledge loaded automatically.
DOI is an identifier system for academic papers, and DBpedia is a structured data representation of Wikipedia.
Both serve Linked Data when it is asked for using content negotiation.

## Every node has a Type

When you visit a URL in Whyis, you will almost never get a 404.
Instead, you'll get a page about a node where nothing is known of it.
When there are no known types for a node, or the types given aren't given custom views, they are assumed to have the rdfs:Resource type, and are given the [rdfs:Resource default view](https://github.com/tetherless-world/whyis/blob/master/templates/resource_view.html).
This default view provides room to show statements about the node, the type, summary descriptions, and a list of nanopublications about the node.
There is also a UI for adding new nanopublications.
This template, resource_view.html, is a useful starting point when creating custom node views in Whyis.
Visit the page `/dbpedia/Tim_Berners-Lee` to visit the node for Tim Berners-Lee, which will automatically import data from DBpedia.
Internally, the URI is mapped to the originating URI of `http://dbpedia.org/resource/Tim_Berners-Lee`, so all statements are imported as-is.

We are also able to reference nodes outside of the Whyis namespace.
This makes it easier to import external knowledge from linked data and ontologies.
All URIs can be referenced using the `/about` URL, with a URL-encoded parameter of `uri`.
For instance, the page for Tim Berners-Lee can also be visited at `/about?uri=http://dbpedia.org/resource/Tim_Berners-Lee`.

## Creating a Custom Default View

Let's create a custom default view for foaf:Person.
We can start by modifying your extension's `vocab.ttl` file to add the following:

```turtle
<http://xmlns.com/foaf/0.1/Person> a owl:Class;
    whyis:hasView "person_view.html".
```

Next, create a file in you extension called `templates/person_view.html` and add the following:

```html
{% raw %}
{% extends "base.html" %}
{% from "_macros.html" import render_resource_link, render_rdfa_resource_link, get_label, facts_panel, summary_panel, content %}
{% block title %}
{{get_label(this.description())}}
{% endblock %}
{% block content %}
<div class="row" >
  <div class="col-md-8">
    {{ summary_panel(this.description()) }}
  </div>
  <div class="col-md-4">
{% if this.description().value(ns.foaf.depiction) %}
  <img class="img-responsive img-thumbnail" src="{{this.description().value(ns.foaf.depiction)}}" alt="{{get_label(this.description())}}" />
{% endif %}
  </div>
</div>
{% endblock %}
{% endraw %}
```

This a very simplified page that takes out a lot of details from the original page and adds a picture of the person that the node represents.

Restart apache or `python manage.py runserver` and reload the page. You will now see the new template being used.

Templates are written in the [Jinja2 templating language](http://jinja.pocoo.org/docs/latest/templates/).


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

## Adding Jinja Filters to Views

To add some more complex logic to the Jinja2 templating system, we can make use of custom Jinja filters.
Start by adding a `filters.py` to your project source directory (usually located at `/apps/my_knowledge_graph/my_knowledge_graph/`) with the following lines:

```python
def foo(s):
    return s[::-1].upper()
```

This is a simple filter that will reverse and capitalize the string passed to it. Filters need to return the result so that next filter can utilize the result.

Next, add the following line to your `__init__.py`, located in the same folder:

```python
from . import filters
```

Now, modify your `config.py` (usually located at `/apps/my_knowledge_graph/`) to add the following import statement:

```python
from my_knowledge_graph import filters
```

To actually make use of the filter that we've written, we'll need to register it with our configuration file. In your `config.py`, we will need to add an dictionary entry to your configuration object (`Config`), as seen below:

```python
filters = { "foo": filters.foo },
```

This registers the function that we've just written as a filter with the name `foo`. You should now be able to use this filter in your application templates. 

For more information on how to use filters in your templates, take a look at the [Jinja2 Filter Docs](http://jinja.pocoo.org/docs/latest/templates/#filters).
