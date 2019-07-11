FROM maven:3.6-jdk-8 as build-java
WORKDIR /apps/whyis/whyis-java
COPY /whyis-java /apps/whyis/whyis-java
RUN mvn clean compile assembly:single -PwhyisProfile

FROM tetherlessworld/whyis-server-deps

COPY --chown=whyis:whyis / /apps/whyis
RUN puppet apply /apps/whyis/docker/image/whyis-server/install.pp

COPY --from=build-java /apps/whyis/jars /apps/whyis/jars
COPY /docker/image/whyis-server/docker-entrypoint.sh /
COPY /docker/image/whyis-server/celery-entrypoint.sh /
WORKDIR /apps/whyis
