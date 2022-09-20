# Creating Inference Agents

**Before starting this tutorial, please make sure that you have created a Whyis extension using the instructions in [Installing Whyis](https://tetherless-world.github.io/whyis/install).**

Whyis is more than just a place to store, manage and query knowledge. The Inference Agent framework allows for post-processing of your uploaded knowledge. Inference Agents are capable of knowledge curation, reasoning, interaction, creation, and much more.

This tutorial will walk through the Inference Agent framework, how to create an inference agent, and invocation of an example inference agent.


## How do Inference Agents Work?

The purpose of Whyis Inference Agents is provide additional knowledge or perform some task on your pre-existing knowledge. Each inference agent is itself a SADI service. There is a listener that waits for knowledge graph changes, such as the upload of new knowledge. On knowledge graph change, the listener invokes each agents' SPARQL query.

Upon invocation of an Inference Agent, the input is used to perform some task and provide output to the knowledge base. For example, if knowledge exists for the Inference Agent's pre-defined SPARQL query and something exists in the input class, create additional knowledge based on the content of that input. To learn more about this process, take a look through the source code of `autonomic.py`.

Agents can also be set up to run on a timed schedule, otherwise known as Inference Tasks. A tutorial on this functionality will be included at a later date.


## Creating a Custom Inference Agent

Example inference agents are provided within the Agents directory as `nlp.py`. At the top of the file, you can import files, modules and more. Namespaces can be defined for your inference agents in the file as well. The `nlp.py` file provides sample inference agent declarations.

A Whyis agent must consist of the following functions:
- getInputClass(self): The type of resource your agent will take as input.
- getOutputClass(self): The type that resource becomes when your agent is done with it.
- get_query(self): The SPARQL query used to identify resources relevant to your Agent. By default, it looks for {inputClass}es that are not yet {outputClass}es.
- process(self, input, output): The main function of the inference agent that performs the transformation.
- An activity_class variable, set to a unique namespace in autonomic.whyis
- Any additional helper functions (optional)

### Inference Agent Declaration in Customization Package

All inference agents should be stored in your kgapp. Here is a sample project source directory location: `/apps/my_knowledge_graph/my_knowledge_graph/`. In this directory, there are two pre-generated files: `agent.py` and `__init__.py`.

`__init__.py` contains import statements to all python inference agent files in this directory. For example, if you have one file in the directory called `agent.py`, `__init__.py` should contain: `import agent`. If you create additional python files in that directory, you need to add import statements in `__init__.py`.

`agent.py` contains the framework for sample inference agents. Here is the content from `agent.py`:

```
from whyis import autonomic
from rdflib import *
from slugify import slugify
from whyis import nanopub

sioc_types = Namespace("http://rdfs.org/sioc/types#")
sioc = Namespace("http://rdfs.org/sioc/ns#")
sio = Namespace("http://semanticscience.org/resource/")
dc = Namespace("http://purl.org/dc/terms/")
prov = autonomic.prov
whyis = autonomic.whyis
```

At the top of the file, we import the relevant classes and packages. These import statements should be included in all inference agent files. Below that are some pre-defined namespaces. You may include as many namespaces as needed. We recommend including `prov = autonomic.prov` and `whyis = autonomic.whyis` in other inference agent files as well.

After the import statements and namespace definitions, we can declare our Inference Agents! A example inference agent, HTML2Text is provided below. More information about this inference agent is provided later in this tutorial.

```
class HTML2Text(autonomic.UpdateChangeService):
    activity_class = whyis.TextFromHTML

    def getInputClass(self):
        return sioc.Post

    def getOutputClass(self):
        return URIRef("http://purl.org/dc/dcmitype/Text")

    def get_query(self):
        return '''select ?resource where { ?resource <http://rdfs.org/sioc/ns#content> [].}'''

    def process(self, i, o):
        content = i.value(sioc.content)
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text("\n")
        o.add(URIRef("http://schema.org/text"), Literal(text))
```


### Inclusion of Inference Agent in Configuration File

After a new Agent is implemented, it must be declared in your customization package's `whyis.conf` file. For the purpose of explanation, let's say that I have created a new inference agent. The name of the python file is `myAgents.py`, the inference agent (python class) defined in this file is called `SampleAgent`, and the customization package's name is `my_knowledge_graph`.

To declare a new inference agent in the configuration, the following two tasks must be completed:
1) Import your new inference agent in the config file.
2) Add your Inference Agent to the **inferencers** dictionary (located at the end of the base config class). The key should be the name of your Inference Agent and the value should be the function call.

In the case of my example, I would first need to import my inference agent. The code might look like the following:
`import my_knowledge_graph.myAgents as myAgents`. Secondly, we must include the inference agent in the inferencers dictionary. A sample inferencers dictionary is provided below, with our new inference agent included.

```
    INFERENCERS = {
        "SETLr": autonomic.SETLr(),
        "HTML2Text" : nlp.HTML2Text(),
        "EntityExtractor" : nlp.EntityExtractor(),
        "EntityResolver" : nlp.EntityResolver(),
		#"TF-IDF Calculator" : nlp.TFIDFCalculator(),
        "SKOS Crawler" : autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related]),
        "SampleAgent" : myAgents.SampleAgent()
    },
    INFERENCE_TASKS = [
        dict ( name="SKOS Crawler",
               service=autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related]),
               schedule=dict(hour="1")
              )
    ]
```

## Inference Agent Invocation Example - HTML To Text

For this example, we will be invoking the pre-defined inference agent, HTML2Text. This Agent is defined in the Agents folder as `nlp.py` and utilizes the BeautifulSoup python package. To better understand this inference agent, review the source code shown earlier in this tutorial (also located in your directory: `/apps/whyis/agents/nlp.py`).

The purpose of HTML2Text is to take an HTML sample and convert it to plain text. HTML2Text takes the URI, <http://rdfs.org/sioc/ns#Post>, as input. The query used for this inference is included below.
```
select ?resource where { ?resource <http://rdfs.org/sioc/ns#content> [].}
```

In order to invoke HTML2Text, we must first define the inference agent in the `config.py` file. Open the file and uncomment the line: '"HTML2Text" : nlp.HTML2Text(),'. Confirm that all uncommented inference agents end in a comma, except for the last defined inference agent in the list. If there is an error in your `config.py`, Whyis will use the default config file instead. Your inferencers dictionary should look like the following:

```
    INFERENCERS = {
        "SETLr": autonomic.SETLr(),
        "HTML2Text" : nlp.HTML2Text()
        #"EntityExtractor" : nlp.EntityExtractor(),
        #"EntityResolver" : nlp.EntityResolver(),
		#"TF-IDF Calculator" : nlp.TFIDFCalculator(),
        #"SKOS Crawler" : autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related]),
    },
```

Second, we must upload some knowledge to invoke the HTML2Text Agent. Below is a sample Turtle file. Copy the content and save it to a file in your local directory as 'htmlKnowledge.ttl'.

```
@prefix sioc: <http://rdfs.org/sioc/ns#>.
<http://rdfs.org/sioc/ns#Post> <http://rdfs.org/sioc/ns#content> """<!DOCTYPE html><html><body><h1>Website heading template!</h1><p>There is no place like 127.0.0.1.</p></body></html>""".
```

To load our new knowledge, use the load command:
```
$ whyis load -i <path to input file directory> -f turtle
```

As a result of the knowledge upload, there will be a new triple that contains parsed HTML text.

| subject                      | predicate              | object                                                      |
|------------------------------|------------------------|-------------------------------------------------------------|
| http://rdfs.org/sioc/ns#Post | http://schema.org/text | Website heading template! There is no place like 127.0.0.1. |


## Inference Agents Troubleshooting

If you are having issues with creating an Inference Agent, try the following solutions:
- Check to make sure there are no errors in your inference agent and config code
- Check the validity of your SPARQL query
- Try restarting celeryd as a privileged user: `$ sudo service celeryd restart`
