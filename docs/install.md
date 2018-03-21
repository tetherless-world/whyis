# Install Whyis

The Whyis installer is layered, which allows for maximum flexibility. Each layer is runnable by itself, resulting in a functional Whyis.

- **Layer 3: Vagrant** [Vagrant](https://www.vagrantup.com/) is a tool for automatically creating virtual machines either on developer computers or in virtual environments. The `Vagrantfile` that is included in Whyis is set up to use [VirtualBox](https://www.virtualbox.org/) to create an Ubuntu 14.04 virtual machine automatically. This script creates a virtual machine and then calls the Layer 2 shell script.
- **Layer 2: Shell Script** If you already have a virtual machine provisioned, or want to directly install Whyis onto an Ubuntu server directly, you can use the Layer 2 shell script. It is a simple script, `install.sh`, that installs Puppet and the needed modules, and then runs the Layer 1 Puppet script.
- **Layer 1: Puppet** [Puppet](https://puppet.com/) is a flexible devops tool that automates the configuration and provisioning of servers, both virtual and physical. The script `manifests/install.pp` can be used directly by current Puppet users that want to incorporate Whyis deployment into their existing Puppet infrastructure.

Choose a layer to install. Most developers working with Whyis for the first time will want to install into a virtual machine, and should choose Layer 1.
Users who are willing to configure a machine directly for use by Whyis should choose Layer 2.
Whyis installations are currently supported on Ubuntu >= 14.04. 


## Layer 2: Install into an Ubuntu system

This is useful for deploying production knowledge graphs, or for developers who already have a machine (virtual or otherwise) that is ready to run Whyis.

```
bash < <(curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/release/install.sh)
```

To install using the development branch of Whyis, use the master install script:

```
bash < <(curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/master/install.sh)
```



## Layer 3: Install into a vagrant virtual machine 

This is useful for developers who want to isolate their development environment so that builds are repeatable, and for developers of multiple knowledge graphs.

You will need to install vagrant and virtualbox.

```
mkdir whyis-vm && cd whyis-vm
curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/release/Vagrantfile > Vagrantfile
curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/release/install.sh > install.sh
vagrant up
```

To install using the development branch of Whyis, use the master install script:

```
mkdir whyis-vm && cd whyis-vm
curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/master/Vagrantfile > Vagrantfile
curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/master/install.sh > install.sh
vagrant up
```

If you are setting up more than one whyis vm (maybe for multiple projects), be sure to change the IP address in the Vagrantfile after you downloaded but before running `vagrant up`:

```
  config.vm.network "private_network", ip: "192.168.33.36"
```

# Administrative Tasks

To peform the following administrative tasks, you need to connect to the VM (if you're not running directly):

```
vagrant ssh
```

Once you are in the server, you need to change to the whyis user, go to the whyis app directory, and activate the python virtual environment:

```
sudo su - whyis
cd /apps/whyis
source venv/bin/activate
```

### Configure Whyis

Whyis is built on the Flask web framework, and most of the Flask authentication options are available to configure in Whyis.
A configuration script will walk you through the configuration process and make a project directory for you. 
Change the default values as needed. The SECRET_KEY and SECURITY_PASSWORD_SALT are randomly generated at runtime, so you shouldn't need to change those.

```
$ python manage.py configure
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

Change directories into the project dir and install it into your virtualenv. Be sure your virtualenv is activated first:

```
$ cd /apps/my_knowledge_graph
$ pip install -e .
```

Restart apache and celeryd as a privileged user (not whyis) to have the configuration take effect:

```
$ sudo service apache2 restart
$ sudo service celeryd restart
```

### Add a User

Registration is available on the website for users, but it's easy to add a user to the knowledge graph from the command line. 
Use `--roles=admin` to make the user an administrator.

```
$ python manage.py createuser -e <email> -p <password (can change later)> -f <First Name> -l <Last Name -u <user handle> --roles=admin
```

### Modify a User

You can change the roles a user has from the command line as well, but you'll need their user handle. 
For instance, you can add a user to a role like this:

```
$ python manage.py updateuser -u <user handle> --add_roles=admin
```

You can remove them from a role like this:

```
$ python manage.py updateuser -u <user handle> --remove_roles=admin
```

Changing a password is also simple:

```
$ python manage.py updateuser -u <user handle> -p <new password>
```

### Run in development mode

Whyis can be run on a different port to enable debugging. You will see output from the log in the console and will be able to examine stack traces inside the browser.

```
$ python manage.py runserver -h 0.0.0.0
```

### Loading Knowledge

Knowledge can be added to Whyis using a command as well. This can be used to inject states that trigger larger-scale knowledge ingestion using [SETLr](https://github.com/tetherless-world/setlr/wiki/SETLr-Tutorial), or can simply add manually curated knowledge. 
If the RDF format supports named graphs, and the graphs are nanopublications, the nanopublications will be added as-is.
If there are no explicit nanopublications, or if the RDF format is triples-only, each graph (including the default one), is treated as a separate nanopublication assertion.
The PublicationInfo will contain some minimal provenance about the load, and each assertion will be the graphs contained in the file.

```
$ python manage.py load -i <input file> -f <turtle|trig|json-ld|xml|nquads|nt|rdfa>
```

## [Next: Creating Whyis Views](views)
