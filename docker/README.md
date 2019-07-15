# Whyis and Docker

Whyis is packaged as two sets of Docker images:

1. a *monolithic* image, which includes everything needed to run whyis is a single image
1. *split* images, which separates services into different containers and must be run with docker-compose or another orchestration system

New users should start with the monolithic image.


## Monolithic image

### Use

#### Prerequisites
* Docker

Each run of the container should be considered a fresh slate for your Whyis application to be run on. In other words, /most/ changes done to the container will be erased after each run. 

To start the monolithic image from Dockerhub, run:

    docker run -p 80:80 -it tetherlessworld/whyis

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
    docker-compose build whyis-deps
    docker-compose push whyis-deps
 

## Split images

The monolithic image was split into images for the databases Whyis relies on (_redis_, _blazegraph_) and the Whyis server application (_whyis-server_).

#### Prerequisites 
* Docker
* `docker-compose`

### Use

    cd docker/compose/split
    docker-compose -f db/docker-compose.yml -f app/docker-compose.yml

which starts both the database (`db/`) and server (`app/`) containers.

### Development

Similar to the monolithic image, the _whyis-server_ image is built from multiple parent images, which change less frequently than the code.

    cd docker/compose/split
    docker-compose -f db/docker-compose.yml build
    docker-compose -f db/docker-compose.yml push
    docker-compose -f app/docker-compose.yml build whyis-ubuntu
    docker-compose -f app/docker-compose.yml push whyis-ubuntu
    docker-compose -f app/docker-compose.yml build whyis-server-deps
    docker-compose -f app/docker-compose.yml push whyis-server-deps

The `db/docker-compose.yml` can be used to start the databases without the server, so that the server can e.g., be run locally:

    cd docker-compose/split
    docker-compose -f db/docker-compose.yml


## Other notes

### Whyis image tags

By default the `docker-compose.yml` use `latest` tags for the whyis images. This can be overriden by specifying the environment variable `WHYIS_IMAGE_TAG`.