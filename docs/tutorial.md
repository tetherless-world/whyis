# Whyis Tutorial

This page contains tutorials that a new user can follow to get started with using Whyis.

## Whyis docker tutorial

If you don't have docker installed, see the docker Whyis prerequisites: http://tetherless-world.github.io/whyis/docker .

### Useful docker commands
A few useful docker commands are listed below.

To run the docker instance (and set up a shared folder):
```shell
$ docker run -p 80:80 -v {absolute_url}/docker-data:/data -it tetherlessworld/whyis
```
To find the container ID:
```shell
$ docker ps
```
To bash into the container:
```shell
$ docker exec -it <container_id> bash
```
To kill a container:
```shell
$ docker kill <container_id>
```
To update to latest whyis version:
```shell
$ docker pull tetherlessworld/whyis
```
Once in the docker instance, to use multiple terminals, install screen:
```shell
root$ apt install screen 
```
### Configuring Whyis
Change to the whyis user:
```shell
root$ su - whyis
```
Change to the whyis directory:
```shell
whyis$ cd whyis
```

To see a list of manage.py commands:
```shell
whyis$ python manage.py
```

To configure to knowledge graph (creating a new knowledge graph instance):
```shell
whyis$ python manage.py configure
```
-- Set project name

-- Give the project a description

-- Give the project a slug (Used for generating files)

-- Set the location of the KG

-- Set your name and email

-- Set the linked data prefix (in general if you are publishing, you do not set to localhost. In this case, when working on your own computer, it is okay. But when deploying, you want to put the server address.)

-- Version, packages, secret key, and salt can be left at default values

Once the knowledge graph instance is created, go to that folder:
```shell
whyis$ cd ../whyis_demo/
```
And install the packages using pip3
```shell
whyis$ pip3 install -e .
```
Note that you should have one KG instance on a machine at a time. If you want to create another KG instance, create another docker instance for it)

Install your favorite text editor (emacs, nano, or vim) as root:
```shell
root$ apt update
root$ apt install vim
```
To open the config file (as the whyis user)
```shell
root$ su - whyis
whyis$ cd whyis_demo
whyis$ emacs config.py
```
You can update contents of the config, such as the project description, if you wish.
### Loading knowledge
Next, we want to load an ontology into the knowledge graph

For this tutorial, we will use a dataset ontology:
```shell
whyis$ python3 manage.py load -i http://orion.tw.rpi.edu/~jimmccusker/dataset.ttl -f turtle
```
Set annonymous read to true:
```shell
whyis$ cd ../whyis_demo
```
```shell
whyis$ emacs config.py
```
Under root_path = '/apps/whyis', add:
```
DEFAULT_ANNONYMOUS_READ = True,
```
Restart the apache2 server as root:
```shell
root$ service apache2 restart
```
You should now see a dataset page at localhost/about?uri=http%3A%2F%2Fschema.org%2FDataset

You can check out dbpedia pages like localhost/dbpedia/JamesHendler or localhost/dbpedia/IBM

From the Dataset page, you can use a template to create a new dataset reference by clicking the Add button (+) at the bottom of the page

Next we want to load some experiment data
```shell
whyis$python3 manage.py load -i https://github.com/tetherless-world/whyis-demo/raw/master/data/ae_experiments.ttl -f turtle
```
You should see that the data loaded into whyis

You can click the list view to see descriptions of the content that was loaded
### Next steps
Visit http://tetherless-world.github.io/whyis/inference to learn about inference agents
