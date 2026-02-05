# Install Whyis

Whyis is available as both a python package and a docker image. When deploying to a server, the generated knowlege graph application (kgapp) can easily be installed in recent Ubuntu versions. Since the kgapp is source-based, it can be managed using source control systems like Git or others.

## As a Python Package

Installing and running Whyis 2.0 is very straightforward. It is available for installation on either Ubuntu 18 or later, MacOS, or the Windows Subsystem for Linux.

Requirements:

* Python 3.7 or later with venv and pip
* Open or Oracle JDK 13 or later

We will refer to your most recent python as `python`, although most systems only use the `python` alias for python 2.x. Please use the command for your version of python.

**NOTE**: It is strongly recommended to install Whyis into a virtual python environment using venv, virtualenv, Conda, or similar. The following will generate and activate a venv for your current python. Please refer to your virtual environment documentation to generate it if you are not using venv.

```
python -m venv venv
source venv/bin/activate
```

Finally, install the whyis package using pip:

```
pip install whyis
```

To generate your first kgapp, make a directory for it, change to that directory, and start whyis:

```
mkdir kgapp
cd kgapp
whyis
```

This will generate all the needed files to build a knowledge graph, and start the SPARQL database, inference engine system, and the web server. Visit the web page at http://localhost:5000 to start working with Whyis.

## As a Docker Image

Running whyis in docker is also very simple. With docker installed, To generate your first knowledge graph, make a directory for your kgapp, change to it, and start the whyis container:

```
mkdir kgapp
cd kgapp
docker pull tetherlessworld/whyis
docker run -v $PWD:$PWD -w $PWD -p 5000:5000 --name mykgapp tetherlessworld/whyis:latest
```

Note that `$PWD` binds the current directory as the working dir in the container. You can adjust this as needed. Once the container is running, you can visit the knowledge graph at http://localhost:5000.

Whyis commands can be run from inside the container using `docker exec`.

## Using docker-compose in a KGApp

When you initialize a Whyis KGApp (the cookiecutter project slug directory), it includes two compose files for containerized deployments:

* `docker-compose.yml` for production-style runs (Gunicorn + Redis, Celery, and Fuseki).
* `docker-compose-dev.yml` for build/development runs (builds from `Dockerfile.dev`); in the template this file is named `docker-compose-dev.yaml`.

For a production-style run, start the stack from your KGApp directory:

```
docker compose up -d
```

For a build/development run, build and start the dev container (use the `.yaml` filename if you have not renamed it):

```
docker compose -f docker-compose-dev.yml up --build
```

This will expose the application on http://localhost:5000. Use `docker compose down` to stop the stack.

## Deploying a kgapp to a Server

If you need to deploy your knowledge graph to a server, copy your kgapp dir to the server, and run the following scripts from within the kgapp dir:

```
./script/bootstrap
./script/setup
```
