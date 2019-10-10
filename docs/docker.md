# Whyis and Docker

Whyis can be used with Docker and Docker Compose to instantiate a fully functional Whyis Docker instance that can be run as many times as required. For an introduction to Docker concepts and terminology, see:
- [A Beginner-Friendly Introduction to Containers, VMs and Docker by freeCodeCamp](https://medium.freecodecamp.org/a-beginner-friendly-introduction-to-containers-vms-and-docker-79a9e3e119b)
- [Docker overview by Docker](https://docs.docker.com/engine/docker-overview/)

Whyis is packaged as two sets of Docker images:

1. a *monolithic* image, which includes everything needed to run whyis is a single image

New users should start with the monolithic image.

2. *split* images, which separates services into different containers and must be run with docker-compose or another orchestration system

For an introduction to Docker Compose, see:
- [Docker Compose overview](https://docs.docker.com/compose/)

## Common concerns

All of the whyis images mount directories from the host in the `docker-compose.yml` files:

* `/data` for persistent storage, mounted as `/data` in the container

On Mac OS X you must allow Docker to mount these directories by going into Docker's Preferences -> File Sharing and adding their absolute paths. For example:

* Add `/data` assuming you have a `/data` directory on your host

## Monolithic image

### Installation and Use

#### Prerequisites
* Docker

#### Instructions
Each run of the container should be considered a fresh slate for your Whyis application to be run on. In other words, *most* changes done to the container will be erased after each run. 

To start the monolithic image from Dockerhub, run:

    docker run -p 80:80 -it tetherlessworld/whyis

This will automatically download the `latest` version of the `whyis` image from the [Docker Hub](https://hub.docker.com/r/tetherlessworld/whyis/). 

Once the docker image is running, you will need to open a new terminal and open a shell into the docker container.

To find the container ID, run:

```shell
docker ps
```

To open a shell inside the docker container

```shell
docker exec -it <container_id> bash
```

This works on Linux systems and in the Windows command prompt. Some third-party shells on Windows (such as git bash), may require instead using

```shell
winpty docker exec -it <container_id> bash
```


To just pull the image or update the image to the latest version, run:

```shell
docker pull tetherlessworld/whyis
```

### Development

#### Prerequisites

* `docker-compose`

#### Building and pushing

The _whyis_ monolithic image is built in two parts:

1. a _whyis-deps_ image, which contains the environment and dependencies for whyis
2. the _whyis_ image, which is the user-facing image and contains the custom code for whyis; it depends (FROM) on whyis-deps

We assume that _whyis-deps_ changes infrequently, whereas whyis changes frequently.
The Continuous Integration server only builds and pushes whyis, retrieving whyis-deps from Dockerhub in the process.
When whyis-deps changes, you will need to push it to Dockerhub manually.

Assuming you have logged in with `docker login`, you can use docker/compose/dev to build whyis-deps and push it to Dockerhub:

    cd docker/compose/monolithic
    ./build-deps.sh
    ./push-deps.sh 

Note: You will have to be be a member of the [Tetherless World](https://hub.docker.com/u/tetherlessworld/) organization to be able to run these steps.

## Split images

The monolithic image was split into images for the databases Whyis relies on (_redis_, _blazegraph_) and the Whyis server application (_whyis-server_).

#### Prerequisites 
* Docker
* `docker-compose`
* A data folder alongside your `/apps` folder is in with permissions 777
  * See other notes

### Use

    cd docker/compose/split
    docker-compose -f db/docker-compose.yml -f app/docker-compose.yml

which starts both the database (`db/`) and server (`app/`) containers.

### Development

Similar to the monolithic image, the _whyis-server_ image is built from multiple parent images, which change less frequently than the code.

    cd docker/compose/split
    ./build-deps.sh
    ./push-deps.sh

The `db/docker-compose.yml` can be used to start the databases without the server, so that (for example) the server can be run locally:

    cd docker-compose/split
    docker-compose -f db/docker-compose.yml

Further, `docker/compose/split/app-dev` references a version of `whyis-server` that mounts `/apps` from the parent directory of the current whyis checkout, for local development.

## Other notes

### Data directory

By default, the split `docker-compose.yml` will mount a directory named `data` in the same directory as your `/apps` folder on the host machine. Due to how Docker allocates volumes, this folder will have the wrong permissions and cause Blazegraph to fail on the first setup. To avoid this, run the following instructions before running `docker-compose`:

	cd /
	mkdir data
	chmod ugo+rwx data
	
You should then be able to start and stop the containers without further permission issues.

### Whyis image tags

By default the `docker-compose.yml` use `latest` tags for the whyis images. This can be overriden by specifying the environment variable `WHYIS_IMAGE_TAG`.
