ARG WHYIS_IMAGE_TAG=latest

FROM maven:3.6-jdk-8 as build-java
WORKDIR /apps/whyis/whyis-java
COPY /whyis-java /apps/whyis/whyis-java
RUN mvn clean compile assembly:single -PwhyisProfile

FROM node:12-alpine as build-bundle
COPY static /static
WORKDIR /static
RUN npm install &&\
	npm run build

FROM tetherlessworld/whyis-server-deps:$WHYIS_IMAGE_TAG
COPY --chown=whyis:whyis / /apps/whyis
RUN puppet apply /apps/whyis/docker/image/whyis-server/install.pp

COPY --from=build-java /apps/whyis/jars /apps/whyis/jars
COPY --from=build-bundle /static/js/whyis_vue_bundle.js /apps/whyis/static/js
COPY --chown=whyis:whyis /docker/image/whyis-server/docker-entrypoint.sh /
WORKDIR /apps/whyis
