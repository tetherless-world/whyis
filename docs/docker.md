# Using Whyis with Docker

Whyis can be used with Docker to instantiate a fully functional Whyis container. For an introduction to Docker concepts and terminology, see:
- [A Beginner-Friendly Introduction to Containers, VMs and Docker by freeCodeCamp](https://medium.freecodecamp.org/a-beginner-friendly-introduction-to-containers-vms-and-docker-79a9e3e119b)
- [Docker overview by Docker](https://docs.docker.com/engine/docker-overview/)

Whyis is packaged as two sets of Docker images:

1. a *monolithic* image, which runs Whyis as a single image
2. *split* images, which must be run with docker-compose or another orchestration system

New users should start with the monolithic image.

## Table of Contents
1. [Prerequisites](#prequisites)
2. [Monolithic Image](#monolithic-image)
3. [Split Images](#split-images)
4. [Docker Data Persistence](#docker-data-persistence)
5. [Whyis App Development](#whyis-app-development)
6. [Whyis Development](#whyis-development)
7. [Notes and Troubleshooting](#notes-and-troubleshooting)

## Prerequisites
### Docker
It is recommended that Docker is installed using instructions directly from the Docker website, as using the default package repositiories may contain older versions of Docker that are no longer compatible with Whyis.

You can find the instructions to install Docker [here](https://docs.docker.com/install/) for most common platforms.

### Docker-Compose
[Docker compose](https://docs.docker.com/compose/) is needed to run the *split* Whyis images, which separate the external services of Whyis (*redis*, *blazegraph*) and the Whyis server application (*whyis-server*) into different containers.

You can find the installation instructions [here](https://docs.docker.com/compose/install/).

## Monolithic Image
To spin up an instance of the monolithic Whyis image, run:
```shell
$ docker run -p 127.0.0.1:80:80 -it tetherlessworld/whyis bash
```
This will automatically download the `latest` tagged version of the `whyis` image from the [Docker Hub](https://hub.docker.com/r/tetherlessworld/whyis/).

You should now have access to a prompt where you can input shell commands on the container and be able to access a log in page at `localhost:80` on your machine. You can stop the container by exiting the shell. 

You can also run Whyis in the background will the following command:
```shell
$ docker run -d -p 127.0.0.1:80:80 tetherlessworld/whyis
```
To stop the container while Whyis is running in the background, see [here](#terminating-whyis).

Note that leaving out `-d` will still allow Whyis to run, but you will be unable to stop the container from the terminal that you used. To terminate Whyis, you will need to run commands from a new terminal.

### Updating the Image
To just pull the image or update the image to the latest version, run:

```shell
$ docker pull tetherlessworld/whyis
```

### Next Steps
See [Whyis App Development](#whyis-app-development) to start developing applications with Whyis.

The section [Notes and Troubleshooting](#notes-and-troubleshooting) may also be relevant for the following:
* [Opening Another Shell](#opening-another-shell)

## Split Images

### Mac OS X
In the provided `docker-compose.yml` files, Whyis will mount the following directories on the host in the `docker-compose.yml` files.
* `/data` for persistent storage

On Mac OS X you must allow Docker to mount these directories by going into Docker's Preferences -> File Sharing and adding their absolute paths. For example:
* Add `/data` assuming you have a `/data` directory on your host

## Docker Data Persistence

## Whyis App Development

## Whyis Development

## Notes and Troubleshooting
### Whyis Container Name
To get the name of the container that is currently running (which is needed for certain operations), run:
```shell
$ docker ps
```

This will output a list of currently running containers. You should pay attention to the following headers:
```
CONTAINER ID
<container_id>

IMAGE
tetherlessworld/whyis

NAMES
<container_name>
```

### Opening Another Shell
If you need to open another terminal on the container, you will need to open a new terminal and run:
```
$ docker exec -it <container_name> bash
```
This works on Linux systems and in the Windows command prompt. Some third-party shells on Windows (such as git bash), require instead using

```shell
$ winpty docker exec -it <container_name> bash
```
To get the container name, see [here](#whyis-container-name).

### Terminating Whyis
If you need to terminate Whyis while it is in the background, run:
```
$ docker kill <container_name>
```
To get the container name, see [here](#whyis-container-name).


