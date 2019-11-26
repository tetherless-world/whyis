
# Using the Whyis command-line interface

To peform the following administrative tasks, if you're not running Whyis directly, you will need to connect to the device you are running it on.

If you're using a virtual machine with Vagrant:
```
vagrant ssh
```

If you're using a Docker container:
```
docker exec -it <container name> bash
```

Once you are in the server, you need to change to the **whyis** user, go to the whyis app directory, and activate the python virtual environment:

```
sudo su - whyis
cd /apps/whyis
source venv/bin/activate
```

To see a brief description of the Whyis subcommands:

```
python manage.py -?
```

To see more in-depth information about a subcommand and its options:

```
python manage.py <subcommand> -?
```

### Configure Whyis
**If you are using an existing Whyis knowledge graph, this step is not needed.  Instead, go to the install instructions for the graph you wish to install.**

Whyis is built on the Flask web framework, and most of the Flask authentication options are available to configure in Whyis.
A configuration script will walk you through the configuration process and make a project directory for you. 
Change the default values as needed. The SECRET_KEY and SECURITY_PASSWORD_SALT are randomly generated at runtime, so you shouldn't need to change those.

Run the following command:
```
python manage.py configure
```

This will run the configuration script, which will allow you to enter the desired configuration options from stdin, which will look like this:
```
project_name [My Knowledge Graph]: 
project_short_description [An example knowledge graph configuration.]: 
project_slug [my_knowledge_graph]: 
location [/apps/my_knowledge_graph]: 
author [J. Doe]: 
email [j.doe@example.com]: 
linked_data_prefix [http://localhost]: 
version [0.1]: 
packages []: 
SECRET_KEY [J00F5f80rGSbvpUo9oBFAtksmrd7ef8u]: 
SECURITY_PASSWORD_SALT [JDyCyPu0KEu/fdJr4CbG65VhCtGugwCu]: 
$ 
```

This will create a project skeleton for you at `location` (here, `/apps/my_knowledge_graph`). The files are:

* **config.py** - Main configuration file for Whyis.
* **vocab.ttl** - Vocabulary file for configuring custom Whyis views.
* **templates/** - Directory for storing Whyis view templates.
* **my_knowledge_graph/** - Project source directory. Put any python code in here.
  * **agent.py** - An empty inference agent module.
* **static/** - Files that are served up at `{linked_data_prefix}/cdn/` as static files.
  * **css/** - Project-specific CSS files.
    * **my_knowledge_graph.css** - Default empty project-specific CSS file.
  * **html/** - Project-specific static HTML files, like for Angular.js templates.
  * **js/** - Project-specific javascript files.
    * **my_knowledge_graph.js** - Default empty project-specific javascript file.
* **setup.py** - File for installation using pip.

Change directories into the project dir and install it into your virtualenv as follows. Be sure your virtualenv is activated first, by running `source venv/bin/activate` if you have not already done so.

```
cd /apps/my_knowledge_graph
pip install -e .
```

Restart apache and celeryd as a privileged user (not whyis) to have the configuration take effect:

```
sudo service apache2 restart
sudo service celeryd restart
```

### Add a User

Registration is available on the website for users, but it's easy to add a user to the knowledge graph from the command line. 
Perform this task as the `whyis` user from the `/apps/whyis` directory.
Use `--roles=admin` to make the user an administrator.

```
python manage.py createuser -e <email> -p <password (can change later)> -f <first name> -l <last name> -u <user handle> --roles=admin
```

### Modify a User

You can change the roles a user has from the command line as well, but you'll need their user handle. 
For instance, you can add a user to a role like this:

```
python manage.py updateuser -u <user handle> --add_roles=admin
```

You can remove them from a role like this:

```
python manage.py updateuser -u <user handle> --remove_roles=admin
```

Changing a password is also simple:

```
python manage.py updateuser -u <user handle> -p <new password>
```

### Run in development mode

Whyis can be run on a different port to enable debugging. You will see output from the log in the console and will be able to examine stack traces inside the browser.

```
python manage.py runserver -h 0.0.0.0
```

### Loading Knowledge

Knowledge can be added to Whyis using a command as well. This can be used to inject states that trigger larger-scale knowledge ingestion using [SETLr](https://github.com/tetherless-world/setlr/wiki/SETLr-Tutorial), or can simply add manually curated knowledge. 
If the RDF format supports named graphs, and the graphs are nanopublications, the nanopublications will be added as-is.
If there are no explicit nanopublications, or if the RDF format is triples-only, each graph (including the default one), is treated as a separate nanopublication assertion.
The PublicationInfo will contain some minimal provenance about the load, and each assertion will be the graphs contained in the file.

```
python manage.py load -i <input file> -f <turtle|trig|json-ld|xml|nquads|nt|rdfa>
```

### Retire a nanopublication

To remove a nanopublication from the Whyis knowledge graph, use the following command:

```
python manage.py retire -n <nanopub URI>
```

This will also retire anything that *prov:wasDerivedFrom* the retired nanopublication, which may happen recursively.

Note that retired nanopublications are still accessible as linked data from a file archive that stores all nanopublications that have been published in the knowledge graph.

### Run tests on Whyis

To run the test suite of Whyis (unit tests, integration tests, API tests):
```
python manage.py test
```

This will run every test that is specified in the source code in a `.py` file whose name begins with `test_`.

To specify an alternate pattern for filenames, use the `--test` option. This should be specified as a filename without an extension. For example, to run the test suite specified in `tests/integration/test_login.py`:

```
python manage.py test --test test_login
```

Test files can also be specified using glob patterns. For example, to run the group of tests in `tests/api/view` whose filenames all end in `_json_view.py`, the command is:
```
python manage.py test --test test_*_json_view
```

### Run an inference agent

To run an inference agent on the Whyis knowledge graph:

```
python manage.py testagent -a <agent>
```

where `agent` is specified as a dotted Python path. Currently-supported agents include `agents.nlp.EntityExtractor`, `agents.nlp.EntityResolver`,  `agents.nlp.IDFCalculator`, and `agents.nlp.HTML2Text`.



### Remove the currently-installed Whyis application

This command will remove the Whyis application that is currently installed, if there is one. Currently, having multiple apps installed into the same Whyis instance simultaneously is undefined behavior, so it is important to run this command before creating a new app.

```
python manage.py uninstallapp
```

### View a list of valid routes in the API

```
python manage.py listroutes
```

### Open a Python shell inside the application context

```
python manage.py shell
```

## [Next: Creating Whyis Views](views)